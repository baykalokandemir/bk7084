import math

class Node:
    """
    Represents an intersection in the city graph.
    Prop:
        x, y: position on the ground plane.
        id: unique identifier.
        edges: list of connected Edge objects.
    """
    _id_counter = 0

    def __init__(self, x, y):
        self.id = Node._id_counter
        Node._id_counter += 1
        self.x = x
        self.y = y
        self.edges = []

    def add_edge(self, edge):
        if edge not in self.edges:
            self.edges.append(edge)

    def remove_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)

    def __repr__(self):
        return f"Node(id={self.id}, x={self.x:.2f}, y={self.y:.2f})"


class Edge:
    """
    Represents a road segment between two nodes.
    Prop:
        start_node, end_node: Node objects.
        width: width of the road.
        lanes: number of lanes (for visual/logic later).
    """
    def __init__(self, start_node, end_node, width=10.0, lanes=2):
        self.start_node = start_node
        self.end_node = end_node
        self.width = width
        self.lanes = lanes
        
        # Bi-directional consistency
        start_node.add_edge(self)
        end_node.add_edge(self)

    @property
    def length(self):
        dx = self.end_node.x - self.start_node.x
        dy = self.end_node.y - self.start_node.y
        return math.sqrt(dx*dx + dy*dy)

    def __repr__(self):
        return f"Edge(start={self.start_node.id}, end={self.end_node.id}, w={self.width})"


class CityGraph:
    """
    The main graph data structure representing the city road network.
    """
    def __init__(self):
        self.nodes = []
        self.edges = []

    def add_node(self, x, y):
        node = Node(x, y)
        self.nodes.append(node)
        return node

    def add_edge(self, node_a, node_b, width=10.0, lanes=2):
        # Prevent duplicate edges between same nodes? 
        # For now, allow simple multigraph behavior or assume caller checks.
        edge = Edge(node_a, node_b, width, lanes)
        self.edges.append(edge)
        return edge

    def remove_edge(self, edge):
        if edge in self.edges:
            self.edges.remove(edge)
            edge.start_node.remove_edge(edge)
            edge.end_node.remove_edge(edge)

    def clear(self):
        self.nodes = []
        self.edges = []
        Node._id_counter = 0

    def get_nearest_node(self, x, y, threshold):
        """
        Finds the nearest node within a threshold distance.
        Returns None if no node is close enough.
        """
        best_node = None
        min_dist_sq = threshold * threshold

        for node in self.nodes:
            dx = node.x - x
            dy = node.y - y
            dist_sq = dx*dx + dy*dy
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                best_node = node
        
        if best_node:
            return best_node, math.sqrt(min_dist_sq)
        return None, float('inf')
