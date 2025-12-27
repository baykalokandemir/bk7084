# framework/utils/polygon.py

## Overview
A robust geometry class representing a 2D closed loop of vertices (a polygon). It serves as the "footprint" for procedural generation. It includes sophisticated methods for modifying the shape (splitting, shrinking, rounding corners) and converting it into 3D meshes (extrusion).

**Critical Assumption:** Most methods, especially `triangulate` and `inset`, assume the polygon is **Convex** and winding is **Counter-Clockwise (CCW)**. Concave shapes may produce rendering artifacts.

## Key Methods
### 3D Generation
* **`extrude(height)`**:
    * Converts the 2D polygon into a 3D prism (a `Shape` object).
    * **Top/Bottom:** Generates caps at $y=height$ and $y=0$ using a triangle fan.
    * **Sides:** Generates vertical quads connecting the edges.
    * **Normals:** Automatically calculates flat-shaded normals for the sides (perpendicular to the edge).
    * **UVs:** Applies a simple planar projection ($u=x, v=z$) to the caps and side walls.

### Geometric Operations
* **`split(split_point, split_dir)`**:
    * Slices the polygon into two new `Polygon` objects using an infinite line.
    * Used recursively to subdivide large city blocks into smaller lots.
    * Handles edge cases where the split line misses the polygon (returns original) or barely touches a vertex.
* **`inset(amount)`**:
    * Shrinks the polygon by shifting all edges inward by a fixed distance.
    * Calculates the new intersection points of the shifted edge lines.
    * Used for generating sidewalks (inset the block to find the building area).
* **`chamfer(radius)` / `fillet(radius, segments)`**:
    * **Chamfer:** Replaces sharp corners with a single flat edge.
    * **Fillet:** Replaces sharp corners with a smooth Bezier curve.
    * *Note:* Both methods include safety logic to limit the radius so it doesn't overlap with adjacent corners.

### Utilities
* **`triangulate()`**: Returns indices for a Triangle Fan (0-1-2, 0-2-3...). Fast, but valid only for convex shapes.
* **`contains_point(point)`**: Uses the 2D cross-product rule to check if a point lies "to the left" of all edges.

## Dependencies
* **Internal:** `framework.shapes.shape`.
* **Libraries:** `pyglm`, `numpy`.