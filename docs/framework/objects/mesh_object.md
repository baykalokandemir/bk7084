# framework/objects/mesh_object.py

## Overview
A concrete implementation of `Object` that represents a 3D mesh with a material. It handles the OpenGL rendering calls, including binding Vertex Array Objects (VAOs), managing transparency/blending settings, and issuing the final draw commands (supporting both triangles and points).

## Changelog (Original vs. Current)
* **Added:** `draw_mode` parameter in `__init__` (allows rendering as `GL_POINTS`, `GL_LINES`, etc., instead of just `GL_TRIANGLES`).
* **Added:** `enable_blending` and `blend_func` parameters in `__init__` to support transparent objects.
* **Modified:** `draw()` method now:
    * Enables/Disables `GL_BLEND` based on object settings.
    * Enables/Disables `GL_PROGRAM_POINT_SIZE` if drawing points.
    * Uses `self.draw_mode` in draw calls instead of hardcoded `GL_TRIANGLES`.
* **Antigravity/AI Note:**
    * The `draw()` method contains lengthy, conversational comments (e.g., "For Mikoshi style...", "But usually point clouds...") debating how to handle indices with points. These explain the logic but are verbose code clutter.
    * There are commented-out lines regarding `glDepthMask` that seem to be leftover experiments.

## Key Classes & Functions
### `MeshObject(Object)`
* `__init__(mesh, material, transform, draw_mode, enable_blending, blend_func)`:
    * Extends `Object`.
    * Stores rendering state (blending mode, primitive type) alongside the mesh and material.
* `draw(camera, lights)`:
    * Binds the shader/material uniforms.
    * Lazily initializes mesh geometry (VAO/VBO) if not already created.
    * Configures OpenGL state (Blending, Point Size).
    * Executes `glDrawElements` (if indices exist) or `glDrawArrays` using the specified `draw_mode`.

## Dependencies
* **Internal:** `framework.objects.object` (Base class `Object`).
* **Libraries:** `pyglm` (as `glm`), `OpenGL.GL` (as `gl`).