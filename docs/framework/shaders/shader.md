# framework/shaders/shader.vert

## Overview
The default Vertex Shader. It is responsible for transforming 3D vertex positions from Model Space to Clip Space (via the Model-View-Projection matrix stack). It also handles the transformation of normals (using the Inverse Transpose matrix to preserve orthogonality) and passes interpolated data (UVs, Colors, World Position) to the fragment shader.

## Changelog (Original vs. Current)
* **No Changes:** The file is identical to the original version.
* **Antigravity/AI Note:** The shader supports a pre-processor directive `#ifdef INSTANCED`. This allows the same shader file to be compiled twice by the `Material` class—once for standard objects and once for `InstancedMeshObject` (where the Model matrix comes from a vertex attribute rather than a uniform).

## Key Logic
### Inputs
* `layout(location = 0) in vec4 in_position;`
* `layout(location = 1) in vec3 in_normal;`
* `layout(location = 2) in vec4 in_color;`
* `layout(location = 3) in vec2 in_uv;`
* **Instanced Inputs:** Locations 4 and 8 are reserved for per-instance Model matrices and Colors.

### Main Function
* **Model Matrix Selection:**
    * If `INSTANCED` is defined: `M = model * in_instance_model` (allows global transform * local instance transform).
    * Otherwise: `M = model`.
* **Normal Transformation:**
    * `normal_matrix = transpose(inverse(M))`
    * This is critical for correct lighting when objects are non-uniformly scaled. If we just multiplied normals by `M`, they would get skewed.
* **Position:** `gl_Position = projection * view * M * in_position`.

## Dependencies
* **Uniforms:** `view`, `projection`, `model`.

# framework/shaders/shader.frag

## Overview
The default Fragment Shader implementing the Blinn-Phong lighting model. It calculates ambient, diffuse, and specular reflections. 

**Critical Update:** The new version includes hardcoded logic to differentiate between "Sun" lighting (Global) and "Street Light" lighting (Local Spotlights), as well as a "hack" to make certain objects glow.

## Changelog (Original vs. Current)
* **Added:** **"Emissive Hack"**: Lines checking if `frag_color` is bright yellow (`>0.95, >0.95, >0.75`). If so, the shader skips lighting calculations and outputs the raw color. This is likely used for the light bulbs inside the street lamps to make them look bright.
* **Added:** **Distance Calculation**: Now calculates `length(light_pos - frag_pos)` for attenuation.
* **Added:** **Light differentiation**:
    * **Light Index 0:** Treated as the Sun/Moon. No attenuation, affects everything equally.
    * **Light Index > 0:** Treated as Street Lights.
        * **Attenuation:** Quadratic falloff (`1.0 / (1.0 + 0.1*d + 0.05*d^2)`).
        * **Spotlight Effect:** Hardcoded to point **DOWN** (`0, -1, 0`). Light strictly falls within a specific cone (cutoff 0.5).

## Key Logic
### Blinn-Phong Model

* Calculates the Half-Vector ($H$) between the Light direction ($L$) and View direction ($V$) to approximate specular highlights efficiently.

### Street Light Logic (New)
* **Attenuation:** Prevents lights from shining infinitely far.
* **Spotlight:** Uses `smoothstep` between `outerCutOff` (0.3) and `cutOff` (0.5) to create a soft-edged cone of light pointing downwards. This prevents street lights from illuminating the sky or roofs above them.

## Dependencies
* **Uniforms:** `light_position[]`, `light_color[]`, `ambient_strength`, `specular_strength`, `texture_scale`.
* **Textures:** `albedo_texture_sampler` (optional via defines).