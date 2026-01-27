# Traffic System Architecture

## 1. The City Graph
The traffic system is built upon a directed graph structure (`CityGraph`) that overlays the visual city mesh.
*   **Nodes**: Represent intersections or connection points. Each node contains a dictionary of `active_connections`, allowing agents to query valid paths to adjacent nodes.
*   **Edges**: Represent roads connecting two nodes. Each edge is subdivided into **Lanes**.
*   **Lanes**: The fundamental unit of navigation. A lane contains a list of **Waypoints** (3D coordinates) that agents follow. 
    *   **Registry**: Each lane maintains an `active_agents` list, allowing for O(1) lookup of cars currently traveling on it.

## 2. The Car Agent
The `CarAgent` class encapsulates the logic for a single vehicle.
*   **Waypoint Following**: Agents seek the next point in their `current_lane.waypoints`. Upon reaching a target (within a small radius), they advance to the next index.
*   **Lane Changing/Turning**: When an agent reaches the end of a lane (Node), it queries the Node for connections. A connection is a Bezier curve (list of points) leading to a target lane. The agent traverses this curve and then registers onto the new lane.
*   **State Machine**:
    *   `Alive`: Active in the scene.
    *   `Reckless`: A boolean flag determining behavior (see below).
    *   `Manual Brake`: A flag controlled by the user via ImGui.

## 3. Optimization Strategies

### A. Lane Registry (Collision Avoidance)
To prevent rear-end collisions efficiently, we use a **Lane Registry** system.
*   **Problem**: Checking every car against every other car for braking is O(N^2).
*   **Solution**: Each car only cares about the car *immediately ahead* in the *same lane*.
*   **Implementation**: By checking `current_lane.active_agents`, a car only iterates over a small subset of relevant neighbors. This reduces the complexity to near O(1) per agent for braking logic.

### B. Spatial Hashing (Crash Detection)
To detect physical crashes (intersections/high speed impacts), we needed a global check.
*   **Problem**: Cars can crash into others in *different* lanes (e.g., at intersections). The Lane Registry doesn't cover this.
*   **Solution**: **Spatial Hashing**.
*   **Implementation**: The world is divided into a 2D grid (Buckets of 5.0 units).
    1.  Each frame, agents are hashed into buckets based on their `(x, z)` position.
    2.  Collision checks are only performed between agents in the same bucket.
    3.  This reduces global collision detection from O(N^2) to amortized O(N).

## 4. The "Reckless" Feature
To simulate entropy and verify collision systems, we introduced **Reckless Drivers**.
*   **Concept**: A percentage of cars (controlled via ImGui) are spawned as "Reckless".
*   **Behavior**: Reckless drivers **ignore** the Lane Registry braking logic. They will drive through other cars if their path is blocked.
*   **Visuals**: Reckless drivers are tinted **Orange**, while normal drivers are **Yellow**.
*   **Result**: This deterministic chaos allows us to test the Spatial Hashing system (Crash Detection) effectively. When a crash occurs (distance < 2.5 units), a **Red Cube** is rendered at the impact site, and the `total_crashes` counter is incremented.
