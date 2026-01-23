# Traffic UI Control Documentation

To facilitate testing and chaos management, several ImGui controls have been added to the "City Controls" panel.

## Simulation Controls

### Recklessness Control
- **`Reckless %` (Slider)**: Controls the probability (0.0 to 1.0) that a **newly spawned** car will be initialized as a "Reckless Driver".
    - **Default**: 0.2 (20%)
    - **Note**: Modifying this slider only affects *future* spawns. Existing cars retain their behavior.

### Chaos Management
- **`Clear Wrecks` (Button)**: Instantly removes all Red Cube crash markers from the scene.
    - Useful for cleaning up the view after a long simulation session without resetting the entire city or traffic flow.

### Manual Braking (Debug)
- **`Num to Brake` (Input)**: Number of cars to select for manual braking.
- **`Brake Random Cars` (Button)**: Freezes the specified number of random **normal** (non-reckless) drivers in place.
    - Used to intentionally create traffic jams to test collision avoidance or reckless driver crashes.
- **`Release All` (Button)**: Unfreezes all manually braked cars.

## Performance Optimization
- **Geometry Reuse**: Crash markers now share a single `Cube` geometry instance on the GPU, significantly reducing memory overhead when hundreds of crashes accumulate.
