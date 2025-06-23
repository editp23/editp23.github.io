from pygltflib import GLTF2, Node
import numpy as np
import os

def rotate_matrix_x(angle_degrees):
    angle = np.deg2rad(angle_degrees)
    cos_a = np.cos(angle)
    sin_a = np.sin(angle)
    # 4x4 matrix flattened row-major
    return [
        1, 0,     0,    0,
        0, cos_a, -sin_a, 0,
        0, sin_a, cos_a, 0,
        0, 0,     0,    1
    ]

def process_and_save(src_path):
    glb = GLTF2().load(src_path)
    
    # Apply rotation to root nodes
    for node in glb.nodes:
        if node.matrix is None:
            node.matrix = rotate_matrix_x(-90)
        else:
            # Combine existing matrix with rotation
            existing = np.array(node.matrix).reshape((4,4))
            rot = np.array(rotate_matrix_x(-90)).reshape((4,4))
            combined = rot @ existing
            node.matrix = combined.flatten().tolist()

    # Build output path
    dir_name, file_name = os.path.split(src_path)
    name, ext = os.path.splitext(file_name)
    out_path = os.path.join(dir_name, f"{name}_rotated{ext}")
    
    glb.save(out_path)
    print(f"Saved rotated GLB: {out_path}")

def walk_and_rotate(base_dir):
    for root, _, files in os.walk(base_dir):
        for file in files:
            if file == "src.glb":
                src_path = os.path.join(root, file)
                process_and_save(src_path)

# Example: replace this with your base directory
base_directory = "/Users/roibar-on/Documents/Research/Multiview-editing/Data/website/recon"
walk_and_rotate(base_directory)
