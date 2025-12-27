# framework/materials/material.py

## Overview
A class that bridges Python objects and GLSL shaders. It manages the compilation of shader programs (both standard and instanced versions), stores material properties (ambient, diffuse, specular, shininess), and handles the binding of textures and uniforms before a draw call is issued.

## Changelog (Original vs. Current)
* **Added:** `self.uniforms` dictionary in `__init__`.
* **Added:** Logic in `set_uniforms()` to iterate over `self.uniforms` and upload custom values (float, int, bool, vec2, vec3, vec4, mat4) to the shader dynamically.
* **Antigravity/AI Note:** The custom uniform handling is a major improvement. It allows creating special effects (like the hologram or scrolling textures) without subclassing `Material` or hardcoding new variables for every single effect.

## Key Classes & Functions
### `Material`
* `__init__(vertex_shader, fragment_shader, color_texture)`:
    * Compiles two versions of the shader program: one normal, and one with `#define INSTANCED` (for use with `InstancedMeshObject`).
    * Sets default lighting values (Phong model coefficients).
* `set_uniforms(is_instanced, obj, camera, lights)`:
    * **Standard Uniforms:** Uploads View/Projection matrices, Light data (arrays of pos/color), and standard material properties.
    * **Texture Binding:** Binds `color_texture` to slot 0 if it exists.
    * **Custom Uniforms:** Checks `self.uniforms` and automatically detects the type (`float`, `glm.vec3`, etc.) to call the correct `glUniform*` function.

## Dependencies
* **Internal:** `framework.shaders.createShader`, `framework.Texture` (implicit import).
* **Libraries:** `OpenGL.GL`, `glm`, `numpy`.