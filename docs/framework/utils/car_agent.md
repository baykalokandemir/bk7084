# Car Agent Logic

**Path**: `framework/utils/car_agent.py`

The `CarAgent` class implements the autonomous behavior for traffic agents. It handles pathfinding, movement, state transitions, and self-diagnosis of stuck states.

## Key Logic

### 1. Navigation & State Machine
The agent follows a list of `waypoints` (typically a `Lane` or a Bezier `Curve`).
- **State Switch (End of Path)**:
    - When an agent reaches the end of its current `path`, it calls `pick_next_path()`.
    - **Logic**:
        1. Access `self.current_lane.dest_node` to find the correct intersection.
        2. Filter `dest_node.connections` for keys starting with `self.current_lane.id`.
        3. **Decision**:
            - **Success**: Pick a random connection -> Switch to `current_curve` -> Set target to next lane.
            - **Dead End**: If no connections exist, log a warning and set `self.alive = False`.

### 2. Stuck Detection
- **Mechanism**: Stores `last_position` and increments `time_since_last_move`.
- **Threshold**: If distance moved < 0.01 units for > 2.0 seconds:
    - Logs `[ALERT] Car stuck at {position}`.
- **Purpose**: Helps identify physics bugs or graph disconnection issues where a car thinks it is moving but isn't.

### 3. Bidirectional Robustness
- **Old Logic**: Assumed destination was always `edge.end_node`. This caused cars on backward lanes (End->Start) to check the wrong node for connections.
- **New Logic**: Uses `lane.dest_node` (explicitly Start or End) to query the correct connectivity graph.

### 4. Identity Persistence **[NEW]**
- **System**: Auto-incrementing `_id_counter` assigns a unique `self.id` to every agent.
- **Telemetry**: All logs (`[ALERT]`, `[WARN]`, `[DEBUG]`) now include `[Car {id}]` prefix to distinguish agents in multi-agent scenarios.

### 6. Graph Integrity (Wormhole Fix) **[CRITICAL]**
- **Problem**: Python passes object references by default. Assigning `self.position = graph_node_pos` meant the agent held a reference to the **actual city graph node**.
- **Consequence**: When the agent moved (`self.position += step`), it dragged the graph node with it, corrupting the road network for all other cars.
- **Solution**: Explicitly copy vectors using `glm.vec3(target)` or `glm.vec3(node.x, node.y, node.z)` when transferring data from Graph to Agent.

### 7. Visual Debugging
- **`render_debug(renderer, camera)`**: Renders a **Bright Yellow Sphere** at the agent's current *Target Waypoint*.
