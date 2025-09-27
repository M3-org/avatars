#!/usr/bin/env python3
"""
Avatar Repository Validation Script

Validates avatar directory structure and identifies missing files for automated
regeneration workflows. Designed for GitHub Actions integration.

Usage:
    python validate.py [--format json|text] [--missing-only] [--exit-code]
"""
import os
import glob
import json
import argparse
import sys
from typing import List, Dict, Any

def scan_avatar_directories(base_dir: str = ".") -> Dict[str, Any]:
    """Scan avatar directories and validate file structure."""
    results = {
        'valid_avatars': [],
        'naming_issues': [],
        'missing_thumbnails': [],
        'missing_models': [],
        'missing_bios': [],
        'summary': {}
    }

    skip_dirs = {'scripts', '_archives', '_incomplete', '_staging-removal', '.git', '__pycache__', '.vscode'}

    avatar_dirs = [
        d for d in os.listdir(base_dir)
        if os.path.isdir(os.path.join(base_dir, d)) and d not in skip_dirs and not d.startswith('.')
    ]

    for dir_name in sorted(avatar_dirs):
        dir_path = os.path.join(base_dir, dir_name)
        avatar_info = validate_avatar_directory(dir_name, dir_path)

        if avatar_info['is_valid']:
            results['valid_avatars'].append(avatar_info)

        # Collect issues for different categories
        if avatar_info['naming_issue']:
            results['naming_issues'].append(avatar_info)
        if not avatar_info['has_bust_thumb'] or not avatar_info['has_glb_thumb']:
            results['missing_thumbnails'].append(avatar_info)
        if not avatar_info['has_model']:
            results['missing_models'].append(avatar_info)
        if not avatar_info['has_bio']:
            results['missing_bios'].append(avatar_info)

    # Generate summary
    total_dirs = len(avatar_dirs)
    results['summary'] = {
        'total_directories': total_dirs,
        'valid_avatars': len(results['valid_avatars']),
        'naming_issues': len(results['naming_issues']),
        'missing_thumbnails': len(results['missing_thumbnails']),
        'missing_models': len(results['missing_models']),
        'missing_bios': len(results['missing_bios']),
        'completion_rate': f"{(len(results['valid_avatars']) / total_dirs * 100):.1f}%" if total_dirs > 0 else "0%"
    }

    return results

def validate_avatar_directory(dir_name: str, dir_path: str) -> Dict[str, Any]:
    """Validate a single avatar directory."""
    info = {
        'directory': dir_name,
        'path': dir_path,
        'has_model': False,
        'has_bust_thumb': False,
        'has_glb_thumb': False,
        'has_bio': False,
        'naming_issue': False,
        'is_valid': False,
        'files': {
            'vrm_files': [],
            'glb_files': [],
            'bust_thumbs': [],
            'glb_thumbs': [],
            'bio_files': []
        },
        'expected_files': {
            'vrm': f"{dir_name}.vrm",
            'glb': f"{dir_name}.glb",
            'bust_thumb': f"thumb-bust_{dir_name}.png",
            'glb_thumb': f"thumb-glb_{dir_name}.png",
            'bio': f"{dir_name}.md"
        }
    }

    # Scan actual files
    vrm_files = glob.glob(os.path.join(dir_path, "*.vrm"))
    glb_files = glob.glob(os.path.join(dir_path, "*.glb"))
    bust_thumbs = glob.glob(os.path.join(dir_path, "thumb-bust_*.png"))
    glb_thumbs = glob.glob(os.path.join(dir_path, "thumb-glb_*.png"))
    bio_files = glob.glob(os.path.join(dir_path, "*.md"))

    info['files']['vrm_files'] = [os.path.basename(f) for f in vrm_files]
    info['files']['glb_files'] = [os.path.basename(f) for f in glb_files]
    info['files']['bust_thumbs'] = [os.path.basename(f) for f in bust_thumbs]
    info['files']['glb_thumbs'] = [os.path.basename(f) for f in glb_thumbs]
    info['files']['bio_files'] = [os.path.basename(f) for f in bio_files]

    # Check for expected files
    expected_vrm = os.path.join(dir_path, info['expected_files']['vrm'])
    expected_glb = os.path.join(dir_path, info['expected_files']['glb'])
    expected_bust = os.path.join(dir_path, info['expected_files']['bust_thumb'])
    expected_glb_thumb = os.path.join(dir_path, info['expected_files']['glb_thumb'])
    expected_bio = os.path.join(dir_path, info['expected_files']['bio'])

    # Validate model files
    has_expected_vrm = os.path.exists(expected_vrm)
    has_expected_glb = os.path.exists(expected_glb)
    info['has_model'] = has_expected_vrm or has_expected_glb

    # Check for naming issues (has models but none match directory name)
    if (vrm_files or glb_files) and not (has_expected_vrm or has_expected_glb):
        info['naming_issue'] = True

    # Validate thumbnails
    info['has_bust_thumb'] = os.path.exists(expected_bust)
    info['has_glb_thumb'] = os.path.exists(expected_glb_thumb)

    # Validate bio
    info['has_bio'] = os.path.exists(expected_bio)

    # Overall validation
    info['is_valid'] = (
        info['has_model'] and
        info['has_bust_thumb'] and
        info['has_glb_thumb'] and
        info['has_bio'] and
        not info['naming_issue']
    )

    return info

