# framework/light.py

## Overview
A simple data container representing a Point Light in the scene. It holds the spatial position and RGB color intensity, which are later passed to the shaders by the `Renderer` to calculate lighting (diffuse/specular).

## Changelog (Original vs. Current)
* **No Changes:** The file is identical to the original version.
* **Antigravity/AI Note:** Currently, this class has no logic, just data. It relies entirely on the shader implementation to determine falloff, attenuation, or range (which seem to be hardcoded or non-existent in the current shader code based on the `Material` class we reviewed earlier).

## Key Classes & Functions
### `PointLight`
* `__init__(pos, color)`:
    * `pos`: A `glm.vec3` or `glm.vec4` representing the light's world-space position.
    * `color`: A `glm.vec3` or `glm.vec4` representing the light's color (and intensity, if values > 1.0).

## Dependencies
* **Libraries:** `pyglm` (as `glm`).