# framework/shapes/car.py

## Overview
A procedural shape generator that creates a simplified low-poly vehicle. It constructs a rectangular prism for the chassis and instantiates four `Cylinder` shapes for the wheels. It handles the linear algebra required to rotate the wheels (aligning them to the X-axis) and positioning them relative to the body before merging all geometry into a single static mesh.

## Changelog (Original vs. Current)
* **New File:** This file did not exist in the original framework.
* **Antigravity/AI Note:**
    * This is a "CPU-side Mesh Merge". It effectively "bakes" the wheels into the car mesh. This means wheels cannot rotate independently during the game (unless the code is significantly changed to separate them into different objects).
    * It serves as a good example of how to combine multiple procedural primitives (`Cylinder` + Manual Quads) into one complex object.

## Key Classes & Functions
### `Car(Shape)`
* `__init__(body_color, wheel_color)`: Sets the colors for the different parts of the car.
* `createGeometry()`:
    * **Body Generation:** Manually defines the 8 vertices of a box and creates 6 faces (Quads) using a helper function `add_quad`.
    * **Wheel Generation:**
        1.  Instantiates a `Cylinder` object to generate the base wheel geometry.
        2.  Defines 4 mounting positions (`fl_pos`, `fr_pos`, etc.).
        3.  **Transformation Loop:** Iterates through each wheel position:
            * Creates a Model Matrix: `Translate(pos) * Rotate(90 deg, Z-axis)`.
            * Multiplies every vertex of the Cylinder by this matrix to move it into place.
            * Transforms normals using the `Normal Matrix` (Inverse Transpose) to ensure lighting remains correct after rotation.
            * Appends the transformed data to the main lists (`all_vertices`, `all_indices`, etc.).

## Dependencies
* **Internal:** `framework.shapes.shape`, `framework.shapes.cylinder`.
* **Libraries:** `pyglm`, `numpy`, `math`.