# framework/utils/road_network.py

## Overview
A dynamic graph manager that represents the city's infrastructure. Unlike a standard graph, it handles **geometric intersections**. When a new road segment is added, the class checks if it crosses any existing roads. If an intersection is detected, it splits both the new and existing segments, creating a new node at the crossing point. This ensures a clean, connected planar graph essential for traffic logic and mesh generation.

## Key Logic
### Graph Management (`add_segment`)
* **Snapping:** Rounds coordinates to 1 decimal place to prevent floating-point errors from creating duplicate nodes or tiny gaps.
* **Intersection Handling:**
    * Iterates through all existing segments to check for crossings.
    * **Logic:** Uses standard line-segment intersection math ($p + t \cdot r = q + u \cdot s$).
    * **Action:** If a split is required:
        1.  **Deletes** the existing segment.
        2.  **Creates** two new segments connecting the original endpoints to the new intersection point.
        3.  **Recursively** calls `add_segment` for the new road to ensure it checks against the *rest* of the network.

### Mesh Generation (`generate_meshes`)
* **Intersection Geometry:**
    * For every node, it identifies all connected roads and sorts them by angle.
    * **Corner Calculation:** Calculates the "Left" and "Right" edges of every road entering the intersection. It finds the intersection point of adjacent road edges (e.g., Road A's Left edge and Road B's Right edge) to define the polygon shape of the intersection itself.
* **Segment Geometry:**
    * Fills the gaps between intersections with simple Quads.
* **Output:** Returns a list of `Shape` objects (ready for batching) and a list of `road_edges` (metadata used to place street lights).

## Dependencies
* **Internal:** `framework.shapes.shape`.
* **Libraries:** `pyglm`, `numpy`, `math`.