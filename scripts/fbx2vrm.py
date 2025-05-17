import os
import sys
import bpy
import argparse
import logging

def parse_arguments():
    parser = argparse.ArgumentParser(description="Import FBX and export as VRM using custom bone mappings")
    parser.add_argument("fbx_path", help="Path to the FBX file")
    parser.add_argument("output_vrm", help="Output VRM file path")
    parser.add_argument("--mappings_dir", default="out", help="Directory containing bone mapping JSON files")
    parser.add_argument("--force", action="store_true", help="Force export even with validation errors")
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1:])

def import_fbx(fbx_path):
    bpy.ops.import_scene.fbx(filepath=fbx_path)
    logging.info(f"Imported FBX: {fbx_path}")

def find_armature():
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            return obj
    raise RuntimeError("No armature found in scene.")

def setup_vrm_extensions(armature):
    """Set up basic VRM metadata"""
    # Initialize VRM extension
    armature.data.vrm_addon_extension.spec_version = "0.0"
    
    # Set basic metadata
    meta = armature.data.vrm_addon_extension.vrm0.meta
    meta.author = "AutoExport"
    meta.version = "0.0"
    meta.title = os.path.basename(armature.name)
    meta.license_name = 'CC0'
    
    # Make sure the armature is the active object
    bpy.context.view_layer.objects.active = armature
    armature.select_set(True)

def load_bone_mapping(model_name, mappings_dir):
    """Get the path to the bone mapping file for this model"""
    mapping_file = os.path.join(mappings_dir, f"{model_name}_mapping.json")
    if os.path.exists(mapping_file):
        return mapping_file
    return None

def export_vrm(output_path, force=False):
    """Export the current scene as a VRM file"""
    # Set export options
    export_options = {
        "filepath": output_path,
        "export_invisibles": False,
        "enable_advanced_preferences": True,
        "export_only_selections": False
    }
    
    result = bpy.ops.export_scene.vrm(**export_options)
    
    if 'FINISHED' in result:
        logging.info(f"Exported VRM to: {output_path}")
        return True
    else:
        if not force:
            logging.error(f"VRM export failed: {result}. Try using --force option to bypass validation.")
            return False
        else:
            logging.error(f"VRM export failed even with --force option: {result}")
            return False

def clean_up():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes: bpy.data.meshes.remove(block)
    for block in bpy.data.armatures: bpy.data.armatures.remove(block)

def process_file(fbx_path, output_vrm, mappings_dir, force=False):
    """Process a single FBX file"""
    # Clean up scene
    clean_up()
    
    # Import FBX
    import_fbx(fbx_path)
    
    # Find armature
    try:
        armature = find_armature()
        bpy.context.view_layer.objects.active = armature
    except RuntimeError as e:
        logging.error(str(e))
        return False
    
    # Set up VRM extension
    setup_vrm_extensions(armature)
    
    # Get model name from FBX path (without extension)
    model_name = os.path.basename(fbx_path).split('.')[0]
    
    # Load bone mapping
    mapping_file = load_bone_mapping(model_name, mappings_dir)
    if mapping_file:
        logging.info(f"Loading bone mapping from: {mapping_file}")
        # Use the built-in operator to load the mapping
        bpy.ops.vrm.load_human_bone_mappings(filepath=mapping_file)
    else:
        logging.warning(f"No bone mapping file found for {model_name}")
    
    # Export VRM
    return export_vrm(output_vrm, force)

def main():
    args = parse_arguments()
    
    # Set up logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Create output directory if doesn't exist
    output_dir = os.path.dirname(args.output_vrm)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    process_file(args.fbx_path, args.output_vrm, args.mappings_dir, args.force)
    
    # Final cleanup
    clean_up()

if __name__ == "__main__":
    main()
