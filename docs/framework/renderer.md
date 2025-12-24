# framework/renderer.py

## Overview
The central rendering engine. It manages the list of drawable objects and light sources. Every frame, it clears the screen, configures the global OpenGL state (Depth Testing), and iterates through every object to trigger its `draw()` method.

## Changelog (Original vs. Current)
* **Added:** `self.clear_color` property (defaulting to Black `[0,0,0,1]`). The original version hardcoded a White background.
* **Modified:** `render()` now uses `self.clear_color` instead of hardcoded values.
* **REMOVED (Critical):** `glfw.swap_buffers()` and `glfw.poll_events()` have been commented out at the end of `render()`.
* **Antigravity/AI Note:** This change effectively demotes `GLRenderer` from "The Game Loop" to just "A Drawing Tool". You must ensure that whatever code calls `renderer.render()` also handles the buffer swapping, otherwise the window will appear frozen.

## Key Classes & Functions
### `GLRenderer`
* `__init__(window, camera)`: Stores references to the window and the active camera.
* `addObject(obj)`: Adds an entity to the render queue.
    * **Safety Check:** Verifies that `obj` actually has a callable `draw()` method before adding it, preventing runtime crashes.
* `addLight(light)`: Adds a light source to the scene.
* `render()`:
    * Clears Color and Depth buffers.
    * Enables `GL_DEPTH_TEST` (ensuring close objects cover far objects).
    * Loops through `self.objects` and calls `o.draw(camera, lights)`.

## Dependencies
* **Internal:** `framework.window`, `framework.shapes`, `framework.light`.
* **Libraries:** `numpy`, `glfw`, `OpenGL.GL`.