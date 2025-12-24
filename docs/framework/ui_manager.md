# framework/ui_manager.py

## Overview
This file handles the Immediate Mode GUI (ImGui) overlay. It renders a control window titled "Mikoshi Controls" that allows the user to tweak generation settings, load 3D models, and adjust shader parameters (colors, slice thickness, glow) at runtime. It acts as the bridge between the user and the `Config` object.

## Changelog (Original vs. Current)
* **New File:** This file did not exist in the original version. It was added to provide real-time control over the new procedural generation features.
* **Antigravity/AI Note:**
    * The UI logic is robust but tightly coupled. Inside the "Load / Regenerate" button logic, the UI Manager directly wipes `renderer.objects` and refills it. In a stricter architecture, the UI would emit an event, and the SceneManager would handle the cleanup.
    * **Color Logic:** The file includes specific logic to synchronize "Hue" sliders with "RGB" color pickers using `colorsys`, ensuring that changing one updates the other smoothly.

## Key Classes & Functions
### `UIManager`
* `render(config, scene_manager, renderer)`:
    * Draws the ImGui window.
    * **Generation Section:** Controls for Point Count, Sampling Mode (Random/Grid), and GLTF scaling.
    * **Model Loading:** A text field to input a path to a `.gltf` file.
        * **"Load / Regenerate" Button:** Triggers `scene_manager.generate_scene(config)` and immediately replaces the render queue (`renderer.objects`) with the new result.
    * **Slice Shader Section:** Sliders for controlling the "Hologram" effect (spacing, thickness, warp, animation speed).
    * **Visuals Section:** Controls for the "Glow" effect and Color Pickers.

## Dependencies
* **External:** `imgui` (Python bindings for cimgui), `colorsys`.