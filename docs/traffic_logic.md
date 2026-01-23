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
