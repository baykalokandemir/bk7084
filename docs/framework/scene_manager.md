# framework/scene_manager.py

## Overview
A high-level coordinator designed specifically to generate and manage the "Mikoshi" (Point Cloud) and "Hologram Slice" demo scenes. It abstracts the logic of loading meshes, converting them into point clouds, assigning materials, and arranging them in 3D space. It also handles the frame-by-frame updates for shader uniforms (like animating the slice effect).

## Changelog (Original vs. Current)
* **New File:** This file did not exist in the original version. It appears to be a refactor to move scene construction logic out of `main.py` or exercise files.
* **Antigravity/AI Note:**
    * The class is named `SceneManager`, but it behaves more like a `DemoSceneLoader`. It contains hardcoded positions (e.g., `translate(-5.0, 0, 0)`) and specific logic for "Mikoshi" and "Slice" shaders.
    * It tightly couples the scene logic with a `config` object (likely from the UI), making it easy to tweak settings but hard to reuse for other game levels.

## Key Classes & Functions
### `SceneManager`
* `__init__()`: Pre-loads the specific materials (`mikoshi_mat`, `slice_mat`) used for this demo.
* `generate_scene(config)`:
    * **GLTF Mode:** If a file path is provided in `config`, it loads the GLTF model. It can either convert it to a Point Cloud (using `PointCloudGenerator`) or render it as a solid mesh with the Slice effect.
    * **Default Mode:** If no file is provided, it generates a hardcoded "Gallery" of test objects:
        1.  Point Cloud Cube & Sphere.
        2.  "Random" Cube & Sphere (procedural volume points).
        3.  Solid Cube & Sphere (showing the Slice shader).
        4.  A generated Car model.
* `update_uniforms(config, dt)`:
    * **Animation:** Updates `self.slice_offset` based on time (`dt`) to make the slice effect scan across the object.
    * **Material Sync:** Copies values from the `config` object (Color, Glow, Slice Thickness, Warp) into the shader uniforms every frame.

## Dependencies
* **Internal:** `framework.materials.Material`, `framework.gltf_loader`, `framework.utils.point_cloud_generator`.
* **Shapes:** `UVSphere`, `Cube`, `RandomCube`, `RandomSphere`, `Car`.