def generate_missing_files_list(results: Dict[str, Any]) -> List[str]:
    """Generate list of directories that need file regeneration."""
    missing_dirs = set()

    for avatar in results['missing_thumbnails']:
        missing_dirs.add(avatar['directory'])

    for avatar in results['missing_bios']:
        missing_dirs.add(avatar['directory'])

    return sorted(list(missing_dirs))

def print_text_report(results: Dict[str, Any], missing_only: bool = False):
    """Print human-readable validation report."""
    summary = results['summary']

    print("🔍 AVATAR REPOSITORY VALIDATION REPORT")
    print("=" * 50)
    print(f"📁 Total Directories: {summary['total_directories']}")
    print(f"✅ Valid Avatars: {summary['valid_avatars']}")
    print(f"📊 Completion Rate: {summary['completion_rate']}")
    print()

    if not missing_only:
        print(f"⚠️  Issues Found:")
        print(f"   • Naming Issues: {summary['naming_issues']}")
        print(f"   • Missing Thumbnails: {summary['missing_thumbnails']}")
        print(f"   • Missing Models: {summary['missing_models']}")
        print(f"   • Missing Bios: {summary['missing_bios']}")
        print()

    # Show naming issues
    if results['naming_issues'] and not missing_only:
        print("🏷️  NAMING INCONSISTENCIES:")
        print("-" * 30)
        for issue in results['naming_issues']:
            print(f"Directory: {issue['directory']}")
            if issue['files']['vrm_files']:
                print(f"  VRM files: {', '.join(issue['files']['vrm_files'])}")
            if issue['files']['glb_files']:
                print(f"  GLB files: {', '.join(issue['files']['glb_files'])}")
            print()

    # Show missing thumbnails
    if results['missing_thumbnails']:
        print("🖼️  MISSING THUMBNAILS:")
        print("-" * 30)
        for avatar in results['missing_thumbnails']:
            missing = []
            if not avatar['has_bust_thumb']:
                missing.append("bust thumbnail")
            if not avatar['has_glb_thumb']:
                missing.append("GLB thumbnail")
            print(f"{avatar['directory']}: {', '.join(missing)}")
        print()

    # Show missing bios
    if results['missing_bios']:
        print("📝 MISSING BIOS:")
        print("-" * 30)
        for avatar in results['missing_bios']:
            print(f"{avatar['directory']}: needs {avatar['expected_files']['bio']}")
        print()

    # Generate workflow suggestions
    missing_dirs = generate_missing_files_list(results)
    if missing_dirs:
        print("🚀 AUTOMATION SUGGESTIONS:")
        print("-" * 30)
        print("Directories needing regeneration:")
        for dir_name in missing_dirs[:10]:  # Show first 10
            print(f"  • {dir_name}")
        if len(missing_dirs) > 10:
            print(f"  ... and {len(missing_dirs) - 10} more")
        print()
        print("💡 To regenerate missing files:")
        dirs_list = "\\n".join(missing_dirs)
        print(f"   python scripts/thumbnails.py --list <(echo -e '{dirs_list}')")

def main():
    parser = argparse.ArgumentParser(description="Validate avatar repository structure")
    parser.add_argument("--format", choices=["json", "text"], default="text",
                       help="Output format (default: text)")
    parser.add_argument("--missing-only", action="store_true",
                       help="Only show missing files, not all issues")
    parser.add_argument("--exit-code", action="store_true",
                       help="Exit with non-zero code if issues found (for CI)")
    parser.add_argument("--base-dir", default=".",
                       help="Base directory to scan (default: current)")

    args = parser.parse_args()

    results = scan_avatar_directories(args.base_dir)

    if args.format == "json":
        print(json.dumps(results, indent=2))
    else:
        print_text_report(results, args.missing_only)

    # Exit with error code for CI if requested and issues found
    if args.exit_code:
        has_issues = (
            results['summary']['naming_issues'] > 0 or
            results['summary']['missing_thumbnails'] > 0 or
            results['summary']['missing_models'] > 0 or
            results['summary']['missing_bios'] > 0
        )
        if has_issues:
            sys.exit(1)

if __name__ == "__main__":
    main()