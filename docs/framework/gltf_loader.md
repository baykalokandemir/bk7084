# framework/gltf_loader.py

## Overview
A dedicated loader utility that imports 3D models in the GLTF 2.0 (or binary .GLB) format. It parses the file using `pygltflib`, extracts the binary geometry data (vertices, normals, UVs, indices), and converts them into the engine's native `MeshObject` and `Shape` structures.

## Changelog (Original vs. Current)
* **New File:** This file did not exist in the original version.
* **Antigravity/AI Note:**
    * **Hierarchy Warning:** The loader iterates through nodes linearly. It **ignores the scene hierarchy**. If a mesh is a child of another node in the GLTF file, the parent's transformation will be ignored, and the mesh will appear at the wrong position. It only respects the local transform of the mesh node itself.
    * **Data Conversion:** It correctly handles the conversion of GLTF 3-component vectors (x, y, z) into the engine's 4-component format (x, y, z, 1.0) for vertices.

## Key Classes & Functions
### `load_gltf(filepath, material)`
* **Input:** Path to a `.gltf` or `.glb` file.
* **Process:**
    * Uses `pygltflib` to parse the JSON structure.
    * **`get_data` Helper:** Handles the complexity of reading binary buffers. It supports both embedded buffers (Data URIs starting with `data:application/octet-stream...`) and external `.bin` files.
    * **Geometry Extraction:** loops through every mesh primitive and extracts:
        * `POSITION`: Converted to `vec4`.
        * `NORMAL`: Kept as `vec3`.
        * `TEXCOORD_0`: Kept as `vec2`.
        * `INDICES`: Flattened to a generic array.
    * **Transform parsing:** Reads the node's transformation. It handles both explicit 4x4 matrices and TRS (Translation, Rotation, Scale) properties.
        * *Note:* It correctly maps GLTF quaternion order (x, y, z, w) to `glm.quat` constructor order (w, x, y, z).
* **Output:** Returns a list of `MeshObject` instances ready to be added to the scene.

## Dependencies
* **External Library:** `pygltflib`.
* **Internal:** `framework.shapes.shape`, `framework.objects.mesh_object`.
* **Libraries:** `numpy`, `base64`, `os`, `pyglm`.