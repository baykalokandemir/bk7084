# exercises/advanced_city_test.py

## Overview
The entry point for the "Procedural City" demo. It generates a complete city layout (roads, buildings, parks, lights) and renders it efficiently using **Static Batching** and **Dynamic Light Culling**.

## Key Logic
### 1. Generation & Batching
* **Problem:** Generating a city results in thousands of individual objects (e.g., 500 buildings, 1000 road segments). Rendering these individually would choke the CPU with draw calls.
* **Solution:**
    * Initializes a `MeshBatcher`.
    * Iterates through all generated components (`buildings`, `parks`, `roads`, `sidewalks`).
    * **Street Lights:** Uses the `street_light_poses` list to instantiate the same street light mesh hundreds of times at different locations, baking them all into the batch.
    * **Build:** Calls `batcher.build()` to merge everything into **one single `MeshObject`** (the `city_object`).

### 2. Dynamic Light Culling (Optimization)
* **Problem:** The fragment shader (`shader.frag`) loops through all active lights. OpenGL limits this array (e.g., `uniform vec4 light_position[10]`). The city has hundreds of street lights.
* **Solution:**
    * **Pre-Calculation:** Stores the world-space position of every light bulb in `all_bulb_positions`.
    * **Per-Frame Logic:**
        1.  Calculates the squared distance from the **Camera** to every bulb.
        2.  Sorts the list of bulbs by distance.
        3.  Selects the **8 Closest Bulbs**.
        4.  Updates the `glrenderer.lights` list to contain only the Sun + these 8 local lights.
    * **Result:** You see infinite lights in the city, but only the ones near you actually cast light.

### 3. UI & Regeneration
* Provides a **"Regenerate"** button via ImGui.
* When clicked, it:
    * Removes the old `city_object` from the renderer.
    * Calls `generator.generate()` to create a new layout.
    * Re-runs the batching process to build the new mesh.
    * Uploads the new geometry to the GPU.

## Dependencies
* **Framework:** `AdvancedCityGenerator`, `MeshBatcher`, `StreetLight`, `GLRenderer`, `FlyCamera`.
* **Libraries:** `imgui`, `glfw`, `glm`.