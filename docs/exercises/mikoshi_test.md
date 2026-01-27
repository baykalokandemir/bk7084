# Documentation: mikoshi_test.py

## Overview
`mikoshi_test.py` serves as the main entry point and testbed for the **Hologram L-System Simulation**. It sets up the OpenGL rendering context, initializes the hologram system, and manages the main game loop including UI interaction and scene updates.

## Key Components

### 1. Configuration (`Config` Class)
The `Config` class acts as a central repository for all tunable parameters. It is modified dynamically via the ImGui interface.

*   **L-System Parameters**:
    *   `L_ITERATIONS`: recursive depth of generation.
    *   `L_SIZE_LIMIT`: maximum number of segments/shapes to generate.
    *   `L_LENGTH`, `L_ANGLE_MIN`, `L_ANGLE_MAX`: Geometric properties of the L-System structure.
*   **Hologram Settings**:
    *   `GRID_SPACING`: Density of the point cloud generation.
    *   `POINT_SIZE`: Visual size of hologram points in the shader.
    *   `POINT_CLOUD_COLOR`: Base RGB color.
    *   `ENABLE_GLOW`: Toggles the shader glow effect.
    *   `USE_POINT_CLOUD`: Switch between point-cloud mode and solid/wireframe mode.
*   **Post-Processing**:
    *   `USE_ABERRATION`, `ABERRATION_STRENGTH`: Chromatic aberration effects.
    *   `USE_BLUR`, `BLUR_STRENGTH`: Gaussian blur effects.

### 2. Scene Management (`SceneManager` Class)
The `SceneManager` abstracts the specific entities in the scene.

*   **Responsibility**: It holds the instance of `Holograms3D` (the core logic class).
*   **`generate_scene(config)`**: Calls `holograms.regenerate(config)` to rebuild the L-System and point clouds when parameters change.
*   **`update_uniforms(config, dt)`**:
    *   Updates the animation time (`accum_time`).
    *   Calls `holograms.update(dt)` for physics/rotation calculation.
    *   Propagates config changes (colors, sizes) to the shaders via `holograms.update_uniforms`.

### 3. Main Loop (`main()` Function)
The `main()` function handles the lifecycle of the application:
1.  **Initialization**:
    *   Creates `OpenGLWindow`.
    *   Sets up `Flycamera`.
    *   Initializes `GLRenderer` and post-processing buffers.
    *   Initializes `ImGui` context and GLFW callbacks.
2.  **Loop Execution**:
    *   **Input**: Processes keyboard/mouse input via `GlfwRenderer`.
    *   **UI Rendering**: Calls `ui_manager.render(...)` to draw the control panel.
    *   **Update**: Advances the simulation state via `scene_manager.update_uniforms(...)`.
    *   **Render**: Calls `glrenderer.render()` to draw the scene to the screen (or FBO).
3.  **Cleanup**: Properly shuts down GLFW and ImGui contexts on exit.

## Usage
Run the file directly to launch the simulation:
```bash
python exercises/mikoshi_test.py
```
Interact with the GUI window to tweak generation parameters in real-time. Click "Regenerate" to apply structural L-System changes.
