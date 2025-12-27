# Antigravity Engine (Mikoshi Framework) - Architecture Guide

## 1. Project Overview
This project is a high-performance, procedural OpenGL engine built on top of a standard educational framework. It is designed to generate complex cyberpunk cities and volumetric point cloud effects ("Mikoshi" style) completely from code, without relying on static asset loading.

### Core Features
* **Procedural City Generation:** Hierarchical generation of roads, blocks, lots, and detailed buildings.
* **Volumetric Rendering:** "Mikoshi" style point clouds with density-based glowing.
* **Holographic Effects:** Real-time geometry slicing and CRT screen simulation.
* **Optimization:** CPU-side static batching and dynamic light culling to support massive scenes.

---

## 2. Directory Structure & Entry Points

**⚠️ CRITICAL WARNING:** The standard entry points (`framework/main.py`, `project/main.py`) are **DEPRECATED/DUMMY FILES**. They lack the necessary event polling logic for the new renderer and will result in a frozen application.

### Correct Entry Points
| Feature | Executable File | Description |
| :--- | :--- | :--- |
| **Point Cloud Demo** | `exercises/mikoshi_test.py` | Runs the "Mikoshi" effect, converting meshes to glowing points. |
| **City Generator** | `exercises/advanced_city_test.py` | Runs the full procedural city generator with optimization. |

### Key Folders
* **`framework/utils/`**: The "Brain". Contains all procedural algorithms (`city_generator`, `road_network`, `batcher`).
* **`framework/shaders/`**: The "Look". Contains the custom GLSL shaders (`mikoshi`, `slice`, `hologram`).
* **`framework/shapes/`**: The "Geometry". Contains procedural shape factories (`building`, `car`, `street_light`).

---

## 3. System Architecture

The engine is divided into four distinct layers:

### Layer 1: The Application Loop (Exercises)
Located in `exercises/*.py`.
* **Responsibility:** These scripts act as the **Game Engine**. They own the `Window`, `Camera`, and `Renderer`.
* **Flow:**
    1.  Initialize ImGui and OpenGL.
    2.  Call the **Generators** (Layer 2) to build the scene.
    3.  **Manual Render Loop:** They manually call `glfw.swap_buffers()` and `glfw.poll_events()` to inject the UI overlay and handle custom input.

### Layer 2: The Generators (Utils)
Located in `framework/utils/`.
* **`advanced_city_generator.py`**: The Architect.
    * Starts with a "Town Square" hexagon.
    * Recursively splits sectors -> blocks -> lots.
    * Populates lots with `Building` objects and roads with `StreetLight` objects.
* **`road_network.py`**: The Engineer.
    * Manages a dynamic graph of road segments.
    * **Self-Repairing Topology:** Automatically detects intersections and splits segments to create clean 4-way junctions.
* **`point_cloud_generator.py`**: The Converter.
    * Takes solid meshes (loaded or procedural) and dissolves them into thousands of points.
    * Calculates local density and encodes it into the `UV.x` channel for shader effects.

### Layer 3: Optimization & Rendering
* **`mesh_batcher.py`**: Static Optimization.
    * Merges thousands of static shapes (buildings, roads) into a **single draw call**.
    * Handles CPU-side matrix transformations to bake positions before upload.
* **Dynamic Light Culling:**
    * The main loop calculates distance from the camera to every streetlight.
    * It updates the shader to only process the **8 closest lights**, allowing the city to have infinite lights without performance cost.

### Layer 4: The Graphics Core
* **`scene_manager.py`**: Upgraded to support **Lazy Loading** (creating GPU buffers only when needed).
* **`renderer.py`**: A lightweight wrapper around OpenGL commands. Note that standard buffer swapping is disabled to allow Layer 1 to control timing.

---

## 4. Shader Pipeline

The engine uses three unique shader techniques to achieve its style:

### A. The Mikoshi Effect (`mikoshi_shader`)

* **Goal:** Render geometry as a cloud of glowing data points.
* **Technique:**
    * **Vertex Shader:** Sets `gl_PointSize` based on distance (perspective), and **Animated Pulse**. Passes `Density` (from UV.x) and `ScaleRatios` for shape cropping.
    * **Fragment Shader:** Renders circular or square points. Uses density to mix between Cyan (base) and White/Magenta (hotspots). Supports **Custom Shapes** (Circle/Square) via discard logic.

### B. The Slice Effect (`slice_shader`)

* **Goal:** Render solid objects as holographic projections being scanned.
* **Technique:**
    * **Discard Logic:** Uses `mod(world_pos, spacing)` to discard pixels that fall between scanlines.
    * **Warping:** Adds a sine wave offset to the position before slicing to create a "glitch" interference effect.

### C. The Hologram Effect (`hologram.frag`)

* **Goal:** Render 2D screens/billboards.
* **Technique:**
    * Converts input texture to grayscale luminance.
    * Converts input texture to grayscale luminance.
    * Overlays procedural vertical strips and animated horizontal scanlines.

### D. Post-Processing Pipeline

*   **Goal:** Apply full-screen effects after the 3D scene is rendered.
*   **Technique:**
    *   **Framebuffer Object (FBO):** The scene is rendered to an off-screen texture instead of the screen.
    *   **Render-to-Quad:** A full-screen quad is drawn with the scene texture.
    *   **Chromatic Aberration:** The fragment shader samples the Red, Green, and Blue channels at slightly different texture coordinates (offset by `aberration_strength`) to simulate lens dispersion.

---

## 5. Geometric Primitives

The engine does not load standard `.obj` files for the city. It builds them:

* **`Building`**: Extrudes a 2D `Polygon` footprint. Adds window frames and glass panes as actual geometry (not textures) to support the Slice shader.
* **`Car`**: A composite shape. Generates a prism body and 4 cylinder wheels, transforming and merging them into one mesh.
* **`StreetLight`**: A simple geometric composition (Box pole + Box arm + Box bulb) generated on the fly.