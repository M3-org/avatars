#!/usr/bin/env python3
"""
Bust Thumbnail Generator (OpenRouter → PNG with transparent background)

Adds retries with exponential backoff and jitter.
"""

import os, sys, io, json, base64, argparse, time, random
from pathlib import Path
from typing import Optional, List, Tuple
import requests
from PIL import Image, ImageFilter
import statistics

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODEL = "google/gemini-2.5-flash-image-preview"

# ---------- Prompt ----------
DEFAULT_PROMPT = (
    "Game character portrait, torso up with arms visible, 3/4 view, "
    "neutral/confident/thinking pose, professional lighting, clean game asset style, "
    "solid flat unlit green background hex #00b140, subject centered, no text"
)
RETRY_NUDGE = "Return only the PNG image as a data URL (no text)."

# ---------- Helpers ----------
def to_data_url(p: Path) -> str:
    with open(p, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")
    return f"data:image/png;base64,{b64}"

def data_url_to_bytes(data_url: str) -> bytes:
    if not data_url.startswith("data:"):
        raise ValueError("Unexpected image format: not a data URL")
    header, b64data = data_url.split(",", 1)
    return base64.b64decode(b64data)

def guess_guide_image(dir_path: Path) -> Optional[Path]:
    model_files = sorted(list(dir_path.glob("*.vrm")) + list(dir_path.glob("*.glb")))
    if model_files:
        stem = model_files[0].stem
        cand = dir_path / f"{stem}.png"
        if cand.exists(): return cand
    shots = sorted(dir_path.glob("screenshot*.png"))
    if shots: return shots[0]
    pngs = sorted(dir_path.glob("*.png"))
    if pngs: return pngs[0]
    return None

# ---------- OpenRouter ----------
def openrouter_generate(prompt: str, guide_image: Optional[Path], api_key: str) -> bytes:
    headers = {"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"}
    content_parts = [{"type": "text", "text": prompt}]
    if guide_image:
        content_parts.append({"type": "image_url", "image_url": {"url": to_data_url(guide_image)}})

    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": content_parts}],
        "modalities": ["image", "text"],
    }
    r = requests.post(OPENROUTER_URL, headers=headers, data=json.dumps(payload), timeout=180)
    r.raise_for_status()
    j = r.json()

    # Your original expected shape:
    try:
        img_url = j["choices"][0]["message"]["images"][0]["image_url"]["url"]
    except Exception as e:
        raise RuntimeError(f"No images in response: {j}") from e

    if img_url.startswith("data:"):
        return data_url_to_bytes(img_url)

    img = requests.get(img_url, timeout=180)
    img.raise_for_status()
    return img.content

# ---------- Robust chroma key ----------
def hex_to_rgb(hexstr: str) -> Tuple[int,int,int]:
    h = hexstr.lstrip("#")
    return tuple(int(h[i:i+2], 16) for i in (0,2,4))

def rgb_to_hsv(r,g,b):
    return Image.new("RGB", (1,1), (r,g,b)).convert("HSV").getpixel((0,0))

def circular_hue_distance(h1, h2):
    d = abs(h1 - h2)
    return min(d, 255 - d)

def sample_border_hsv(im: Image.Image, sample_px: int = 4) -> Tuple[int,int,int]:
    w, h = im.size
    px = im.convert("RGB").load()
    samples = []
    for x in range(w):
        for y in range(sample_px):
            samples.append(px[x, y]); samples.append(px[x, h-1-y])
    for y in range(h):
        for x in range(sample_px):
            samples.append(px[x, y]); samples.append(px[w-1-x, y])
    hs, ss, vs = [], [], []
    for (r,g,b) in samples:
        H,S,V = rgb_to_hsv(r,g,b)
        hs.append(H); ss.append(S); vs.append(V)
    return (int(statistics.median(hs)), int(statistics.median(ss)), int(statistics.median(vs)))

def remove_background_auto(image_bytes: bytes,
                           fallback_hex: str = "#00b140",
                           hue_fuzz: int = 18,
                           sat_min: float = 0.15,
                           val_min: float = 0.15) -> Image.Image:
    im = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
    hsv = im.convert("HSV")
    H,S,V,A = [ch for ch in hsv.split()] + [im.split()[3]]

    try:
        bgH, bgS, bgV = sample_border_hsv(im)
    except Exception:
        bgH, bgS, bgV = rgb_to_hsv(*hex_to_rgb(fallback_hex))

    Hpx = H.load(); Spx = S.load(); Vpx = V.load()
    w,h = im.size
    mask = Image.new("L", (w,h), 0); Mpx = mask.load()
    sat_thr = int(sat_min * 255); val_thr = int(val_min * 255)

    for y in range(h):
        for x in range(w):
            if Spx[x,y] >= sat_thr and Vpx[x,y] >= val_thr:
                if circular_hue_distance(Hpx[x,y], bgH) <= hue_fuzz:
                    Mpx[x,y] = 255  # background

    from PIL import ImageChops, ImageFilter as _IF
    mask = mask.filter(_IF.GaussianBlur(1.2))
    out = im.copy(); outA = out.split()[3]
    inv = Image.eval(mask, lambda p: 255 - p)
    combined = ImageChops.multiply(outA, inv)
    out.putalpha(combined)
    return out

