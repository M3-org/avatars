import os
import json
import csv # Added for CSV export

def get_markdown_bio(md_file_path_full):
    """Helper function to read markdown file content."""
    if md_file_path_full and os.path.exists(md_file_path_full):
        try:
            with open(md_file_path_full, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading markdown file {md_file_path_full}: {e}")
            return None
    return None

def generate_csv(avatars_data, csv_file_path="avatars.csv"):
    """Generates the avatars.csv file."""
    header = ["Avatar", "Bust Thumbnail", "GLB Thumbnail", "Models", "Markdown"]
    rows = []

    for avatar_name, data in avatars_data.items():
        bust_thumb_path = data.get("bust_thumb") or ""
        glb_thumb_path = data.get("glb_thumb") or ""
        
        models_md_parts = []
        if data.get("glb"):
            glb_filename = os.path.basename(data["glb"])
            models_md_parts.append(f"[{glb_filename}]({data['glb']})")
        if data.get("vrm"):
            vrm_filename = os.path.basename(data["vrm"])
            models_md_parts.append(f"[{vrm_filename}]({data['vrm']})")
        models_md = " / ".join(models_md_parts)

        md_link = ""
        if data.get("markdown"):
            md_filename = os.path.basename(data["markdown"])
            md_link = f"[{md_filename}]({data['markdown']})"
            
        rows.append([
            avatar_name,
            bust_thumb_path,
            glb_thumb_path,
            models_md,
            md_link
        ])

    try:
        with open(csv_file_path, "w", newline="", encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(header)
            writer.writerows(rows)
        print(f"Successfully generated {csv_file_path}")
    except IOError as e:
        print(f"Error writing CSV file {csv_file_path}: {e}")

def main():
    avatars_data = {}
    # Assuming the script is run from the root of the 'avatars' workspace
    base_dir = '.' 
    excluded_dirs = {".git", "scripts", "__pycache__", ".vscode"} # Set of directories to exclude

    avatar_folders = [
        d for d in os.listdir(base_dir) 
        if os.path.isdir(os.path.join(base_dir, d)) and d not in excluded_dirs
    ]

    for folder_name in sorted(avatar_folders):
        folder_path_full = os.path.join(base_dir, folder_name)
        
        # Initialize data structure for this avatar
        data = {
            "bio": None,
            "markdown": None,
            "glb": None,
            "vrm": None,
            "bust_thumb": None,
            "glb_thumb": None
        }

        # Markdown file (bio and path)
        md_file_name = f"{folder_name}.md"
        md_file_full_path = os.path.join(folder_path_full, md_file_name)
        if os.path.exists(md_file_full_path):
            data["bio"] = get_markdown_bio(md_file_full_path)
            data["markdown"] = os.path.join(folder_name, md_file_name)

        # GLB model file
        glb_file_name = f"{folder_name}.glb"
        glb_file_full_path = os.path.join(folder_path_full, glb_file_name)
        if os.path.exists(glb_file_full_path):
            data["glb"] = os.path.join(folder_name, glb_file_name)

        # VRM model file
        vrm_file_name = f"{folder_name}.vrm"
        vrm_file_full_path = os.path.join(folder_path_full, vrm_file_name)
        if os.path.exists(vrm_file_full_path):
            data["vrm"] = os.path.join(folder_name, vrm_file_name)
        
        # Bust thumbnail image
        bust_thumb_file_name = f"thumb-bust_{folder_name}.png"
        bust_thumb_full_path = os.path.join(folder_path_full, bust_thumb_file_name)
        if os.path.exists(bust_thumb_full_path):
            data["bust_thumb"] = os.path.join(folder_name, bust_thumb_file_name)

        # GLB thumbnail image
        glb_thumb_file_name = f"thumb-glb_{folder_name}.png"
        glb_thumb_full_path = os.path.join(folder_path_full, glb_thumb_file_name)
        if os.path.exists(glb_thumb_full_path):
            data["glb_thumb"] = os.path.join(folder_name, glb_thumb_file_name)
            
        avatars_data[folder_name] = data

    # Write the data to a JSON file
    json_output_file_name = 'data.json'
    try:
        with open(json_output_file_name, 'w', encoding='utf-8') as f:
            json.dump(avatars_data, f, indent=4, sort_keys=True) # Added sort_keys for consistent output
        print(f"Successfully generated {json_output_file_name}")
    except IOError as e:
        print(f"Error writing JSON file {json_output_file_name}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred during JSON generation: {e}")

    # Generate CSV file
    csv_output_file_name = 'avatars.csv'
    generate_csv(avatars_data, csv_output_file_name)

if __name__ == '__main__':
    main() 
