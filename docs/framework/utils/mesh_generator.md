# MeshGenerator

`framework.utils.mesh_generator`

The `MeshGenerator` class is a specialized **Debug Visualization Tool**. While earlier versions generated the city logic geometry, the current pipeline uses this class specifically to visualize the invisible "Traffic Graph" overlaid on top of the visible city mesh.

## usage

This class is essential for verifying that the AI navigation graph (`CityGraph`) aligns perfectly with the visual road geometry (`AdvancedCityGenerator`).

## Methods

### `generate_traffic_debug(graph) -> Shape`
Generates a `Shape` object containing a wireframe visualization of traffic lanes.

**Visual Output:**
-   **Method**: `GL_LINES` (Line primitives).
-   **Forward Lanes (Right Side)**: Rendered in **Neon Green**.
-   **Backward Lanes (Left Side)**: Rendered in **Neon Red**.
-   **Offsets**: The lines are offset `0.15 * RoadWidth` from the center to roughly match the center of the asphalt lane.
-   **Elevation**: Lines are lifted `0.8m` above the ground `(Y=0.8)` to ensure they float clearly above curbs, sidewalks, and road surfaces without Z-fighting.

**Technical Details:**
-   Uses `glm.vec4` for vertex positions to ensure compatibility with the renderer's stride expectation.
-   Forces Normals to `(0, 1, 0)` (UP) to ensure the lines catch lighting and appear bright/neon even though lines typically don't have surface normals.

**Example:**
```python
mesh_gen = MeshGenerator()
debug_shape = mesh_gen.generate_traffic_debug(city_gen.graph)

# Render as GL_LINES
debug_mesh = MeshObject(debug_shape, Material())
debug_mesh.draw_mode = gl.GL_LINES
renderer.addObject(debug_mesh)
```
