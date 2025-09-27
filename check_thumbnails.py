#!/usr/bin/env python3
import os
import glob

def check_thumbnail_consistency():
    issues = []
    skip_dirs = {'scripts', '_archives', '_incomplete', '_staging-removal', '.git'}

    for item in os.listdir('.'):
        if os.path.isdir(item) and item not in skip_dirs and not item.startswith('.'):
            dir_name = item

            # Check for expected thumbnails
            expected_bust = os.path.join(dir_name, f"thumb-bust_{dir_name}.png")
            expected_glb = os.path.join(dir_name, f"thumb-glb_{dir_name}.png")

            has_expected_bust = os.path.exists(expected_bust)
            has_expected_glb = os.path.exists(expected_glb)

            # Check what thumbnails actually exist
            actual_bust_thumbs = glob.glob(os.path.join(dir_name, "thumb-bust_*.png"))
            actual_glb_thumbs = glob.glob(os.path.join(dir_name, "thumb-glb_*.png"))

            # Check if directory has models but missing proper thumbnails
            has_vrm = bool(glob.glob(os.path.join(dir_name, "*.vrm")))
            has_glb = bool(glob.glob(os.path.join(dir_name, "*.glb")))

            if (has_vrm or has_glb):  # Directory has models
                issue = {
                    'directory': dir_name,
                    'has_models': True,
                    'expected_bust_exists': has_expected_bust,
                    'expected_glb_exists': has_expected_glb,
                    'actual_bust_thumbs': [os.path.basename(f) for f in actual_bust_thumbs],
                    'actual_glb_thumbs': [os.path.basename(f) for f in actual_glb_thumbs],
                    'has_vrm': has_vrm,
                    'has_glb': has_glb
                }

                # Only report if there are thumbnail issues
                if not (has_expected_bust or has_expected_glb) and (actual_bust_thumbs or actual_glb_thumbs):
                    issues.append(issue)
                elif not (has_expected_bust and has_expected_glb) and not (actual_bust_thumbs or actual_glb_thumbs):
                    # Has models but no thumbnails at all
                    issue['no_thumbnails'] = True
                    issues.append(issue)

    return issues

if __name__ == '__main__':
    issues = check_thumbnail_consistency()

    if issues:
        print("THUMBNAIL NAMING ISSUES FOUND:")
        print("=" * 50)
        for issue in issues:
            print(f"Directory: {issue['directory']}")
            print(f"Has VRM: {issue['has_vrm']}, Has GLB: {issue['has_glb']}")
            print(f"Expected bust exists: {issue['expected_bust_exists']}")
            print(f"Expected GLB thumb exists: {issue['expected_glb_exists']}")

            if issue['actual_bust_thumbs']:
                print(f"Actual bust thumbs: {', '.join(issue['actual_bust_thumbs'])}")
            if issue['actual_glb_thumbs']:
                print(f"Actual GLB thumbs: {', '.join(issue['actual_glb_thumbs'])}")

            if issue.get('no_thumbnails'):
                print("⚠️  NO THUMBNAILS FOUND")

            print("-" * 30)

        print(f"\nTotal directories with thumbnail issues: {len(issues)}")
    else:
        print("No thumbnail naming issues found!")