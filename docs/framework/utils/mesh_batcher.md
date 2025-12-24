# framework/utils/mesh_batcher.py

## Overview
A geometry optimization tool that combines multiple individual `Shape` objects into a single large `Shape`. It manually transforms vertices and normals on the CPU (using NumPy) to apply the object's position/rotation/scale before merging. This effectively reduces the number of draw calls from $N$ to $1$.

## Key Classes & Functions
### `MeshBatcher`
* `__init__()`: Initializes buffers for collecting geometry data.
* `add_shape(shape, transform, color)`:
    * **CPU Transformation:**
        * Applies the `transform` matrix to the shape's vertices ($V_{new} = V \times M$).
        * Applies the **Normal Matrix** (Inverse Transpose) to the shape's normals to ensure lighting remains correct even if the object is scaled non-uniformly.
    * **Color Override:** Optionally replaces the shape's vertex colors (useful for theming batches).
    * **Index Management:** Adds `index_offset` to the shape's indices. This ensures that the indices of the second shape point to the vertices of the second shape, not the first.
* `build(material)`:
    * Concatenates all collected NumPy arrays into one massive set of buffers.
    * Uploads the combined data to the GPU via `shape.createBuffers()`.
    * Returns a single `MeshObject` ready for rendering.

## Dependencies
* **Internal:** `framework.objects.MeshObject`, `framework.shapes.Shape`.
* **Libraries:** `numpy`, `OpenGL.GL`, `pyglm`.