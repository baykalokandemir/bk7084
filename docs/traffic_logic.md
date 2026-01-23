# Traffic Logic Documentation

## Lane Registry System
To enable efficient spatial queries without a global spatial hash (for now), we implemented a **Lane Registry**.

### Overview
Each `Lane` object now maintains a list of `active_agents`:
- **`active_agents`**: A list of `CarAgent` instances currently traversing this lane.

### Agent Logic
The `CarAgent` manages its registration automatically:
1.  **Registration**: When entering a lane (spawn or transition), the agent calls `lane.active_agents.append(self)`.
2.  **Deregistration**: When leaving a lane (despawn, or entering a curve), the agent calls `lane.active_agents.remove(self)`.
3.  **Curve Handling**: While on a curve (intersection), the agent is technically "between lanes" and is not registered on any lane list. This prevents it from blocking cars on the previous logic (though eventually we might want intersection registries).

## Collision Avoidance (Braking)
We implemented a simple "Distance Keeper" logic.

### Update Loop
Every frame, `CarAgent.update()`:
1.  Checks if it is on a valid `Lane`.
2.  Iterates through `self.current_lane.active_agents`.
3.  Identifies agents that are **ahead** of it.
    - Ahead is determined by `target_index` (further along path) or remaining distance to the same target node.
4.  Calculates distance to the nearest agent ahead.
5.  **Action**:
    - If distance < **4.0 units**, set speed to `0.0`.
    - Otherwise, set speed to `15.0`.

### Limitations
- Agents on curves do not check for collisions (yet).
- Agents entering a new lane from a curve might "ghost" into an existing car if the gap is small (though they will register and brake once they are fully on the lane).
- Intersection logic is purely random and does not check for cross-traffic.

## Phase 3: Crash System

### Reckless Drivers
To simulate human error, `CarAgent` now has a property `is_reckless` (20% chance on spawn).
- **Behavior**: Reckless drivers **completely ignore** the braking logic triggered by cars ahead of them in the Lane Registry. They will drive through other cars, causing collisions.

### Collision Detection (Spatial Hashing)
To correctly detect impacts, we implemented a broad-phase collision system using **Spatial Hashing**.
- **Algorithm**:
    1.  **Grid**: The world is divided into strict cells of size **5.0 units**.
    2.  **Bucketing**: Each frame, every active agent is hashed into a bucket based on its `(x, z)` position.
    3.  **Check**: We iterate through each bucket. If a bucket has >1 agents, we check distance between them.
    4.  **Collision**: If distance < **2.5 units**, a crash is registered.
- **Resolution**:
    - Both agents are marked as dead (`alive = False`).
    - The crash coordinate (midpoint) is stored in `crash_events` for future visualization.

