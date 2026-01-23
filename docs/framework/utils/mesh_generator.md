# Mesh Generator Visualization

**Path**: `framework/utils/mesh_generator.py`

This module creates the visual representations (Meshes) for the simulation data.

## Key Methods

### 1. `generate_traffic_debug(graph)`
**[NEW]** Generates a wireframe debugger for the logic graph.
- **Input**: `CityGraph` object.
- **Output**: A `Shape` object containing lines for:
    - **Green Lines**: Forward Lanes (Start -> End).
    - **Red Lines**: Backward Lanes (End -> Start).
    - **Cyan Curves**: Intersection connections (Bezier paths).
- **Usage**:
    - The output shape is usually wrapped in a `MeshObject` with `gl.GL_LINES` draw mode.
    - Used in `test_graph_city.py` to overlay the logical road network on top of the visual BSP geometry.
    - Visual Offset: Lines are lifted slightly (`y=0.2`) to avoid z-fighting with the road pavement.
