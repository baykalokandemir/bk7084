# framework/shaders/hologram.frag

## Overview
A specialized fragment shader for rendering 2D textures with a "Cyberpunk Screen" aesthetic. It ignores the original colors of the texture, converting them to grayscale luminance, and then re-colors the result using a single uniform (`hologram_color`). It overlays procedural vertical strips and moving horizontal scanlines to simulate digital interference.

## Changelog (Original vs. Current)
* **New File:** This file is unique to the "Antigravity" version. It is likely used for the animated billboards or floating screens in the city environment.

## Key Logic
### 1. UV Manipulation (Zoom/Pan)
* **Interactive Control:** Allows the texture to be scaled (`uv_scale`) and offset (`uv_offset`) at runtime.
* **Clipping:** Explicitly discards pixels outside the 0.0-1.0 UV range. This is crucial when "zooming out" on a texture so that it doesn't repeat infinitely (unless repeating is desired, but this shader forces a hard crop).

### 2. Luminance Extraction
* `dot(tex_color.rgb, vec3(0.299, 0.587, 0.114))`
* Converts the colorful input texture into a single brightness value. This allows the user to force the hologram to be any color (e.g., pure Cyan or pure Magenta) regardless of the source image colors.

### 3. Procedural Effects
* **Vertical Strips:** Uses `sin(uv.x * frequency)` to create vertical bars.
    * **Duty Cycle:** The `lines_thickness` uniform controls how wide the visible bars are versus the empty gaps.
* **Scanline Animation:** Uses `sin(uv.y - time)` to create a subtle horizontal wave that scrolls down the screen, simulating a CRT refresh rate or transmission artifact.

### 4. Alpha Composition
* `alpha = brightness * strips * scanline`
* This creates an **Additive Blending** look. Dark areas of the original image become fully transparent. Bright areas become colored and opaque, but are periodically cut out by the scanlines.

## Dependencies
* **Uniforms:** `hologram_color`, `time`, `lines_frequency`, `lines_thickness`, `uv_scale/offset`.
* **Samplers:** `texture_sampler`.