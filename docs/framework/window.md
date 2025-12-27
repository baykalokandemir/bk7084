# framework/window.py

## Overview
A wrapper class around the GLFW library. It creates the operating system window, initializes the OpenGL context, and acts as the central hub for input processing. It captures raw keyboard and mouse events from GLFW and dispatches them to the active `Camera` instance.

## Changelog (Original vs. Current)
* **Added:** `toggle_mouse_capture()` method. This switches the cursor mode between `GLFW_CURSOR_NORMAL` (visible, moving freely) and `GLFW_CURSOR_DISABLED` (invisible, locked to window).
* **Modified:** `key_callback`:
    * Added logic to bind the **TAB** key to `toggle_mouse_capture()`.
* **Modified:** `cursor_pos_callback`:
    * Added a check for `self.mouse_capture`. If active, the camera moves even if the left mouse button isn't held down.
* **Antigravity/AI Note:** The implementation of mouse capture is clean. Resetting the camera mouse position (`self.camera.reset_mouse`) when re-capturing is a crucial detail that prevents the camera from "snapping" wildly when you tab back into the game.

## Key Classes & Functions
### `OpenGLWindow`
* `__init__(width, height, title)`: Initializes GLFW, creates the window, makes the context current, and binds all input callbacks.
* `toggle_mouse_capture()`:
    * Hides the cursor and locks it to the center of the screen (essential for FPS cameras).
    * Calls `camera.reset_mouse()` to sync the camera's internal state with the new cursor lock.
* **Callbacks (`key_callback`, `mouse_button_callback`, etc.):**
    * Standard event handlers that forward input data to `self.camera`.

## Dependencies
* **Libraries:** `glfw`, `OpenGL.GL`, `pyglm` (as `glm`).