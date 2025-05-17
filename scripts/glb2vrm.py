import os
import sys
import bpy
import argparse
import logging

def parse_arguments():
    parser = argparse.ArgumentParser(description="Import GLB and export as VRM")
    parser.add_argument("glb_path", help="Path to the GLB file")
    parser.add_argument("output_vrm", help="Output VRM file path")
    return parser.parse_args(sys.argv[sys.argv.index("--") + 1:])

def import_glb(glb_path):
    bpy.ops.import_scene.gltf(filepath=glb_path, bone_heuristic='FORTUNE')
    logging.info(f"Imported GLB: {glb_path}")

def find_armature():
    for obj in bpy.context.scene.objects:
        if obj.type == 'ARMATURE':
            return obj
    raise RuntimeError("No armature found in scene.")

def export_vrm(output_path, armature_name):
    armature = bpy.data.objects[armature_name]
    armature.data.vrm_addon_extension.spec_version = "0.0"

    # Minimal metadata
    vrm_meta = armature.data.vrm_addon_extension.vrm0.meta
    vrm_meta.title = "Converted from GLB"
    vrm_meta.version = "1.0"
    vrm_meta.author = "AutoExport"
    vrm_meta.license_name = 'CC0'

    bpy.ops.object.select_all(action='DESELECT')
    armature.select_set(True)
    bpy.context.view_layer.objects.active = armature

    result = bpy.ops.export_scene.vrm(
        filepath=output_path,
        export_invisibles=False,
        enable_advanced_preferences=True,
        export_fb_ngon_encoding=False,
        export_only_selections=False
    )

    if 'FINISHED' not in result:
        raise RuntimeError(f"VRM export failed: {result}")
    logging.info(f"Exported VRM to: {output_path}")

def clean_up():
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    for block in bpy.data.meshes: bpy.data.meshes.remove(block)
    for block in bpy.data.armatures: bpy.data.armatures.remove(block)

def main():
    args = parse_arguments()
    clean_up()
    import_glb(args.glb_path)
    armature = find_armature()
    export_vrm(args.output_vrm, armature.name)
    clean_up()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
