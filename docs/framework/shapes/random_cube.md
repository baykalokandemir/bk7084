# framework/shapes/random_cube.py

## Overview
A procedural shape generator that creates a "Cloud Cube"—a volume defined not by solid triangles, but by thousands of individual points scattered on its surface. It supports two modes of generation: purely random noise (for a glitchy data look) or a structured grid (for a scanner look).

## Changelog (Original vs. Current)
* **New File:** This file did not exist in the original framework. It was added specifically for the "Mikoshi" point cloud demo.
* **Antigravity/AI Note:** The logic is clean. It essentially treats the cube as 6 separate 2D planes and scatters points across them. The `indices` are explicitly set to `None`, enforcing that this shape cannot be drawn with `GL_TRIANGLES`.

## Key Classes & Functions
### `RandomCube(Shape)`
* `__init__(side_length, point_count, mode)`:
    * `mode='random'`: Distributes points stochastically.
    * `mode='regular'`: Distributes points in an even grid pattern.
* `createGeometry()`:
    * **Random Mode:** Inside a loop of `point_count`:
        1.  Selects a random face (0-5).
        2.  Selects random `u, v` coordinates within `[-s, s]`.
        3.  Maps `u, v` to 3D space based on the fixed axis of the selected face (e.g., Front Face -> $z = +s$).
    * **Regular Mode:**
        1.  Calculates `grid_size = sqrt(points / 6)`.
        2.  Iterates `i, j` from `0` to `grid_size`.
        3.  Generates points at fixed intervals `step = side_length / grid_size`.

## Dependencies
* **Internal:** `framework.shapes.shape`.
* **Libraries:** `pyglm`, `numpy`, `random`.