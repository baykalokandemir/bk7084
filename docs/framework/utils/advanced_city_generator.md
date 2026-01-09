# Advanced City Generator

`framework.utils.advanced_city_generator`

The `AdvancedCityGenerator` is the procedural engine responsible for creating the High-Fidelity BSP (Binary Space Partitioning) layout of the city. It generates the physical geometry for blocks, roads, sidewalks, and building lots.

## Key Concepts

### 1. BSP Layout Generation
The city starts as a single large rectangle (Root Polygon). It is recursively subdivided into smaller regions (Blocks) using a BSP tree algorithm.
-   **Split Logic**: Divided by random lines, either orthogonal (grid-like) or random angles (organic).
-   **Road Creation**: Each split line becomes a road segment.

### 2. Uniform Road Network
Unlike complex road hierarchies, this generator produces a **uniform traffic network**:
-   **Road Width**: All roads are generated with a standard width of **8.0 meters**.
-   **Lanes**: All roads are configured as **2-lane** (1 forward, 1 backward).
-   **Reasoning**: This simplification ensures reliable graph connectivity and predictable traffic flow simulation without the complexity of merging multi-lane arterials with local streets.

### 3. Block & Lot Subdivision
After the main road network is carved, the resulting "Blocks" are further subdivided:
-   **Inset**: Blocks are shrunk to create space for Sidewalks and Curbs.
-   **Lots**: Blocks are recursively split into smaller building plots ("Lots").
-   **Zoning**: These lots are passed to the `CityGenerator` (or used directly) to spawn `Building` instances.

## Methods

### `generate()`
The main entry point.
1.  **Town Square**: Optionally carves a central plaza (currently disabled in hybrid mode).
2.  **Recursion**: Calls `_split_city_recursive` to slice the city into blocks and roads.
3.  **Mesh Generation**: Converts the abstract `RoadNetwork` edges into 3D meshes (Roads, Sidewalks).
4.  **Street Lights**: Procedurally places street lamps along the road edges.

## Usage

```python
# Create a 400x400m city
adv_gen = AdvancedCityGenerator(width=400, depth=400)
adv_gen.generate()

# Access generated geometry
render_roads(adv_gen.roads)
render_buildings(adv_gen.buildings)
```