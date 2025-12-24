# framework/camera.py

## Overview
This file defines the camera system for the engine. It provides an abstract base `Camera` class and two concrete implementations:
1.  **Trackball:** An orbital camera that rotates around a center point (useful for inspecting objects). It includes a visual "gizmo" (RGB axis lines) to visualize its orientation.
2.  **Flycamera:** A First-Person Shooter (FPS) style camera that allows free movement through the scene using WASD keys and mouse look.

## Changelog (Original vs. Current)
* **Modified:** `Flycamera` input handling was completely rewritten.
    * **Old:** Moved the camera *inside* the `key_press` event (resulting in jerky movement dependent on keyboard repeat rate).
    * **New:** `key_press` and `key_release` now only toggle boolean flags in a `self.keys` dictionary. Actual movement happens in a new `update(dt)` method.
* **Added:** `Flycamera.update(dt)` method. This calculates movement based on `dt` (delta time), ensuring smooth, frame-rate independent rendering.
* **Added:** `reset_mouse(x, y)` method to both `Camera` (abstract) and `Flycamera` (implementation). This prevents the camera from "jumping" when the mouse is re-captured by the window.
* **Antigravity/AI Note:** The changes to `Flycamera` are a massive improvement. The introduction of `dt` (delta time) means the camera won't speed up if the game runs at high FPS, or slow down at low FPS.

## Key Classes & Functions
### `Camera` (Base Class)
* `compute_projection_matrix()`: Calculates the perspective projection matrix based on FOV and aspect ratio.
* `rotate/scroll/draw`: Abstract methods.

### `Trackball(Camera)`
* **Math:** Uses a "project to sphere" algorithm. It maps 2D mouse coordinates to a virtual 3D sphere to calculate rotation quaternions/matrices.
* `draw()`: Unlike a normal camera, this class can render itself (a visual axis gizmo) if needed for debugging.


### `Flycamera(Camera)`
* **Math:** Uses Euler Angles (Pitch/Yaw) to calculate the `front`, `up`, and `right` vectors.

* `update(dt)`: **Critical.** Must be called every frame. It checks the state of W/A/S/D keys and updates `self.position` by `speed * dt`.

## Dependencies
* **Libraries:** `pyglm` (as `glm`), `glfw` (for key codes), `framework.materials.shaders`.