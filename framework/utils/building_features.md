# Building Features Documentation

This document details the procedural building generation features implemented in the `framework/utils` module.

## 1. Polygon Geometry (`polygon.py`)

The foundation of the building system is the `Polygon` class, which supports advanced geometric operations:

*   **`split(split_point, split_dir)`**: Divides a polygon into two pieces using an arbitrary line. Used for the BSP city layout.
*   **`scale(factor)`**: Scales the polygon relative to its geometric centroid. Used to create road gaps between blocks.
*   **`chamfer(radius)`**: Bevels the corners of the polygon, creating a flat cut.
*   **`fillet(radius, segments)`**: Rounds the corners of the polygon using quadratic Bezier curves for a smooth finish.

## 2. Building Generation (`building.py`)

The `Building` class takes a 2D `Polygon` footprint and generates a detailed 3D mesh.

### Core Features
*   **Inset Windows**: Windows are physically inset into the facade, creating depth. They include:
    *   **Frames**: 3D geometry for window frames.
    *   **Glass**: Separate geometry for the glass pane (allows for different materials/colors).
    *   **Sills & Headers**: Solid wall sections above and below windows.
*   **Corner Columns**: Structural columns are generated at every corner to ensure solid geometry and prevent gaps between window sections.

### Styles & Parameters
The appearance is controlled via a `style` dictionary passed to the constructor:

*   **`window_style`**:
    *   `"single"`: Wide horizontal bands of glass (default).
    *   `"vertical_stripes"`: Thin vertical windows repeated across the facade.
        *   **Brick-like Shift**: Vertical windows are shifted horizontally on alternating floors to create a staggered pattern.
*   **`stepped` (bool)**: If true (and building is tall), the building creates setbacks, tapering as it rises (3 tiers).
*   **`floor_height`**: Height of each story.
*   **`window_ratio`**: Percentage of the floor height occupied by the window.
*   **`inset_depth`**: How deep the windows are recessed.

### Roof Features
*   **Antennas**: Randomly generates antenna/spire structures on the roof for added detail.

## 3. City Generator (`advanced_city_generator.py`)

The `AdvancedCityGenerator` orchestrates the creation of the city layout and buildings.

### Layout Logic
*   **Generalized BSP**: Uses Binary Space Partitioning with arbitrary split angles.
*   **Orthogonal Bias**: 90% chance to split at 0 or 90 degrees to maintain a structured grid, with 10% organic/diagonal splits.
*   **Two-Stage Splitting**:
    1.  **City -> Blocks**: Splits the city into large blocks. These are scaled down to create **Roads**.
    2.  **Block -> Lots**: Splits blocks into individual building lots. These are **not** scaled, ensuring buildings touch each other.
*   **Aspect Ratio Correction**: Splits are biased to cut the longest axis, preventing the creation of thin sliver lots.

### Special Features
*   **Town Square**: Automatically carves out a hexagonal park in the center of the city, surrounded by a wide roundabout.
*   **Randomization**:
    *   **Corner Style**: 20% Chamfer, 20% Fillet, 60% Sharp.
    *   **Window Style**: 50% Single, 50% Vertical Stripes.
    *   **Stepped**: 40% chance for tall buildings to be stepped.
    *   **Height**: Random height variation (10.0 - 40.0 units).

## Usage Example

```python
from framework.utils.advanced_city_generator import AdvancedCityGenerator
from framework.utils.mesh_batcher import MeshBatcher

# 1. Generate City Data
generator = AdvancedCityGenerator(width=400, depth=400)
generator.generate()

# 2. Batch Render
batcher = MeshBatcher()

# Add Buildings
for shape in generator.buildings:
    batcher.add_shape(shape)

# Add Parks
for shape in generator.parks:
    batcher.add_shape(shape, color=glm.vec4(0.2, 0.8, 0.2, 1.0))

# 3. Create MeshObject
city_mesh = batcher.build(material)
```
