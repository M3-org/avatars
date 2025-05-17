import os
import json
import glob

# Create out directory if it doesn't exist
if not os.path.exists('out'):
    os.makedirs('out')

# Define the VRM bone mapping dictionaries for different naming conventions
def get_bone_mappings():
    # Dictionary of different mapping types
    mappings = {
        # CC_Base naming convention
        "cc_base": {
            "hips": "CC_Base_Hip",
            "spine": "CC_Base_Spine01",
            "chest": "CC_Base_Spine02",
            "neck": "CC_Base_NeckTwist01",
            "head": "CC_Base_Head",
            "leftUpperLeg": "CC_Base_L_Thigh",
            "leftLowerLeg": "CC_Base_L_Calf",
            "leftFoot": "CC_Base_L_Foot",
            "leftToes": "CC_Base_L_ToeBase",
            "rightUpperLeg": "CC_Base_R_Thigh",
            "rightLowerLeg": "CC_Base_R_Calf",
            "rightFoot": "CC_Base_R_Foot",
            "rightToes": "CC_Base_R_ToeBase",
            "leftShoulder": "CC_Base_L_Clavicle",
            "leftUpperArm": "CC_Base_L_Upperarm",
            "leftLowerArm": "CC_Base_L_Forearm",
            "leftHand": "CC_Base_L_Hand",
            "rightShoulder": "CC_Base_R_Clavicle",
            "rightUpperArm": "CC_Base_R_Upperarm",
            "rightLowerArm": "CC_Base_R_Forearm",
            "rightHand": "CC_Base_R_Hand"
        },
        
        # Standard naming convention (Hips, Spine, etc.)
        "standard": {
            "hips": "Hips",
            "spine": "Spine",
            "chest": "Spine1",
            "upperChest": "Spine2",
            "neck": "Neck",
            "head": "Head",
            "leftUpperLeg": "LeftUpLeg",
            "leftLowerLeg": "LeftLeg",
            "leftFoot": "LeftFoot",
            "leftToes": "LeftToeBase",
            "rightUpperLeg": "RightUpLeg",
            "rightLowerLeg": "RightLeg",
            "rightFoot": "RightFoot",
            "rightToes": "RightToeBase",
            "leftShoulder": "LeftShoulder",
            "leftUpperArm": "LeftArm",
            "leftLowerArm": "LeftForeArm",
            "leftHand": "LeftHand",
            "rightShoulder": "RightShoulder",
            "rightUpperArm": "RightArm",
            "rightLowerArm": "RightForeArm",
            "rightHand": "RightHand"
        },
        
        # J_Bip naming convention
        "j_bip": {
            "hips": "J_Bip_C_Hips",
            "spine": "J_Bip_C_Spine",
            "chest": "J_Bip_C_Chest",
            "neck": "J_Bip_C_Neck",
            "head": "J_Bip_C_Head",
            "leftUpperLeg": "J_Bip_L_UpperLeg",
            "leftLowerLeg": "J_Bip_L_LowerLeg",
            "leftFoot": "J_Bip_L_Foot",
            "rightUpperLeg": "J_Bip_R_UpperLeg",
            "rightLowerLeg": "J_Bip_R_LowerLeg",
            "rightFoot": "J_Bip_R_Foot",
            "leftShoulder": "J_Bip_L_Shoulder",
            "leftUpperArm": "J_Bip_L_UpperArm",
            "leftLowerArm": "J_Bip_L_LowerArm",
            "leftHand": "J_Bip_L_Hand",
            "rightShoulder": "J_Bip_R_Shoulder",
            "rightUpperArm": "J_Bip_R_UpperArm",
            "rightLowerArm": "J_Bip_R_LowerArm",
            "rightHand": "J_Bip_R_Hand"
        },
        
        # Stretch naming convention
        "stretch": {
            "hips": "root",
            "spine": "spine_01",
            "chest": "spine_02",
            "neck": "neck",
            "head": "head",
            "leftUpperLeg": "thigh_stretch_l",
            "leftLowerLeg": "leg_stretch_l",
            "leftFoot": "foot_l",
            "rightUpperLeg": "thigh_stretch_r",
            "rightLowerLeg": "leg_stretch_r",
            "rightFoot": "foot_r",
            "leftShoulder": "shoulder_l",
            "leftUpperArm": "arm_stretch_l",
            "leftLowerArm": "forearm_stretch_l",
            "leftHand": "hand_l",
            "rightShoulder": "shoulder_r",
            "rightUpperArm": "arm_stretch_r",
            "rightLowerArm": "forearm_stretch_r",
            "rightHand": "hand_r"
        },
        
        # Mixamo naming convention
        "mixamo": {
            "hips": "mixamorig:Hips",
            "spine": "mixamorig:Spine",
            "chest": "mixamorig:Spine1",
            "upperChest": "mixamorig:Spine2",
            "neck": "mixamorig:Neck",
            "head": "mixamorig:Head",
            "leftUpperLeg": "mixamorig:LeftUpLeg",
            "leftLowerLeg": "mixamorig:LeftLeg",
            "leftFoot": "mixamorig:LeftFoot",
            "leftToes": "mixamorig:LeftToeBase",
            "rightUpperLeg": "mixamorig:RightUpLeg",
            "rightLowerLeg": "mixamorig:RightLeg",
            "rightFoot": "mixamorig:RightFoot",
            "rightToes": "mixamorig:RightToeBase",
            "leftShoulder": "mixamorig:LeftShoulder",
            "leftUpperArm": "mixamorig:LeftArm",
            "leftLowerArm": "mixamorig:LeftForeArm",
            "leftHand": "mixamorig:LeftHand",
            "rightShoulder": "mixamorig:RightShoulder",
            "rightUpperArm": "mixamorig:RightArm",
            "rightLowerArm": "mixamorig:RightForeArm",
            "rightHand": "mixamorig:RightHand"
        }
    }
    
    return mappings

