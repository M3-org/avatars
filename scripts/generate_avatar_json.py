import os
import json
import glob

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

def main():
    avatars_data = {}
    # Assuming the script is run from the root of the 'avatars' workspace
    base_dir = '.'  # Current directory

    # List all subdirectories in the base directory
    # These are assumed to be the avatar folders
    avatar_folders = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and not d.startswith('.')]

    for folder_name in sorted(avatar_folders):
        folder_path_full = os.path.join(base_dir, folder_name)
        
        avatars_data[folder_name] = {
            "bio": None,
            "glb": None,
            "bust": None,
            "glb_preview": None
        }

        # Find markdown file and read bio
        md_files = glob.glob(os.path.join(folder_path_full, '*.md'))
        if md_files:
            # Prefer md file with the same name as the folder if multiple exist
            preferred_md = os.path.join(folder_path_full, folder_name + '.md')
            if preferred_md in md_files:
                md_file_full = preferred_md
            else:
                md_file_full = md_files[0] # Take the first one found
            
            avatars_data[folder_name]["bio"] = get_markdown_bio(md_file_full)

        # Find GLB file
        glb_files = glob.glob(os.path.join(folder_path_full, '*.glb'))
        if glb_files:
            # Prefer glb file with the same name as the folder
            preferred_glb = os.path.join(folder_path_full, folder_name + '.glb')
            if preferred_glb in glb_files:
                 avatars_data[folder_name]["glb"] = os.path.join(folder_name, os.path.basename(preferred_glb))
            else:
                # Fallback to any .glb file if specific one isn't found
                avatars_data[folder_name]["glb"] = os.path.join(folder_name, os.path.basename(glb_files[0]))


        # Find bust_*.png file
        bust_files = glob.glob(os.path.join(folder_path_full, 'bust_*.png'))
        if bust_files:
            avatars_data[folder_name]["bust"] = os.path.join(folder_name, os.path.basename(bust_files[0]))
            # Prefer bust_foldername.png if multiple exist (e.g. bust_balancer.png vs bust_balancer2.png)
            preferred_bust = os.path.join(folder_path_full, f'bust_{folder_name}.png')
            if preferred_bust in bust_files:
                 avatars_data[folder_name]["bust"] = os.path.join(folder_name, os.path.basename(preferred_bust))
            else:
                # Fallback to the first bust file found alphabetically
                avatars_data[folder_name]["bust"] = os.path.join(folder_name, os.path.basename(sorted(bust_files)[0]))


        # Find glb_*.png file
        glb_preview_files = glob.glob(os.path.join(folder_path_full, 'glb_*.png'))
        if glb_preview_files:
            avatars_data[folder_name]["glb_preview"] = os.path.join(folder_name, os.path.basename(glb_preview_files[0]))
            # Prefer glb_foldername.png
            preferred_glb_preview = os.path.join(folder_path_full, f'glb_{folder_name}.png')
            if preferred_glb_preview in glb_preview_files:
                avatars_data[folder_name]["glb_preview"] = os.path.join(folder_name, os.path.basename(preferred_glb_preview))
            else:
                avatars_data[folder_name]["glb_preview"] = os.path.join(folder_name, os.path.basename(sorted(glb_preview_files)[0]))


    # Write the data to a JSON file
    output_file_name = 'data.json'
    try:
        with open(output_file_name, 'w', encoding='utf-8') as f:
            json.dump(avatars_data, f, indent=4)
        print(f"Successfully generated {output_file_name}")
    except IOError as e:
        print(f"Error writing JSON file {output_file_name}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    main() 
