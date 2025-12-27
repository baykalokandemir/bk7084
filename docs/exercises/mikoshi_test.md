# exercises/mikoshi_test.py

## Overview
The executable entry point for the "Mikoshi" Point Cloud Demo. It functions as the **Game Loop**, integrating the 3D engine with the 2D ImGui control panel. It is responsible for initialization, input handling (routing events to UI vs. Camera), and orchestrating the frame update cycle.

## Key Logic
### 1. Configuration State (`Config`)
A static class acting as a central state store. It holds all the tweakable parameters:
- **Generation:** Point Count, Sampling Mode.
- **Point Settings:** Base Size, Shape (Circle/Square).
- **Animation:** Resize Horizontal/Vertical (Pulsing effect).
- **Visuals:** Colors, Glow Strength.

### 2. Input Handling (Callback Wrappers)
* **Problem:** We need to click buttons on the UI without moving the 3D camera.
* **Solution:** Wraps the standard GLFW callbacks.
    * `if not imgui.get_io().want_capture_mouse:` -> Only pass clicks to the Camera if the UI isn't using them.

### 3. The Render Loop
* **Step 1: UI Logic:** `ui_manager.render()` draws the sliders and buttons, updating the `Config` object in real-time.
* **Step 2: Scene Update:** `scene_manager.update_uniforms()` reads the `Config` and pushes the new values (e.g., Slice Offset, Glow Strength) to the active shaders.
* **Step 3: Draw 3D:** `glrenderer.render()` draws the scene to the back buffer.
* **Step 4: Draw UI:** `impl.render()` draws the ImGui interface on top of the 3D scene.
* **Step 5: Swap:** `glfw.swap_buffers()` displays the final frame.

## Dependencies
* **Framework:** `SceneManager`, `UIManager`, `GLRenderer`, `Camera`.
* **Libraries:** `imgui`, `glfw`, `OpenGL`.