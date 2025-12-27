# framework/objects/instanced_mesh_object.py

## Overview
A specialized object class designed for high-performance rendering of many identical meshes (e.g., a forest of trees or a city of buildings). Instead of issuing a draw call for every single object, it groups them and uses OpenGL "Instancing" to draw thousands of copies in a single call. It manages extra Vertex Buffer Objects (VBOs) to store per-instance data like transformation matrices and colors.

## Changelog (Original vs. Current)
* **No Changes:** The file is identical to the original version.
* **Antigravity/AI Note:** The implementation is standard and efficient. It correctly uses `glVertexAttribDivisor` to pass unique matrices and colors to the shader for each instance.

## Key Classes & Functions
### `InstancedMeshObject(Object)`
* `__init__(mesh, material, transforms, colors)`:
    * Prepares the object for instancing. Requires a list of `transforms` (matrices) and optional `colors`.
* `_create_instance_buffers()`:
    * **Crucial Logic:** This function packs the 4x4 transformation matrices into a generic VBO. Since OpenGL attributes are max vec4, it splits the matrix into 4 separate attribute locations (4, 5, 6, 7).
    * Sets up the Attribute Divisor to `1` (telling OpenGL to advance these attributes once per *instance*, not per *vertex*).
* `update_transforms(transforms)` & `update_colors(colors)`:
    * Allows updating the position/color of all instances dynamically by re-uploading data to the GPU buffer (`glBufferSubData`).
* `draw(camera, lights)`:
    * Calls `glDrawElementsInstanced` or `glDrawArraysInstanced`.
    * Passes `True` to `material.set_uniforms` to signal the shader that instancing is active.

## Dependencies
* **Internal:** `framework.objects.object`
* **Libraries:** `numpy`, `OpenGL.GL`, `ctypes`.