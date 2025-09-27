#!/usr/bin/env python3
import os
import glob

def check_naming_consistency():
    mismatches = []

    # Get all directories except utility ones
    skip_dirs = {'scripts', '_archives', '_incomplete', '_staging-removal', '.git'}

    for item in os.listdir('.'):
        if os.path.isdir(item) and item not in skip_dirs and not item.startswith('.'):
            dir_name = item

            # Look for VRM or GLB files with the directory name
            expected_vrm = os.path.join(dir_name, f"{dir_name}.vrm")
            expected_glb = os.path.join(dir_name, f"{dir_name}.glb")

            has_expected_vrm = os.path.exists(expected_vrm)
            has_expected_glb = os.path.exists(expected_glb)

            # Check what VRM/GLB files actually exist
            actual_vrms = glob.glob(os.path.join(dir_name, "*.vrm"))
            actual_glbs = glob.glob(os.path.join(dir_name, "*.glb"))

            # If directory has models but none match the directory name
            if (actual_vrms or actual_glbs) and not (has_expected_vrm or has_expected_glb):
                primary_file = None
                if actual_vrms:
                    primary_file = os.path.basename(actual_vrms[0])
                elif actual_glbs:
                    primary_file = os.path.basename(actual_glbs[0])

                if primary_file:
                    mismatches.append({
                        'directory': dir_name,
                        'primary_file': primary_file,
                        'all_vrms': [os.path.basename(f) for f in actual_vrms],
                        'all_glbs': [os.path.basename(f) for f in actual_glbs]
                    })

    return mismatches

if __name__ == '__main__':
    mismatches = check_naming_consistency()

    if mismatches:
        print("NAMING INCONSISTENCIES FOUND:")
        print("=" * 50)
        for mismatch in mismatches:
            print(f"Directory: {mismatch['directory']}")
            print(f"Primary file: {mismatch['primary_file']}")
            if mismatch['all_vrms']:
                print(f"VRM files: {', '.join(mismatch['all_vrms'])}")
            if mismatch['all_glbs']:
                print(f"GLB files: {', '.join(mismatch['all_glbs'])}")
            print("-" * 30)

        print(f"\nTotal mismatches found: {len(mismatches)}")
    else:
        print("No naming inconsistencies found!")