# framework/utils/point_cloud_generator.py

## Overview
A powerful geometry processing utility that converts solid meshes into volumetric point clouds. It analyzes the surface area of the source mesh to ensure points are distributed evenly, preventing "clumping" in small triangles and "gaps" in large ones. It also calculates local point density to drive the glowing shader effects.

## Key Classes & Functions
### `PointCloudGenerator`
* **`generate(source_shape, point_count, color, mode)`**
    * **Input:** A source `Shape` object (Cube, Car, Loaded GLTF).
    * **Process:**
        1.  **Triangle Extraction:** Converts the source mesh into a list of triangles (handling both indexed and non-indexed geometry).
        2.  **Area Weighting:** Calculates the surface area of every triangle. This allows the sampler to pick larger triangles more often, ensuring uniform density across the entire model.
        3.  **Sampling Modes:**
            * **`'random'`:** Uses barycentric coordinate sampling ($\sqrt{r_1}$ method) to pick random points inside triangles. Fast but noisy.
            * **`'poisson'`:** Uses **Poisson Disk Sampling** (Dart Throwing) with a 3D grid acceleration structure. This rejects points that are too close to neighbors, creating a clean, high-quality distribution with no overlapping points.
        4.  **Density Calculation:**
            * Performs a neighbor search (currently $O(N^2)$) to count how many other points are within `search_radius`.
            * Normalizes this count and stores it in the **UV.x** channel.
            * *Note:* This data is read by `mikoshi_shader.vert` to make dense areas glow brighter.
    * **Output:** Returns a new `Shape` object containing only vertices (no indices), optimized for `GL_POINTS` rendering.

### Helper Methods
* **`_sample_triangle(v0, v1, v2)`**:
    * Implements the standard formula for uniform random sampling within a triangle:
    * $P = (1 - \sqrt{r_1})A + (\sqrt{r_1}(1 - r_2))B + (\sqrt{r_1}r_2)C$
    * This prevents points from clustering near the vertices.

## Dependencies
* **Internal:** `framework.shapes.shape`.
* **Libraries:** `pyglm`, `numpy`, `random`.