# framework/shapes/cube.py

## Overview
A concrete implementation of `Shape` that generates a standard Cube. It is constructed with "hard edges," meaning vertices are duplicated for each face. This ensures that lighting normals are perpendicular to each face (flat shading) and texture coordinates map correctly to each side.

## Changelog (Original vs. Current)
* **No Changes:** The file is identical to the original version.
* **Antigravity/AI Note:** The implementation is correct and standard. It manually defines the 24 vertices (4 vertices * 6 faces) required for a cube with distinct face normals and UV mappings.

## Key Classes & Functions
### `Cube(Shape)`
* `__init__(color, side_length)`: Sets parameters and calls `Shape.__init__`.
* `createGeometry()`:
    * **Vertices:** Generates 24 `vec4` positions.
    * **Normals:** specific `vec3` normal for each of the 6 faces (Front, Back, Top, Bottom, Right, Left).
    * **UVs:** Maps the full [0,1] texture range to each face, with rotation adjustments to ensure textures align correctly (e.g., "up" is always "up").
    * **Indices:** Defines two triangles per face to form the solid mesh.

## Dependencies
* **Internal:** `framework.shapes.shape`.
* **Libraries:** `pyglm`, `numpy`.