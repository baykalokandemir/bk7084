# framework/materials/shaders.py

## Overview
A low-level utility module responsible for the compilation pipeline of GLSL shaders. It reads source code from files, injects pre-processor macros (like `#define INSTANCED`) dynamically, compiles the Vertex and Fragment stages, and links them into a usable OpenGL Program ID.

## Changelog (Original vs. Current)
* **No Changes:** The file is identical to the original version.
* **Antigravity/AI Note:** The logic for injecting defines is robust. It correctly checks for the `#version` tag and ensures new definitions are inserted *after* it, preventing GLSL compilation errors (as `#version` must always be the first line).

## Key Classes & Functions
### `createShader(vtx_filename, frag_filename, defines)`
* Reads the shader source files from disk.
* **Define Injection:** If a list of `defines` is provided (e.g., `['INSTANCED']`), it injects them into the source code string immediately after the `#version` line.
* Calls `createShaderFromString` to finish the job.

### `createShaderFromString(vtx_source, frag_source)`
* **Compilation:** Creates and compiles `GL_VERTEX_SHADER` and `GL_FRAGMENT_SHADER` objects.
* **Error Handling:** checks `glGetShaderiv` for compile errors and raises a Python Exception with the GLSL error log if compilation fails.
* **Linking:** Attaches shaders to a Program and links them. Checks `glGetProgramiv` for link errors.
* **Cleanup:** Deletes the individual shader objects after linking (standard OpenGL practice).

## Dependencies
* **Libraries:** `OpenGL.GL`.