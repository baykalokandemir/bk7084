# City Graph Data Structures

**Path**: `framework/utils/city_graph.py`

This module defines the core data structures for the traffic simulation graph. It represents the city as a network of Nodes (intersections) and Edges (roads), with detailed Lane information for agent navigation.

## Core Classes

### 1. `Lane`
Represents a single driveable strip of road.
- **Attributes**:
    - `id`: Unique integer ID.
    - `waypoints`: List of `glm.vec3` points defining the center line of the lane.
    - `parent_edge`: Reference to the `Edge` this lane belongs to.
    - `dest_node`: **[NEW]** The explicit destination `Node` this lane leads to. Crucial for bidirectional traffic logic.
        - For Forward Lanes (index 0), `dest_node` is `edge.end_node`.
        - For Backward Lanes (index 1), `dest_node` is `edge.start_node`.
- **Key Logic**:
    - Stores directional metadata ensuring agents know exactly which intersection they are approaching, preventing "U-turn" logic errors on backward lanes.

### 2. `Node` (Intersection)
Represents a junction where roads meet.
- **Attributes**:
    - `id`, `x`, `y`: Identifiers and position.
    - `edges`: List of connected `Edge` objects.
    - `connections`: Dictionary mapping `(from_lane_id, to_lane_id)` to a list of Bezier curve points.
- **Methods**:
    - `generate_connections()`: **[UPDATED]**
        - automatically identifies incoming and outgoing lanes based on the edge topology (`start_node` vs `end_node`).
        - Enforces strict directionality:
            - **Incoming**: Start->End lanes if we are EndNode; End->Start lanes if we are StartNode.
            - **Outgoing**: Start->End lanes if we are StartNode; End->Start lanes if we are EndNode.
        - Generates cubic Bezier curves connecting valid incoming lanes to valid outgoing lanes (Left, Right, Straight turns).

### 3. `Edge` (Road Segment)
Represents a road connecting two nodes.
- **Attributes**:
    - `lanes`: List of `Lane` objects.
- **Methods**:
    - `generate_lanes()`:
        - Creates lane geometry based on road width.
        - Applies **Intersection Insets**: Shortens lanes at both ends to create visual gaps for intersections.
        - Assigns explicit `dest_node` to each generated lane.

### 4. `CityGraph`
Container class managing lists of `nodes` and `edges`.
- Provides lookup methods like `get_nearest_node` (unused by current traffic logic but available).
