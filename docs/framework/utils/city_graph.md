# CityGraph

`framework.utils.city_graph`

The `CityGraph` module provides the fundamental data structures for representing the logical connectivity of the city. It is a node-edge graph that serves as the "brain" of the city, enabling traffic simulation, pathfinding, and AI navigation.

## Classes

### `Node`
Represents a single intersection or endpoint in the road network.

**Properties:**
- `id` (int): Unique identifier for the node.
- `x`, `y` (float): Spatial position on the ground plane (XZ).
- `edges` (list[Edge]): List of `Edge` objects connected to this node.

**Methods:**
- `add_edge(edge)`: Connects an edge to this node.
- `remove_edge(edge)`: Disconnects an edge from this node.

---

### `Edge`
Represents a road segment connecting two `Node` objects.

**Properties:**
- `start_node` (Node): The starting intersection.
- `end_node` (Node): The ending intersection.
- `width` (float): The physical width of the road (default: 10.0).
- `lanes` (int): Number of lanes (default: 2).
- `length` (property): Returns the Euclidean length of the edge.

**Note:**
Edges are bi-directional in connectivity (added to both nodes), but the `start` and `end` distinction is useful for calculating lane offsets (vectors).

---

### `CityGraph`
The container class for the entire road network.

**Properties:**
- `nodes` (list[Node]): All intersections in the city.
- `edges` (list[Edge]): All road segments in the city.

**Methods:**

#### `add_node(x, y) -> Node`
Creates and registers a new `Node` at the specified position.

#### `add_edge(node_a, node_b, width=10.0, lanes=2) -> Edge`
Creates a connection between two existing nodes. Use this method instead of manually creating `Edge` objects to ensure they are tracked by the graph.

#### `remove_edge(edge)`
Safely removes an edge from the graph and disconnects it from its nodes.

#### `get_nearest_node(x, y, threshold) -> (Node, float)`
Finds the closest node to the given `(x, y)` coordinates within the `threshold` distance.
- **Returns**: `(Node, distance)` or `(None, infinity)` if no node is found.

#### `clear()`
Resets the entire graph, removing all nodes and edges.
