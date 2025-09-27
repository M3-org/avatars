#!/usr/bin/env python3
"""
Enhanced Bust Thumbnail Generator (OpenRouter → PNG with transparent background)

Features edge detection + HSV chroma keying for improved background removal.
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
                           val_min: float = 0.15,
                           edge_blur: float = 1.0,
                           morph_radius: int = 2) -> Image.Image:
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

    from PIL import ImageChops, ImageFilter as _IF, ImageOps

    # Apply gaussian blur to soften the color-based mask
    mask = mask.filter(_IF.GaussianBlur(1.2))

    # Create edge-based mask for better boundary detection
    gray = ImageOps.grayscale(im)
    edges = gray.filter(_IF.FIND_EDGES)

    # Blur the edges to create softer transitions
    if edge_blur > 0:
        edges = edges.filter(_IF.GaussianBlur(edge_blur))

    # Invert edges so edges are dark, non-edges are light
    edges_inv = ImageOps.invert(edges)

    # Combine color mask with edge information
    # Where edges are strong (low values in edges_inv), we trust the color mask less
    # Where edges are weak (high values in edges_inv), we trust the color mask more
    edge_weight = Image.eval(edges_inv, lambda p: min(255, p + 128))  # Boost edge influence
    combined_mask = ImageChops.multiply(mask, edge_weight)

    # Apply morphological operations to clean up the mask
    if morph_radius > 0:
        # Erosion followed by dilation (opening) to remove noise
        from PIL import ImageFilter
        # Create a simple circular kernel approximation using multiple gaussian blurs
        eroded = combined_mask
        for _ in range(morph_radius):
            eroded = eroded.filter(_IF.MinFilter(3))

        dilated = eroded
        for _ in range(morph_radius):
            dilated = dilated.filter(_IF.MaxFilter(3))
        combined_mask = dilated

    # Apply final gaussian blur for smooth edges
    combined_mask = combined_mask.filter(_IF.GaussianBlur(0.8))

    # Apply the enhanced mask
    out = im.copy(); outA = out.split()[3]
    inv_mask = Image.eval(combined_mask, lambda p: 255 - p)
    final_alpha = ImageChops.multiply(outA, inv_mask)
    out.putalpha(final_alpha)
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
                retries: int, retry_backoff: float, force: bool = False,
                edge_blur: float = 1.0, morph_radius: int = 2) -> None:
    if not dir_path.is_dir():
        print(f"[skip] Not a directory: {dir_path}", file=sys.stderr)
        return

    out_path = dir_path / f"thumb-bust_{dir_path.name}.png"
    if out_path.exists() and not force:
        print(f"[skip] Exists: {out_path}")
        return

    guide = guess_guide_image(dir_path)
    print(f"[info] Guide: {guide if guide else 'none'}")
    print(f"[gen] {dir_path.name} → {out_path.name}")

    raw_png = call_with_retry(prompt, guide, api_key, retries=retries, backoff=retry_backoff)

    cutout = remove_background_auto(
        raw_png, fallback_hex="#00b140",
        hue_fuzz=hue_fuzz, sat_min=sat_min, val_min=val_min,
        edge_blur=edge_blur, morph_radius=morph_radius
    )

    final_img = resize_square_rgba(cutout, size=size)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    final_img.save(out_path, format="PNG", optimize=True)
    print(f"[ok] Wrote {out_path}")

def main():
    ap = argparse.ArgumentParser(description="Generate enhanced bust thumbnails with transparent background.")
    ap.add_argument("-i", "--input-dir", default=".", help="Input directory containing avatar folders (default: current)")
    ap.add_argument("--prompt", help="Custom prompt (default: uses vn_bust.txt or built-in)")
    ap.add_argument("--size", type=int, default=400, help="Output square size (default 400)")
    ap.add_argument("-f", "--force", action="store_true", help="Force overwrite existing thumbnails")
    ap.add_argument("--edge-blur", type=float, default=1.0, help="Edge detection blur radius (default 1.0)")
    ap.add_argument("--morph-radius", type=int, default=2, help="Morphological operation radius (default 2)")
    args = ap.parse_args()

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("ERROR: OPENROUTER_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    input_dir = Path(args.input_dir).resolve()

    # Load prompt: custom > vn_bust.txt > default
    prompt = DEFAULT_PROMPT
    if args.prompt:
        prompt = args.prompt
    else:
        vn_prompt_file = Path("scripts/vn_bust.txt")
        if vn_prompt_file.exists():
            prompt = vn_prompt_file.read_text().strip()

    # Read directory names from stdin
    dirs = []
    for line in sys.stdin:
        line = line.strip()
        if line and not line.startswith("#"):
            dirs.append(line)

    if not dirs:
        print("Nothing to do; no directories provided via stdin.", file=sys.stderr)
        sys.exit(0)

    for rel in dirs:
        dir_path = (input_dir / rel).resolve()
        try:
            process_dir(
                dir_path, api_key, prompt,
                size=args.size, hue_fuzz=18,
                sat_min=0.15, val_min=0.15,
                retries=3, retry_backoff=2.0,
                force=args.force, edge_blur=args.edge_blur,
                morph_radius=args.morph_radius
            )
        except Exception as e:
            print(f"[error] {rel}: {e}", file=sys.stderr)

if __name__ == "__main__":
    main()
