# framework/shapes/other_shapes.md

## Overview
This document covers the standard geometric primitives included in the framework. These shapes form the building blocks for more complex objects (like the Car) or serve as test meshes.

## Common Features
* **Inheritance:** All classes inherit from `framework.shapes.shape.Shape`.
* **`split_faces` Parameter:** The `Cone`, `Cylinder`, and `UVSphere` classes accept a boolean `split_faces`.
    * `False` (Default): Vertices are shared between faces. Normals are averaged, resulting in **Smooth Shading**.
    * `True`: Vertices are duplicated for each face. Normals are perpendicular to the face, resulting in **Flat Shading** (low-poly look).

---

### `Cone`
* **Description:** A cone aligned along the Y-axis, centered at the origin.
* **Key Logic:** Generates a top apex vertex and a bottom ring of vertices. Includes a bottom disk cap.
* **Parameters:** `radius`, `height`, `segments`.

### `Cylinder`
* **Description:** A cylinder aligned along the Y-axis, centered at the origin.
* **Key Logic:** Generates top and bottom rings connected by quad strips (sides), plus two disk caps (top/bottom).
* **Parameters:** `radius`, `height`, `segments`.

### `Quad`
* **Description:** A simple 2D rectangle in the XY plane (Z=0).
* **Key Logic:** Composed of 4 vertices and 2 triangles. Useful for UI elements, billboards, or floor tiles.
* **Parameters:** `width`, `height`.

### `Triangle`
* **Description:** A single equilateral-ish triangle in the XY plane.
* **Key Logic:** The simplest possible mesh (3 vertices, 1 index triangle).
* **Usage:** Primarily for debugging or minimal testing.

### `UVSphere`
* **Description:** A standard sphere generated using latitude (stacks) and longitude (slices).
* **Key Logic:**
    * Iterates through spherical coordinates ($\phi$, $\theta$) to generate vertices.
    * Texture coordinates (UVs) map the entire image to the sphere surface (standard equirectangular mapping).
* **Parameters:** `radius`, `stacks`, `slices`.