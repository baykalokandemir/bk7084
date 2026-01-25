# framework/utils/building.py

## Overview
A procedural generator that constructs 3D building meshes from 2D footprints. It goes beyond simple extrusion by adding architectural details like recessed windows, window frames, stepped setbacks (for skyscrapers), and roof antennas.

## Key Logic
### `Building` Class
* **`__init__(footprint, height, style_params)`**:
    * **`footprint`**: A `Polygon` object defining the base shape.
    * **`style_params`**: A dictionary controlling the aesthetic (e.g., `window_ratio`, `floor_height`, `stepped`).
* **`generate()`**:
    * Determines the building topology based on height.
    * **Stepped Skyscrapers:** If height > 15.0 and `stepped=True`, it recursively generates 3 stacked blocks, each smaller than the last (`scale(0.7)`, `scale(0.4)`), creating a "Wedding Cake" architecture style.
    * **Standard Blocks:** Otherwise, generates a single extrusion.
    * **Props:** Randomly adds antennas to the roof.
    * **Textures:** Assigns a `texture_name` to the generated Shape, derived from `style_params` (e.g., "brick1.png").

### `_generate_block()` (The Heavy Lifting)
* **Roof:** Uses `polygon.triangulate()` to create a flat cap.
* **Walls & Windows:**
    * Iterates through every edge of the polygon.
    * **Floors:** Slices the wall vertically into floors based on `floor_height`.
    * **Columns:** Adds solid geometry at the corners (margins).
    * **Window Logic:**
        * Calculates window intervals based on `window_style` (e.g., "vertical_stripes").
        * **Inset Effect:** Instead of painting a window texture on a flat quad, it creates **actual geometry**.
            * Pushes the window pane inwards by `inset_depth`.
            * Generates 4 extra quads to form the **Window Frame** (Top, Bottom, Left, Right) connecting the outer wall to the recessed glass.
            * Generates 4 extra quads to form the **Window Frame** (Top, Bottom, Left, Right) connecting the outer wall to the recessed glass.
            * This allows the buildings to react correctly to the "Slice" and "Mikoshi" shaders, which rely on geometric depth.
* **UV Mapping:**
    * **Walls:** UV coordinates are generated based on physical dimensions. U-coordinates correspond to the cumulative length along the building perimeter, and V-coordinates correspond to height. This ensures textures (like bricks) tile correctly without stretching, regardless of wall length or building height.
    * **Roofs:** UV coordinates use a planar projection based on the world X/Z position, scaled to ensure appropriate texture density.

## Dependencies
* **Internal:** `framework.shapes.shape`, `framework.utils.polygon`.
* **Libraries:** `pyglm`, `numpy`, `random`.