# Antigravity Engine (Mikoshi Framework)

## 1. Overview
This project is a specialized OpenGL rendering engine built on top of a standard educational framework. It diverges significantly from the base version to support advanced procedural generation and stylized rendering effects.

**Core Aesthetic:**
* **Mikoshi Style:** Volumetric point clouds with density-based glowing.
* **Holographic:** Scanline slicing effects and CRT-style screen interference.
* **Procedural:** Entire cities and complex geometries generated via code, not loaded from static assets.

---

## 2. Quick Start
**⚠️ CRITICAL WARNING:** Do not use `framework/main.py` or `project/main.py`. These are legacy/dummy files that will result in a frozen window or a blank screen because they lack the necessary event polling logic required by the new renderer.

**Correct Entry Points:**
* **Point Cloud Demo:** Run `exercises/mikoshi_test.py`
* **City Generator:** Run `exercises/advanced_city_test.py` (Analysis pending)

---

## 3. System Architecture

| Component | File Path | Responsibility |
| :--- | :--- | :--- |
| **Application** | `exercises/mikoshi_test.py` | The Game Loop. Handles Window, Input, UI integration, and Time. |
| **Logic** | `framework/scene_manager.py` | The Brain. Generates geometry, manages entity lists, and updates shader uniforms. |
| **Interface** | `framework/ui_manager.py` | The Controls. Renders the ImGui panel to tweak config variables. |
| **Graphics** | `framework/renderer.py` | The Painter. Wraps OpenGL draw calls. *Note: Frame buffer swapping is disabled here to allow UI injection.* |
| **Resources** | `framework/gltf_loader.py` | The Importer. Loads external `.gltf` / `.glb` models (e.g., the car). |

---

## 4. Key Algorithms (Utils)

### A. Procedural City Generation
Located in `framework/utils/`.
* **`advanced_city_generator.py`**: The Master Architect. Creates a hierarchical city layout starting from a central hexagon ("Town Square") and recursively splitting sectors into blocks and lots.
* **`road_network.py`**: A dynamic graph system. Automatically repairs geometry when roads intersect, creating clean 4-way junctions and assigning traffic lanes.
* **`building.py`**: The Constructor. Extrudes 2D polygonal footprints into 3D structures with recessed windows, stepped setbacks, and roof antennas.
* **`polygon.py`**: The Foundation. Robust 2D geometry class handling operations like splitting, insetting (for sidewalks), and chamfering corners.

### B. Geometry Optimization
* **`point_cloud_generator.py`**:
    * **Function:** Converts solid meshes (Cubes, Cars) into "Mikoshi" point clouds.
    * **Logic:** Uses area-weighted triangle sampling or Poisson Disk Sampling to distribute points evenly. Calculates local density and stores it in `UV.x` for the shader.
* **`mesh_batcher.py`**:
    * **Function:** Static Batching.
    * **Logic:** Merges thousands of individual building/road shapes into a single massive mesh on the CPU to reduce draw calls from $N$ to $1$.

---

## 5. Shader Library

### A. Mikoshi (Point Cloud)
* **Files:** `mikoshi_shader.vert`, `mikoshi_shader.frag`
* **Visuals:** Glowing points that change color based on distance.
* **Tech:** Repurposes UV coordinates to store "Density". High-density areas glow white/magenta. Point size attenuates with distance.

### B. Slice (Hologram)
* **Files:** `slice_shader.vert`, `slice_shader.frag`
* **Visuals:** Objects appear to be sliced by laser scanlines.
* **Tech:** Uses `discard` in the fragment shader based on world-space position modulo (`pos % spacing`). Applies sine-wave distortion for a "glitch" look.

### C. Hologram (2D)
* **Files:** `hologram.frag`
* **Visuals:** CRT screens and digital billboards.
* **Tech:** Converts texture colors to luminance, re-colors them to a single hue, and overlays procedural scanlines and vertical strips.

---

## 6. Procedural Shapes
Located in `framework/shapes/`.
* **`random_cube.py` / `random_sphere.py`**: Primitives defined by a cloud of vertices rather than solid triangles.
* **`car.py`**: A composite shape factory. Generates a vehicle body and 4 wheels, transforming and merging them into a single object.