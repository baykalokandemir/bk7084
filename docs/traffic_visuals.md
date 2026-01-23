# Traffic Visuals Documentation

## Vehicle Colors
To assist with debugging and observation, vehicles are color-coded based on their behavior profile:

*   **Yellow (`vec4(1.0, 1.0, 0.0, 1.0)`)**: **Normal Drivers**. These drivers obey traffic rules, including the Lane Registry and braking logic.
*   **Orange (`vec4(1.0, 0.5, 0.0, 1.0)`)**: **Reckless Drivers**. These drivers (approx. 20% of population) ignore braking logic and will cause collisions if obstructed.

## Crash Visualization
When the Spatial Hashing system detects a collision (overlap), the following visual feedback occurs:

1.  **Agent Removal**: The colliding cars are immediately removed from the simulation (`alive = False`) and vanish.
2.  **Crash Marker**: A **Red Cube** (`side_length=2.5`) is spawned at the exact midpoint of the collision.
    *   **Material**: The cube uses a high ambient strength material (unlit red) to appear "glowing" or highly visible.
    *   **Persistence**: These cubes remain in the scene until the "Regenerate" button is pressed, allowing users to survey high-risk areas over time.
