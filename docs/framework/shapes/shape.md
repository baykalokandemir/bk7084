# framework/shapes/shape.py

## Overview
The base class for all geometric entities. It acts as a container for raw vertex data (Positions, Normals, Colors, UVs, Indices) and manages the upload of this data to the GPU via OpenGL Vertex Buffer Objects (VBOs) and Vertex Array Objects (VAOs).

## Changelog (Original vs. Current)
* **Added:** `createGeometry()` method. This is an empty placeholder method intended to be overridden by subclasses (like `Cube` or `Sphere`) to procedurally generate their vertex data on demand.
* **Modified:** `createBuffers()` now includes a safety check `if self.indices is not None` before attempting to access `.any()`. This prevents crashes if the index array is uninitialized (e.g., in point clouds without connectivity).
* **Antigravity/AI Note:** The addition of `createGeometry` supports the "Lazy Loading" pattern used in `MeshObject`. It allows the engine to define a shape object lightly and only generate the heavy vertex arrays right before the first draw call.

## Key Classes & Functions
### `Shape`
* `__init__()`: Initializes empty NumPy arrays for all vertex attributes.
* `createBuffers()`:
    * Generates a **VAO** (Vertex Array Object) to store the state.
    * Generates **VBOs** (Vertex Buffer Objects) for:
        * **Slot 0:** Position (vec4)
        * **Slot 1:** Normal (vec3)
        * **Slot 2:** Color (vec4)
        * **Slot 3:** UV (vec2)
    * **Index Buffer:** Generates an Element Array Buffer if indices exist.
* `delete()`: Frees the GPU memory by deleting all generated buffers.

## Dependencies
* **Libraries:** `numpy`, `OpenGL.GL`, `pyglm`.