# CityGenerator

`framework.utils.city_generator`

The `CityGenerator` class acts as the **builder** and **manager** of the `CityGraph`. Its primary responsibility is to convert spatial layout data from procedural algorithms (like BSP) into a clean, connected graph structure suitable for AI navigation. It also handles the zoning and generation of buildings along the road network.

## Key Responsibilities

1.  **Graph Construction**: Importing raw segments from a layout generator and welding them into a connected graph using Spatial Hashing.
2.  **Zoning**: Procedurally placing building plots along road edges.
3.  **Simulation State**: It holds the `CityGraph` instance that drives the simulation.

## Methods

### `__init__()`
Initializes empty lists for buildings and a new empty `CityGraph`.

### `build_graph_from_layout(layout_generator)`
Ingests a road network from a layout source (e.g., `AdvancedCityGenerator`).

**Process:**
1.  Iterates through `layout_generator.road_network.segments`.
2.  **Spatial Hashing**: Rounds vertex coordinates to `0.1m` precision. If two segment endpoints fall into the same "bucket", they share a single `Node`. This ensures loop closure and connectivity.
3.  **Cleaning**: Filters out zero-length or degenerate segments to prevent math errors.
4.  Populates `self.graph` with the resulting Nodes and Edges.

**Usage:**
```python
adv_gen = AdvancedCityGenerator(width=400, depth=400)
adv_gen.generate()

city_gen = CityGenerator()
city_gen.build_graph_from_layout(adv_gen)
```

### `generate_buildings()`
Populates the city with 3D buildings based on the graph structure.

**Algorithm:**
1.  Iterates through every `Edge` in the graph.
2.  Calculates the "Right" and "Left" vectors relative to the road direction.
3.  Steps along the road at regular intervals (plot width).
4.  Places a `Building` object on both the left and right sides of the road.
5.  **Alignment**: Buildings are oriented to face the road.
6.  **Style**: Randomizes height, window style, and stepped geometry for visual variety.

Output is stored in `self.buildings`, which is a list of `Shape` objects ready for the `MeshBatcher`.