# Detect naming convention based on bone names
def detect_naming_convention(bone_names):
    # Get all mapping types
    mappings = get_bone_mappings()
    
    # Dictionary to keep track of matches for each naming convention
    matches = {convention: 0 for convention in mappings.keys()}
    
    # Count matches for each naming convention
    for convention, mapping in mappings.items():
        for bone in mapping.values():
            if bone in bone_names:
                matches[convention] += 1
    
    # Find the naming convention with the most matches
    best_convention = max(matches.items(), key=lambda x: x[1])
    
    # If we found at least 3 matching bones, use that convention
    if best_convention[1] >= 3:
        return best_convention[0]
    
    # Special case for "standard" with Hips but not LeftUpLeg naming
    if "Hips" in bone_names and "Spine" in bone_names:
        # Check if it might be using left/right leg/arm instead of LeftLeg/RightLeg
        if "LeftLeg" not in bone_names and "Left Leg" in bone_names:
            return "standard_with_spaces"
        return "standard"
    
    # If we couldn't detect a specific convention, try a custom approach
    return "custom"

# Create bone mapping based on detected naming convention
def create_bone_mapping(bone_names):
    naming_convention = detect_naming_convention(bone_names)
    
    # Get all mapping types
    mappings = get_bone_mappings()
    
    # Initialize empty mapping
    mapping = {}
    
    # Handle standard naming conventions
    if naming_convention in mappings:
        for vrm_bone, source_bone in mappings[naming_convention].items():
            if source_bone in bone_names:
                mapping[vrm_bone] = source_bone
    
    # Handle standard with spaces
    elif naming_convention == "standard_with_spaces":
        for vrm_bone, source_bone in mappings["standard"].items():
            # Try with spaces
            spaced_bone = source_bone.replace("Left", "Left ").replace("Right", "Right ")
            if spaced_bone in bone_names:
                mapping[vrm_bone] = spaced_bone
    
    # Handle custom/unknown naming - try to guess based on common patterns
    else:
        # Try to find key bones through partial matches
        for bone in bone_names:
            lower_bone = bone.lower()
            
            # Skip common parent bones that aren't useful for VRM
            if bone in ["RL_BoneRoot", "Armature", "secondary", "root_x", "Armature_0"]:
                continue
                
            # Basic heuristics - try to map common patterns
            if "hip" in lower_bone or "pelvis" in lower_bone:
                mapping["hips"] = bone
            elif "spine" in lower_bone and not any(x in lower_bone for x in ["1", "2", "3"]):
                mapping["spine"] = bone
            elif "spine1" in lower_bone or "spine01" in lower_bone:
                mapping["chest"] = bone
            elif "spine2" in lower_bone or "spine02" in lower_bone:
                mapping["upperChest"] = bone
            elif "neck" in lower_bone and "twist" not in lower_bone:
                mapping["neck"] = bone
            elif "head" in lower_bone:
                mapping["head"] = bone
            
            # Left leg
            elif any(x in lower_bone for x in ["leftupleg", "left_upleg", "l_upleg", "thigh_l", "left_thigh"]):
                mapping["leftUpperLeg"] = bone
            elif any(x in lower_bone for x in ["leftleg", "left_leg", "l_leg", "leg_l"]):
                mapping["leftLowerLeg"] = bone
            elif any(x in lower_bone for x in ["leftfoot", "left_foot", "l_foot", "foot_l"]):
                mapping["leftFoot"] = bone
            
            # Right leg
            elif any(x in lower_bone for x in ["rightupleg", "right_upleg", "r_upleg", "thigh_r", "right_thigh"]):
                mapping["rightUpperLeg"] = bone
            elif any(x in lower_bone for x in ["rightleg", "right_leg", "r_leg", "leg_r"]):
                mapping["rightLowerLeg"] = bone
            elif any(x in lower_bone for x in ["rightfoot", "right_foot", "r_foot", "foot_r"]):
                mapping["rightFoot"] = bone
            
            # Left arm
            elif any(x in lower_bone for x in ["leftshoulder", "left_shoulder", "l_shoulder", "shoulder_l", "l_clavicle"]):
                mapping["leftShoulder"] = bone
            elif any(x in lower_bone for x in ["leftarm", "left_arm", "l_arm", "arm_l"]) and "fore" not in lower_bone:
                mapping["leftUpperArm"] = bone
            elif any(x in lower_bone for x in ["leftforearm", "left_forearm", "l_forearm", "forearm_l"]):
                mapping["leftLowerArm"] = bone
            elif any(x in lower_bone for x in ["lefthand", "left_hand", "l_hand", "hand_l"]):
                mapping["leftHand"] = bone
            
            # Right arm
            elif any(x in lower_bone for x in ["rightshoulder", "right_shoulder", "r_shoulder", "shoulder_r", "r_clavicle"]):
                mapping["rightShoulder"] = bone
            elif any(x in lower_bone for x in ["rightarm", "right_arm", "r_arm", "arm_r"]) and "fore" not in lower_bone:
                mapping["rightUpperArm"] = bone
            elif any(x in lower_bone for x in ["rightforearm", "right_forearm", "r_forearm", "forearm_r"]):
                mapping["rightLowerArm"] = bone
            elif any(x in lower_bone for x in ["righthand", "right_hand", "r_hand", "hand_r"]):
                mapping["rightHand"] = bone
    
    return mapping, naming_convention