def resize_square_rgba(im: Image.Image, size: int = 400) -> Image.Image:
    im = im.convert("RGBA")
    tmp = im.copy()
    tmp.thumbnail((size, size), Image.Resampling.LANCZOS)
    canvas = Image.new("RGBA", (size, size), (0,0,0,0))
    x = (size - tmp.width)//2; y = (size - tmp.height)//2
    canvas.paste(tmp, (x,y), tmp)
    return canvas

# ---------- Retry wrapper ----------
def call_with_retry(prompt: str,
                    guide_image: Optional[Path],
                    api_key: str,
                    retries: int,
                    backoff: float) -> bytes:
    """
    Retries ONLY when we fail to extract an image (RuntimeError from openrouter_generate).
    On retries:
      - attempt 2+: append RETRY_NUDGE to the prompt
      - attempt 3+: drop the guide to reduce token/route ambiguity
    """
    attempt = 0
    last_err = None
    cur_prompt = prompt
    cur_guide = guide_image

    while attempt <= retries:
        try:
            if attempt == 1 and RETRY_NUDGE not in cur_prompt:
                cur_prompt = f"{prompt}\n\n{RETRY_NUDGE}"
            if attempt >= 2:
                cur_guide = None

            return openrouter_generate(cur_prompt, cur_guide, api_key)

        except RuntimeError as e:
            last_err = e
            if attempt == retries:
                break
            delay = backoff * (2 ** attempt) + random.uniform(0, 0.333 * backoff)
            print(f"[retry] No image; attempt {attempt+1}/{retries} failed. Sleeping {delay:.2f}s…", file=sys.stderr)
            time.sleep(delay)
            attempt += 1

        except requests.RequestException as e:
            # Network/HTTP errors: retry as well
            last_err = e
            if attempt == retries:
                break
            delay = backoff * (2 ** attempt) + random.uniform(0, 0.333 * backoff)
            print(f"[retry] HTTP error; attempt {attempt+1}/{retries} failed. Sleeping {delay:.2f}s…", file=sys.stderr)
            time.sleep(delay)
            attempt += 1

    raise last_err if last_err else RuntimeError("Unknown generation failure")

# ---------- Pipeline ----------
def process_dir(dir_path: Path, api_key: str, prompt: str,
                size: int, hue_fuzz: int, sat_min: float, val_min: float,
                retries: int, retry_backoff: float) -> None:
    if not dir_path.is_dir():
        print(f"[skip] Not a directory: {dir_path}", file=sys.stderr)
        return

    out_path = dir_path / f"thumb-bust_{dir_path.name}.png"
    if out_path.exists():
        print(f"[skip] Exists: {out_path}")
        return

    guide = guess_guide_image(dir_path)
    print(f"[info] Guide: {guide if guide else 'none'}")
    print(f"[gen] {dir_path.name} → {out_path.name}")

    raw_png = call_with_retry(prompt, guide, api_key, retries=retries, backoff=retry_backoff)

    cutout = remove_background_auto(
        raw_png, fallback_hex="#00b140",
        hue_fuzz=hue_fuzz, sat_min=sat_min, val_min=val_min
    )

    final_img = resize_square_rgba(cutout, size=size)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final_img.save(out_path, format="PNG", optimize=True)
    print(f"[ok] Wrote {out_path}")

def main():
    ap = argparse.ArgumentParser(description="Generate bust thumbnails with transparent background.")
    ap.add_argument("--list", required=True, help="Text file: one avatar directory per line.")
    ap.add_argument("--root", default=".", help="Root folder of avatar directories.")
    ap.add_argument("--prompt-file", help="Optional file to override the default prompt.")
    ap.add_argument("--size", type=int, default=400, help="Output square size (default 400).")
    ap.add_argument("--hue-fuzz", type=int, default=18, help="Hue tolerance around bg hue (0-127).")
    ap.add_argument("--sat-min", type=float, default=0.15, help="Min saturation to consider bg [0..1].")
    ap.add_argument("--val-min", type=float, default=0.15, help="Min value/brightness for bg [0..1].")
    ap.add_argument("--retries", type=int, default=3, help="Retries when no image/HTTP error (default 3).")
    ap.add_argument("--retry-backoff", type=float, default=2.0, help="Base seconds for exponential backoff (default 2.0).")
    args = ap.parse_args()

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    root = Path(args.root).resolve()
    list_file = Path(args.list)
    if not list_file.exists():
        print(f"ERROR: List file not found: {list_file}", file=sys.stderr)
        sys.exit(1)

    prompt = DEFAULT_PROMPT
    if args.prompt_file:
        txt = Path(args.prompt_file).read_text().strip()
        if txt:
            prompt = txt

    dirs = [ln.strip() for ln in list_file.read_text().splitlines()
            if ln.strip() and not ln.startswith("#")]
    if not dirs:
        print("Nothing to do; list file is empty.", file=sys.stderr)
        sys.exit(0)

    for rel in dirs:
        dir_path = (root / rel).resolve()
        try:
            process_dir(
                dir_path, api_key, prompt,
                size=args.size, hue_fuzz=args.hue_fuzz,
                sat_min=args.sat_min, val_min=args.val_min,
                retries=args.retries, retry_backoff=args.retry_backoff
            )
        except Exception as e:
            print(f"[error] {rel}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
