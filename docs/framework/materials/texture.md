# framework/materials/texture.py

## Overview
A wrapper class for OpenGL textures. It handles loading images from disk (via Pillow/PIL), direct pixel manipulation (reading/writing specific pixels), and uploading the pixel data to the GPU. It implements a "dirty flag" system to ensure data is only re-uploaded to the GPU when changes are made.

## Changelog (Original vs. Current)
* **No Changes:** The file is identical to the original version.
* **Antigravity/AI Note:** The implementation is clean. The "dirty" flag logic in `bind()` is a good optimization, preventing unnecessary `glTexImage2D` calls (which are expensive) every frame.

## Key Classes & Functions
### `Texture`
* `__init__(resolution, data, file_path)`:
    * Can initialize from a file OR manually with a specific resolution and data array.
    * Defaults to a transparent black texture if no data is provided.
* `load_from_file(path)`:
    * Uses `PIL.Image` to open an image and convert it to RGBA format.
    * Stores the raw pixel data in `self.data` (NumPy array).
* `set_pixel(x, y, color)` / `get_pixel(x, y)`:
    * Allows CPU-side modification of the texture data. Sets `self.dirty = True` so the next render call updates the GPU.
* `upload()`:
    * Generates an OpenGL texture ID (if one doesn't exist).
    * Uploads `self.data` to the GPU using `glTexImage2D`.
    * Generates mipmaps and sets default filtering (Linear Mipmap Linear) and wrapping (Repeat).
* `bind(unit)`:
    * Activates the specified texture unit (e.g., `GL_TEXTURE0`).
    * Checks if `self.dirty` is true; if so, triggers an upload first.

## Dependencies
* **Libraries:** `OpenGL.GL`, `numpy`, `pyglm` (as `glm`), `PIL` (Pillow).