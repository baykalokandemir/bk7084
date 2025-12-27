# framework/shaders/mikoshi_shader

## Overview
A specialized shader pair for rendering volumetric point clouds. It replaces standard lighting with a "Data Visualization" aesthetic, using distance-based fading and density-based glowing to create a cyberpunk look.

## Vertex Shader (`mikoshi_shader.vert`)
### Key Features
* **Density Attribute:** It repurposes the standard `uv` input attribute. specifically `uv.x`, to carry **Density Data** instead of texture coordinates. This allows the generator to "tag" certain points (like corners or edges) as being "dense," which the fragment shader then renders as brighter.
* **Point Size Attenuation:**
    * Calculates `dist_to_cam` (distance from camera to vertex).
    * Sets `gl_PointSize` inversely proportional to distance (`10.0 / dist`). This simulates perspective for individual points—points further away appear smaller.
    * **Clamp:** Constrains point size between 1.0 and 2.0 pixels to prevent aliasing artifacts.

## Fragment Shader (`mikoshi_shader.frag`)
### Key Features
* **Point Shaping:**
    * Uses `gl_PointCoord` (a built-in variable for point primitives) to discard pixels outside a circular radius. This renders points as **circles** instead of the default squares.
    * Controlled by the `is_point_mode` uniform to prevent accidental holes if used on solid meshes.
* **Color Palettes:**
    * **Base:** Interpolates between a **Deep Blue** (shadow/far) and the user-defined `base_color` (usually Cyan) based on proximity to the camera.
* **Glow Logic:**
    * If `enable_glow` is true, it uses the passed `v_density` value.
    * **Magenta Tint:** Adds `vec3(0.2, 0.0, 0.1)` scaled by density.
    * **Hot Core:** If density is very high, it adds pure white (`hot_white`), making the densest clusters of points appear to "burn" with intensity.

## Dependencies
* **Uniforms:** `enable_glow`, `is_point_mode`, `base_color`.
* **Attributes:** `uv.x` (Must be populated with density data by the geometry generator).