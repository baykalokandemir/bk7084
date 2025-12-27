# framework/shaders/post_process

## Overview
The `post_process` shader pair implements full-screen effects applied after the 3D scene has been rendered to a texture. Currently, it implements **Chromatic Aberration**.

## Vertex Shader (`post_process.vert`)
A simple "pass-through" shader that renders a full-screen quad.
*   **Input:** `vec2 position`, `vec2 texCoords`.
*   **Output:** `vec2 TexCoords`.
*   **Logic:** Passes positions directly (in NDC, -1 to 1) and texture coordinates to the fragment shader.

## Fragment Shader (`post_process.frag`)
Implements the visual effect logic.

### 1. Chromatic Aberration
Simulates a lens failing to focus all colors to the same point.
*   **Uniforms:**
    *   `sampler2D screenTexture`: The texture containing the rendered 3D scene.
    *   `float aberration_strength`: The distance (in UV space) to offset the color channels.
*   **Logic:**
    *   Calculates a `direction` vector from the center of the screen to the current pixel.
    *   **Red Channel:** Sampled at `uv + direction * strength`.
    *   **Green Channel:** Sampled at `uv` (center).
    *   **Blue Channel:** Sampled at `uv - direction * strength`.
    *   This creates a radial color split that increases towards the edges of the screen.

### 2. Blur
A simple adjustable blur effect.
*   **Uniforms:**
    *   `float blur_strength`: Controls the radius of the blur sample kernel.
*   **Logic:**
    *   Implements a 9-tap Box Blur (samples a 3x3 grid around the pixel).
    *   The distance between samples is scaled by `blur_strength`.
    *   If combined with Chromatic Aberration, the aberration offset is applied to each sample.
