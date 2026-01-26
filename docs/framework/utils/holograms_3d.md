# Documentation: Holograms3D

**File**: `framework/utils/holograms_3d.py`  
**Class**: `Holograms3D`

## Overview
The `Holograms3D` class is a high-level manager that consolidates **Procedural Generation (L-Systems)**, **Point Cloud Rendering (Holograms)**, and **Animation Logic** into a single cohesive unit. It allows a Scene Manager to easily instantiate complex, animated hologram clusters without managing individual agents or geometries manually.

## Core Responsibilities
1.  **L-System Generation**: Uses `LSystem` to generate a string of rules and interpret them into 3D transforms.
2.  **Geometry Creation**:
    *   **Hologram Mode**: Converts standard shapes (Cube, Sphere, etc.) into Grid Point Clouds using `GridPointCloudGenerator`.
    *   **Solid Mode**: Falls back to standard mesh rendering with a "Slice" shader effect.
3.  **Animation**:
    *   **Group Rotation**: Rotates the entire cluster around a central axis.
    *   **Individual Rotation**: Spins every object on its own random axis.
4.  **Uniform Management**: updates shader uniforms (glow, color, time) each frame.

## Class API

### `__init__(self, root_position=glm.vec3(0, -1.0, 0))`
Initializes the manager.
*   `root_position`: The center of the group rotation in World Space.

### `regenerate(self, config)`
Rebuilds the entire visual scene based on the provided configuration object.
*   **Process**:
    1.  Clears existing objects.
    2.  Instantiates an `LSystem` with rules/angles from `config`.
    3.  Generates the L-System string and transforms.
    4.  Iterates through transforms and creates `MeshObject` instances (either Point Cloud or Solid).
    5.  Assigns random rotation speeds/axes to each new object.

### `update(self, dt)`
Advances the animation state. Should be called once per frame.
*   **Logic**:
    1.  Increments `group_rotation` by `group_speed * dt`.
    2.  Calculates `group_parent_transform`.
    3.  Iterates through all internal objects:
        *   Updates individual spin angle.
        *   Calculates `Local = Initial_LSystem_Pos * Spin_Rotation`.
        *   Calculates `Final = Group_Parent * Local`.
        *   Applies `Final` to `obj.transform`.

### `update_uniforms(self, config, time)`
Updates shader uniforms for visual effects.
*   **Parameters**:
    *   `config`: Source of color, glow, and size settings.
    *   `time`: Accumulated application time (for shader animations).
*   **Effects**:
    *   Updates `base_color`, `point_size`, `enable_glow`, and `time` on all hologram materials.

### `_create_hologram_object(self, source_shape, spacing, color, transform)` (Private)
Helper method to generate a Point Cloud MeshObject.
1.  Calls `GridPointCloudGenerator.generate`.
2.  Creates a unique `Material` instance using `mikoshi_shader`.
3.  Sets default uniforms (`is_point_mode=True`, `anim_x=True`, etc.).
4.  Returns the configured `MeshObject` with `draw_mode=gl.GL_POINTS`.

## Dependencies
*   `framework.utils.l_system`: For procedural structure generation.
*   `framework.utils.grid_point_cloud_generator`: For converting meshes to points.
*   `framework.objects`: `MeshObject` base class.
*   `framework.materials`: `Material` class.
*   `OpenGL.GL`, `pyglm`: Graphics and Math libraries.
