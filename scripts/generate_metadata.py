import os
import csv
import glob

def get_avatar_data(base_dir="."):
    """Scans subdirectories for avatar assets."""
    avatar_data = []
    excluded_dirs = ["scripts", ".git", "__pycache__"] # Add any other dirs to exclude

    for item in os.listdir(base_dir):
        item_path = os.path.join(base_dir, item)
        if os.path.isdir(item_path) and item not in excluded_dirs:
            avatar_name = item

            bust_pattern = os.path.join(item_path, f"thumb-bust_{avatar_name}.png")
            glb_preview_pattern = os.path.join(item_path, f"thumb-glb_{avatar_name}.png")
            glb_model_pattern = os.path.join(item_path, f"{avatar_name}.glb")
            vrm_model_pattern = os.path.join(item_path, f"{avatar_name}.vrm")
            md_file_pattern = os.path.join(item_path, f"{avatar_name}.md")

            data = {"name": avatar_name}

            # More robust file finding using glob for exact match
            bust_files = glob.glob(bust_pattern)
            data["bust_thumb"] = os.path.join(avatar_name, os.path.basename(bust_files[0])) if bust_files else ""
            
            glb_preview_files = glob.glob(glb_preview_pattern)
            data["glb_thumb"] = os.path.join(avatar_name, os.path.basename(glb_preview_files[0])) if glb_preview_files else ""

            glb_model_files = glob.glob(glb_model_pattern)
            data["glb_model"] = os.path.join(avatar_name, os.path.basename(glb_model_files[0])) if glb_model_files else ""
            
            vrm_model_files = glob.glob(vrm_model_pattern)
            data["vrm_model"] = os.path.join(avatar_name, os.path.basename(vrm_model_files[0])) if vrm_model_files else ""

            md_files = glob.glob(md_file_pattern)
            data["md_file"] = os.path.join(avatar_name, os.path.basename(md_files[0])) if md_files else ""
            
            avatar_data.append(data)
    
    avatar_data.sort(key=lambda x: x["name"].lower())
    return avatar_data

def generate_readme(avatar_data, readme_file="README.md"):
    """Generates the README.md file."""
    content = ["# Avatars\n"]
    content.append("## Naming Convention\n")
    content.append("For each avatar, create a folder named after the avatar (e.g., `my-avatar-name`). Inside this folder, the following file naming scheme is expected:\n")
    content.append("- **Avatar Folder:** `avatar-name/`")
    content.append("- **Bust Thumbnail:** `avatar-name/thumb-bust_avatar-name.png`")
    content.append("- **GLB Preview Thumbnail:** `avatar-name/thumb-glb_avatar-name.png`")
    content.append("- **GLB Model:** `avatar-name/avatar-name.glb`")
    content.append("- **VRM Model (Optional):** `avatar-name/avatar-name.vrm`")
    content.append("- **Markdown Bio:** `avatar-name/avatar-name.md`\n")
    content.append("---\n") # Horizontal rule or just a blank line
    content.append("| Avatar | Bust | GLB Preview | Models | Markdown |")
    content.append("|---|---|---|---|---|")

    for avatar in avatar_data:
        name = avatar['name']
        
        bust_thumb_md = f"![{avatar['bust_thumb']}]({avatar['bust_thumb']})" if avatar['bust_thumb'] else ""
        glb_thumb_md = f"![{avatar['glb_thumb']}]({avatar['glb_thumb']})" if avatar['glb_thumb'] else ""
        
        models_md_parts = []
        if avatar['glb_model']:
            glb_filename = os.path.basename(avatar['glb_model'])
            models_md_parts.append(f"[{glb_filename}]({avatar['glb_model']})")
        if avatar['vrm_model']:
            vrm_filename = os.path.basename(avatar['vrm_model'])
            models_md_parts.append(f"[{vrm_filename}]({avatar['vrm_model']})")
        models_md = " / ".join(models_md_parts)

        md_file_md = ""
        if avatar['md_file']:
            md_filename = os.path.basename(avatar['md_file'])
            md_file_md = f"[{md_filename}]({avatar['md_file']})"
            
        content.append(f"| {name} | {bust_thumb_md} | {glb_thumb_md} | {models_md} | {md_file_md} |")

    with open(readme_file, "w") as f:
        f.write("\\n".join(content) + "\\n")
    print(f"Generated {readme_file}")

def generate_csv(avatar_data, csv_file="avatars.csv"):
    """Generates the avatars.csv file."""
    header = ["Avatar", "Bust", "GLB Preview", "Models", "Markdown"]
    rows = []

    for avatar in avatar_data:
        name = avatar['name']
        bust_thumb_path = avatar['bust_thumb'] if avatar['bust_thumb'] else ""
        glb_thumb_path = avatar['glb_thumb'] if avatar['glb_thumb'] else ""

        models_csv_parts = []
        if avatar['glb_model']:
            glb_filename = os.path.basename(avatar['glb_model'])
            models_csv_parts.append(f"[{glb_filename}]({avatar['glb_model']})")
        if avatar['vrm_model']:
            vrm_filename = os.path.basename(avatar['vrm_model'])
            models_csv_parts.append(f"[{vrm_filename}]({avatar['vrm_model']})")
        models_csv = " / ".join(models_csv_parts)
        
        md_file_csv = ""
        if avatar['md_file']:
            md_filename = os.path.basename(avatar['md_file'])
            md_file_csv = f"[{md_filename}]({avatar['md_file']})"

        rows.append([
            name,
            bust_thumb_path,
            glb_thumb_path,
            models_csv, # This will be a string like "[file.glb](path) / [file.vrm](path)"
            md_file_csv   # This will be a string like "[file.md](path)"
        ])

    with open(csv_file, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(rows)
    print(f"Generated {csv_file}")

if __name__ == "__main__":
    print("Starting metadata generation...")
    avatars = get_avatar_data()
    if not avatars:
        print("No avatar data found. Please check subdirectories and naming conventions.")
    else:
        generate_readme(avatars)
        generate_csv(avatars)
    print("Metadata generation finished.") 