# Process all JSON files
def process_json_files():
    json_files = glob.glob('*.json')
    stats = {"total": len(json_files), "successful": 0, "conventions": {}}
    
    for json_file in json_files:
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            # Extract the model name (filename without extension)
            model_name = os.path.splitext(json_file)[0]
            
            # Navigate to the collision shapes section to get bone names
            # First, get the model object key
            model_key = list(data.keys())[0]
            
            # Extract bone names from collision shapes
            collision_shapes = data[model_key]['Object'][model_key]['Physics']['Collision Shapes']
            bone_names = list(collision_shapes.keys())
            
            # Create bone mapping
            mapping, convention = create_bone_mapping(bone_names)
            
            # Keep stats
            stats["conventions"][convention] = stats["conventions"].get(convention, 0) + 1
            
            # Save mapping to out directory
            if mapping:  # Only save if mapping is not empty
                stats["successful"] += 1
                output_path = os.path.join('out', f"{model_name}_mapping.json")
                with open(output_path, 'w') as f:
                    json.dump(mapping, f, indent=4)
                
                print(f"Created mapping for {model_name} using {convention} convention")
            else:
                print(f"WARNING: Could not create mapping for {model_name} (detected as {convention})")
        
        except Exception as e:
            print(f"Error processing {json_file}: {str(e)}")
    
    print("\nProcessing summary:")
    print(f"Total JSON files: {stats['total']}")
    print(f"Successful mappings: {stats['successful']}")
    print("Naming conventions detected:")
    for convention, count in stats["conventions"].items():
        print(f"  - {convention}: {count} file(s)")

if __name__ == "__main__":
    process_json_files()
