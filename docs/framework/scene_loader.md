# framework/scene_loader.py

## Overview
**Note:** Despite the name, this file functions as a **GLTF Exporter**. It iterates through the objects in the `Renderer`, packs their geometry (vertices, normals, indices) and transformation matrices into the GLTF 2.0 standard format, and saves the result to disk as a `.gltf` (JSON) and `.bin` (Binary) pair.

## Changelog (Original vs. Current)
* **No Changes:** The file is identical to the original version.
* **Antigravity/AI Note:** The implementation is a standard use of the `pygltflib` library. It correctly handles the complex task of padding binary data (aligning to 4 bytes) and setting up BufferViews/Accessors, which is often where manual GLTF export code fails.

## Key Classes & Functions
### `export_scene(renderer, filepath="scene.gltf")`
* The main entry point. Accepts the `GLRenderer` instance and a target file path.
* Initializes a blank `GLTF2` container.
* Loops through `renderer.objects` and calls `_pack_mesh` and `add_node` for each.
* **Instancing Support:** If an object has a `transforms` list (like `InstancedMeshObject`), it correctly creates multiple GLTF Nodes sharing the same Mesh, preserving the optimization in the exported file.
* Saves the JSON structure and writes the binary blob to a separate `.bin` file.

### Internal Helpers
* `_pack_mesh(gltf, mesh_obj)`: Converts the raw numpy arrays from your `Mesh` class into GLTF Accessors and BufferViews.
* `_append_blob(gltf, data, target)`: Appends raw byte data to the global binary buffer, ensuring 4-byte alignment.
* `_matrix_from(obj)`: Extracts the 4x4 transformation matrix from an object, flattening it into a 16-float list required by GLTF.

## Dependencies
* **External Library:** `pygltflib` (Required for constructing the GLTF hierarchy).
* **Libraries:** `numpy`, `pathlib`.