# framework/shaders/slice_shader

## Overview
A special effects shader that renders geometry as a series of floating, non-physical slices. It uses the `discard` keyword in the fragment shader to transparency-cull pixels that fall between the defined "slice bands," creating a sci-fi hologram aesthetic.

## Vertex Shader (`slice_shader.vert`)
### Key Logic
* **World Space Pass-through:** Unlike standard shaders that often do lighting in View Space, this shader explicitly passes the **World Space Position** (`world_pos`) to the fragment shader. This is required because the slicing effect needs to be consistent across the object's actual location in the scene, regardless of camera angle.

## Fragment Shader (`slice_shader.frag`)
### Key Logic
* **The "Discard" Mechanic:**
    * The core logic relies on the Modulo operator (`mod`).
    * It calculates the distance of the current pixel along a specific axis (`slice_normal`).
    * `d_mod = mod(dist, slice_spacing)` creates a repeating saw-tooth pattern.
    * `if (d_mod > slice_thickness) discard;` deletes any pixel that isn't within the thin "thickness" band of the pattern.
* **Warp / Glitch Effect:**
    * Before calculating the slice, it adds a sine wave offset based on the X and Z coordinates:
    * `dist += sin(world_pos.x * 10.0 + world_pos.z * 10.0) * warp_factor;`
    * This bends the perfect planes into wavy, interference-like patterns, making the hologram look imperfect or "glitchy."
* **Animation:**
    * Adds `slice_offset` to the distance calculation. Changing this value frame-by-frame makes the scanlines move across the object.

## Dependencies
* **Uniforms:** `slice_spacing`, `slice_thickness`, `slice_normal` (axis), `warp_factor` (distortion), `slice_offset` (animation), `color`.