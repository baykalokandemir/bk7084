# City Generator Logic

**Path**: `framework/utils/city_generator.py`

This module provides high-level algorithms to generate the city graph structure, analyze connectivity, and prepare it for traffic simulation.

## Key Methods

### 1. `build_graph_from_layout(layout)`
- **Input**: An `AdvancedCityGenerator` instance (or similar layout object) containing separate lists of roads, buildings, etc.
- **Process**:
    1. Extracts raw segments from the layout.
    2. Merges vertices close to each other into unique `Node` objects (Threshold ~1.0 unit).
    3. Creates `Edge` objects connecting these nodes.
    4. Triggers `node.generate_connections()` for all nodes to build intersection curves.
    5. Calls `self.audit_graph()` to verify integrity.

### 2. `audit_graph()`
**[NEW]** Connectivity Auditor.
- **Purpose**: Runs a post-generation check to identify "Dead Ends" (lanes with no valid outgoing connections).
- **Logic**:
    - Iterates every `Lane` in the graph.
    - Identifies the `exit_node` for that lane (based on travel direction).
    - Checks `exit_node.connections` for any keys starting with `lane.id`.
    - If count == 0:
        - Adds lane to `self.dead_end_lanes`.
        - Prints `[FAIL] Lane {id} has no outlets.`
- **Result**: Populates a list of problem lanes that the visualizer (`test_graph_city.py`) can render as Red or Yellow cubes.

### 3. Irregularity & Naturalization
(Inherited from previous implementation)
- `apply_irregularity(amount)`: Perturbs node positions to create organic city layouts.
