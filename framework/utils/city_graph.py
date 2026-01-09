import math
from pyglm import glm

class Lane:
    """
    Represents a single traffic lane.
    """
    _id_counter = 0

    def __init__(self, width, waypoints, parent_edge):
        self.id = Lane._id_counter
        Lane._id_counter += 1
        self.width = width
        self.waypoints = waypoints # List of glm.vec3
        self.parent_edge = parent_edge

    def get_point(self, distance):
        """
        Returns a point along the lane at the given distance.
        Simple linear interpolation between waypoints.
        """
        if not self.waypoints:
            return glm.vec3(0)
            
        total_len = 0
        for i in range(len(self.waypoints) - 1):
            p1 = self.waypoints[i]
            p2 = self.waypoints[i+1]
            seg_len = glm.length(p2 - p1)
            
            if distance <= total_len + seg_len:
                # Interpolate here
                t = (distance - total_len) / seg_len
                return glm.mix(p1, p2, t)
            
            total_len += seg_len
            
        return self.waypoints[-1] # Clamp to end

class Node:
    """
    Represents an intersection in the city graph.
    """
    _id_counter = 0

    def __init__(self, x, y):
        self.id = Node._id_counter
        Node._id_counter += 1
        self.x = x
        self.y = y
        self.edges = []
        # Mapping (from_lane_id, to_lane_id) -> List[vec3] waypoints
        self.connections = {} 

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
    Now contains detailed Lane objects.
    """
    def __init__(self, start_node, end_node, width=10.0, lanes_count=2):
        self.start_node = start_node
        self.end_node = end_node
        self.width = width
        self.lanes_count = lanes_count
        self.lanes = [] # List of Lane objects
        
        # Bi-directional consistency
        start_node.add_edge(self)
        end_node.add_edge(self)
        
        # Auto-generate lanes on creation
        self.generate_lanes()

    @property
    def length(self):
        dx = self.end_node.x - self.start_node.x
        dy = self.end_node.y - self.start_node.y
        return math.sqrt(dx*dx + dy*dy)

    def generate_lanes(self):
        """
        Generates Lane objects based on width and direction.
        Forward: Right side. Backward: Left side.
        Includes INSET logic to create Intersection Gaps.
        """
        self.lanes = []
        
        # 1. Base Geometry
        p1 = glm.vec3(self.start_node.x, 0, self.start_node.y)
        p2 = glm.vec3(self.end_node.x, 0, self.end_node.y)
        
        direction = p2 - p1
        length = glm.length(direction)
        if length < 0.1: return
        
        dir_norm = glm.normalize(direction)
        
        # 2. Inset Calculation (Gap at intersections)
        # Heuristic: Gap ~= Road Width (or 0.8 * Width)
        inset = self.width * 0.8
        
        # Safety Check: Can we afford this inset?
        if length < (inset * 2.2):
            # Reduced inset for very short roads to prevent inversion
            inset = length * 0.4 
            
        # 3. Calculate Effective Lane Start/End (Center Line Shortened)
        # Shift start forward by inset
        lane_base_start = p1 + dir_norm * inset
        # Shift end backward by inset
        lane_base_end = p2 - dir_norm * inset
        
        # 4. Perpendicular Vector (Right Side)
        # (x, 0, z) -> (-z, 0, x)
        perp = glm.vec3(-dir_norm.z, 0, dir_norm.x)
        
        lane_width = self.width / self.lanes_count 
        offset_dist = self.width * 0.15 
        
        # 5. Generate Lanes (Applied to Shortened Base)
        
        # Forward Lane (Right Side)
        f_start = lane_base_start + perp * offset_dist
        f_end   = lane_base_end + perp * offset_dist
        self.lanes.append(Lane(width=lane_width, waypoints=[f_start, f_end], parent_edge=self))
        
        # Backward Lane (Left Side) - Travel Direction is End -> Start
        # Relative to p1->p2 "Left" is the other side.
        b_start = lane_base_start - perp * offset_dist
        b_end   = lane_base_end - perp * offset_dist
        
        # Backward Lane travels FROM End TO Start
        self.lanes.append(Lane(width=lane_width, waypoints=[b_end, b_start], parent_edge=self))

    def __repr__(self):
        return f"Edge(start={self.start_node.id}, end={self.end_node.id}, w={self.width}, lanes={len(self.lanes)})"


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
        Lane._id_counter = 0

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
