# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a 3D avatar repository containing branded crypto/Web3 project avatars in various formats (GLB, VRM). Each avatar represents a character with detailed personality, backstory, and catchphrases documented in markdown files. The avatars are designed for use in virtual environments, streaming, and AI agent personas.

## Repository Structure

The repository follows a consistent directory structure:
- Each avatar has its own directory named after the project (e.g., `aave/`, `uniswap/`, `eliza/`)
- Within each directory:
  - `{name}.glb` - 3D model in GLB format
  - `{name}.vrm` - VRM format (optional, for VRChat/VTuber use)
  - `{name}.md` - Character biography, personality, and catchphrases
  - `thumb-bust_{name}.png` - Character portrait thumbnail
  - `thumb-glb_{name}.png` - 3D model preview thumbnail
  - `{name}_mapping.json` - Bone mapping for VRM conversion (if applicable)

**Utility Directories:**
- `_archives/` - Archive files (zip backups, old collections)
- `_incomplete/` - Incomplete avatar data that needs models or proper bios
- `_source-files/` - Blender files and other development assets
- `scripts/` - Python utilities for metadata generation

## Common Development Tasks

### Generate Metadata Files
To regenerate metadata files after adding new avatars:
```bash
python scripts/generate_all_metadata.py
```

Options:
- `--json`: Generate data.json for programmatic access
- `--csv`: Generate avatars.csv for spreadsheet use
- `--readme`: Generate README.md with markdown tables
- `--all`: Generate all files (default)

### Convert FBX to VRM (Blender Required)
For converting FBX models to VRM format:
```bash
blender --background --python scripts/fbx2vrm.py -- input.fbx output.vrm --mappings_dir out/
```

### Convert GLB to VRM (Blender Required)
For converting GLB models to VRM format:
```bash
blender --background --python scripts/glb2vrm.py -- input.glb output.vrm
```

## Adding New Avatars

When adding a new avatar:
1. Create a new directory with the avatar name
2. Add the required files following the naming convention
3. Create a markdown bio following the existing format (personality, values, relationships, catchphrases)
4. Run the metadata generation scripts to update README.md and data.json
5. Commit changes with descriptive message

## Character Bio Format

Each avatar's markdown file should include:
- Character name and brief description
- **Personality** - Key character traits and mannerisms
- **Values & Perspective** - Core beliefs and worldview
- **Core Knowledge** - Technical expertise areas
- **Relationships** - Interactions with other avatars/protocols
- **Catchphrases** - Memorable quotes that define the character

## File Naming Conventions

- Directory names: lowercase with hyphens (e.g., `magic-eden/`)
- Model files: `{avatar-name}.glb`, `{avatar-name}.vrm`
- Thumbnails: `thumb-bust_{avatar-name}.png`, `thumb-glb_{avatar-name}.png`
- Bio files: `{avatar-name}.md`
- Mapping files: `{avatar-name}_mapping.json`

## Key Files

- `README.md` - Auto-generated table of all avatars and their assets
- `data.json` - Complete avatar metadata in JSON format
- `avatars.csv` - CSV export of avatar data
- `scripts/` - Python utilities for metadata generation and model conversion
- no need to cd, make sure you're in the right directory and do pwd before commands