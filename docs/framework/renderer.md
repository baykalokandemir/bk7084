# framework/renderer.py

## Overview
The central rendering engine. It manages the list of drawable objects and light sources. Every frame, it clears the screen, configures the global OpenGL state (Depth Testing), and iterates through every object to trigger its `draw()` method.

## Changelog (Original vs. Current)
* **Added:** `self.clear_color` property (defaulting to Black `[0,0,0,1]`). The original version hardcoded a White background.
* **Added:** **Framebuffer Object (FBO)** support for Post-Processing. The renderer can now render the scene to a texture before displaying it.
* **Modified:** `render()` now uses `self.clear_color` instead of hardcoded values.
* **Modified:** `render()` logic updated to support both "Direct-to-Screen" and "Render-to-Texture" (Post-Process) modes.
* **REMOVED (Critical):** `glfw.swap_buffers()` and `glfw.poll_events()` have been commented out at the end of `render()`.
* **Antigravity/AI Note:** This change effectively demotes `GLRenderer` from "The Game Loop" to just "A Drawing Tool". You must ensure that whatever code calls `renderer.render()` also handles the buffer swapping, otherwise the window will appear frozen.

## Key Classes & Functions
### `GLRenderer`
* `__init__(window, camera)`: Stores references to the window and the active camera.
* `addObject(obj)`: Adds an entity to the render queue.
    * **Safety Check:** Verifies that `obj` actually has a callable `draw()` method before adding it, preventing runtime crashes.
* `addLight(light)`: Adds a light source to the scene.
* `init_post_process(width, height)`: Initializes the Framebuffer, Color Texture, and Renderbuffer (Depth/Stencil) for off-screen rendering. Compiles the `post_process` shader and sets up the fullscreen quad.
* `resize_post_process(width, height)`: Resizes the internal textures and buffers to match the new window dimensions. **Must be called in the window resize callback.**
* `render()`:
    * **Post-Process Mode:**
        1.  Binds the custom FBO.
        2.  Clears buffers & Renders Scene to Texture.
        3.  Binds default Framebuffer (Screen).
        4.  Renders Fullscreen Quad using `post_process` shader (applying Aberration).
    * **Standard Mode:**
        1.  Binds default Framebuffer.
        2.  Clears buffers & Renders Scene directly.
    * Enables `GL_DEPTH_TEST` (ensuring close objects cover far objects).
    * Loops through `self.objects` and calls `o.draw(camera, lights)`.

## Dependencies
* **Internal:** `framework.window`, `framework.shapes`, `framework.light`.
* **Libraries:** `numpy`, `glfw`, `OpenGL.GL`.