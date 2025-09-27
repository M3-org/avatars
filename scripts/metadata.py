#!/usr/bin/env python3
import os
import json
import csv
import glob
import argparse

def get_markdown_bio(md_file_path):
    """Helper function to read markdown file content."""
    if md_file_path and os.path.exists(md_file_path):
        try:
            with open(md_file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading markdown file {md_file_path}: {e}")
            return None
    return None

def scan_avatars(base_dir="."):
    """Scans directories for avatar assets and returns structured data."""
    avatars_data = {}
    excluded_dirs = {".git", "scripts", "__pycache__", ".vscode", "_archives", "_incomplete", "_staging-removal"}

    avatar_folders = [
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d)) and d not in excluded_dirs
    ]

    for folder_name in sorted(avatar_folders):
        folder_path = os.path.join(base_dir, folder_name)

        data = {
            "bio": None,
            "markdown": None,
            "glb": None,
            "vrm": None,
            "bust_thumb": None,
            "glb_thumb": None
        }

        # Look for files using exact patterns
        md_file = os.path.join(folder_path, f"{folder_name}.md")
        if os.path.exists(md_file):
            data["bio"] = get_markdown_bio(md_file)
            data["markdown"] = os.path.join(folder_name, f"{folder_name}.md")

        glb_file = os.path.join(folder_path, f"{folder_name}.glb")
        if os.path.exists(glb_file):
            data["glb"] = os.path.join(folder_name, f"{folder_name}.glb")

        vrm_file = os.path.join(folder_path, f"{folder_name}.vrm")
        if os.path.exists(vrm_file):
            data["vrm"] = os.path.join(folder_name, f"{folder_name}.vrm")

        bust_thumb = os.path.join(folder_path, f"thumb-bust_{folder_name}.png")
        if os.path.exists(bust_thumb):
            data["bust_thumb"] = os.path.join(folder_name, f"thumb-bust_{folder_name}.png")

        glb_thumb = os.path.join(folder_path, f"thumb-glb_{folder_name}.png")
        if os.path.exists(glb_thumb):
            data["glb_thumb"] = os.path.join(folder_name, f"thumb-glb_{folder_name}.png")

        avatars_data[folder_name] = data

    return avatars_data

def generate_json(avatars_data, output_file="data.json"):
    """Generates JSON file with avatar data."""
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(avatars_data, f, indent=4, sort_keys=True)
        print(f"Generated {output_file}")
    except IOError as e:
        print(f"Error writing JSON file {output_file}: {e}")

def generate_csv(avatars_data, output_file="avatars.csv"):
    """Generates CSV file with avatar data."""
    header = ["Avatar", "Bust Thumbnail", "GLB Thumbnail", "Models", "Markdown"]
    rows = []

    for avatar_name, data in avatars_data.items():
        bust_thumb = data.get("bust_thumb", "")
        glb_thumb = data.get("glb_thumb", "")

        models_parts = []
        if data.get("glb"):
            filename = os.path.basename(data["glb"])
            models_parts.append(f"[{filename}]({data['glb']})")
        if data.get("vrm"):
            filename = os.path.basename(data["vrm"])
            models_parts.append(f"[{filename}]({data['vrm']})")
        models = " / ".join(models_parts)

        markdown = ""
        if data.get("markdown"):
            filename = os.path.basename(data["markdown"])
            markdown = f"[{filename}]({data['markdown']})"

        rows.append([avatar_name, bust_thumb, glb_thumb, models, markdown])

    try:
        with open(output_file, "w", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
        print(f"Generated {output_file}")
    except IOError as e:
        print(f"Error writing CSV file {output_file}: {e}")

def generate_readme(avatars_data, output_file="README.md"):
    """Generates README.md file with avatar table."""
    content = ["# Avatars\n"]
    content.append("## Naming Convention\n")
    content.append("For each avatar, create a folder named after the avatar (e.g., `my-avatar-name`). Inside this folder, the following file naming scheme is expected:\n")
    content.append("- **Avatar Folder:** `avatar-name/`")
    content.append("- **Bust Thumbnail:** `avatar-name/thumb-bust_avatar-name.png`")
    content.append("- **GLB Preview Thumbnail:** `avatar-name/thumb-glb_avatar-name.png`")
    content.append("- **GLB Model:** `avatar-name/avatar-name.glb`")
    content.append("- **VRM Model (Optional):** `avatar-name/avatar-name.vrm`")
    content.append("- **Markdown Bio:** `avatar-name/avatar-name.md`\n")
    content.append("---\n")
    content.append("| Avatar | Bust | GLB Preview | Models | Markdown |")
    content.append("|---|---|---|---|---|")

    for avatar_name, data in sorted(avatars_data.items()):
        bust_md = f"![{data['bust_thumb']}]({data['bust_thumb']})" if data.get('bust_thumb') else ""
        glb_md = f"![{data['glb_thumb']}]({data['glb_thumb']})" if data.get('glb_thumb') else ""

        models_parts = []
        if data.get("glb"):
            filename = os.path.basename(data["glb"])
            models_parts.append(f"[{filename}]({data['glb']})")
        if data.get("vrm"):
            filename = os.path.basename(data["vrm"])
            models_parts.append(f"[{filename}]({data['vrm']})")
        models_md = " / ".join(models_parts)

        markdown_md = ""
        if data.get("markdown"):
            filename = os.path.basename(data["markdown"])
            markdown_md = f"[{filename}]({data['markdown']})"

        content.append(f"| {avatar_name} | {bust_md} | {glb_md} | {models_md} | {markdown_md} |")

    with open(output_file, "w", encoding='utf-8') as f:
        f.write("\n".join(content) + "\n")
    print(f"Generated {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Generate avatar metadata files")
    parser.add_argument("--json", action="store_true", help="Generate data.json file")
    parser.add_argument("--csv", action="store_true", help="Generate avatars.csv file")
    parser.add_argument("--readme", action="store_true", help="Generate README.md file")
    parser.add_argument("--all", action="store_true", help="Generate all files (default)")
    parser.add_argument("--base-dir", default=".", help="Base directory to scan (default: current)")

    args = parser.parse_args()

    # Default to all if no specific flags given
    if not any([args.json, args.csv, args.readme]):
        args.all = True

    print("Scanning avatar directories...")
    avatars_data = scan_avatars(args.base_dir)

    if not avatars_data:
        print("No avatar data found. Please check subdirectories and naming conventions.")
        return

    print(f"Found {len(avatars_data)} avatar directories")

    if args.all or args.json:
        generate_json(avatars_data)

    if args.all or args.csv:
        generate_csv(avatars_data)

    if args.all or args.readme:
        generate_readme(avatars_data)

    print("Metadata generation complete!")

if __name__ == "__main__":
    main()