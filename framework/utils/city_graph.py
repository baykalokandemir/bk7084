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

    def __repr__(self):
        return f"Lane(id={self.id}, w={self.width})"

def get_bezier_points(p0, p1, p2, p3, steps=10):
    points = []
    for i in range(steps + 1):
        t = i / steps
        u = 1 - t
        tt = t * t
        uu = u * u
        uuu = uu * u
        ttt = tt * t
        
        # p = u^3*P0 + 3*u^2*t*P1 + 3*u*t^2*P2 + t^3*P3
        p = (p0 * uuu) + (p1 * (3 * uu * t)) + (p2 * (3 * u * tt)) + (p3 * ttt)
        points.append(p)
    return points

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

    def generate_connections(self):
        """
        Generates curved paths between incoming and outgoing lanes.
        """
        self.connections = {}
        
        # 1. Identify Incoming and Outgoing Lanes
        incoming = [] # List of (Lane, DirectionVec3)
        outgoing = [] # List of (Lane, DirectionVec3)
        
        for edge in self.edges:
            if not hasattr(edge, 'lanes'): continue
            
            p1 = glm.vec3(edge.start_node.x, 0, edge.start_node.y)
            p2 = glm.vec3(edge.end_node.x, 0, edge.end_node.y)
            edge_dir = glm.normalize(p2 - p1)
            
            # Logic:
            # Lane 0 is Forward (p1->p2)
            # Lane 1 is Backward (p2->p1)
            
            if edge.start_node == self:
                # We are at p1.
                # Traffic LEAVING us goes to p2 (Forward, Lane 0).
                # Traffic ARRIVING at us comes from p2 (Backward, Lane 1).
                
                # Outgoing: Lane 0
                if len(edge.lanes) > 0:
                    outgoing.append((edge.lanes[0], edge_dir))
                
                # Incoming: Lane 1
                if len(edge.lanes) > 1:
                    incoming.append((edge.lanes[1], -edge_dir)) # Dir toward self
                    
            elif edge.end_node == self:
                # We are at p2.
                # Traffic LEAVING us goes to p1 (Backward, Lane 1).
                # Traffic ARRIVING at us comes from p1 (Forward, Lane 0).
                
                # Incoming: Lane 0
                if len(edge.lanes) > 0:
                    incoming.append((edge.lanes[0], edge_dir)) # Dir toward self
                
                # Outgoing: Lane 1
                if len(edge.lanes) > 1:
                    outgoing.append((edge.lanes[1], -edge_dir))

        # 2. Connect All valid pairs
        for in_lane, in_dir in incoming:
            for out_lane, out_dir in outgoing:
                if in_lane.parent_edge == out_lane.parent_edge:
                    continue # Don't U-Turn immediately (optional)
                
                # Determine turn type by angle
                # Cross product Y component tells Left vs Right
                # Dot product tells Straight vs Reverse
                
                # angle 0 -> Straight (Dot ~ 1)
                # angle -90 -> Right (Cross.y > 0? No, let's check)
                # angle +90 -> Left
                
                dot = glm.dot(in_dir, out_dir)
                cross_y = (in_dir.z * out_dir.x) - (in_dir.x * out_dir.z)
                
                # Heuristics
                is_straight = dot > 0.5
                is_right = cross_y > 0.1 # Right Hand Rule: X cross Z = -Y. 
                # Wait, if Forward=(0,-1) and Right=(1,0). 
                # x=0,z=-1. x=1,z=0.
                # (z*x') - (x*z') = (-1*1) - (0*0) = -1. So CrossY < 0 is Right?
                # Let's rely on standard: Right turn means out_dir is roughly -90 deg from in_dir.
                
                # We connect everything for now! Cars choose paths.
                # Just need to generate valid geometry.
                
                p0 = in_lane.waypoints[-1]
                p3 = out_lane.waypoints[0]
                
                dist = glm.length(p3 - p0)
                if dist < 0.1: continue
                
                # Control Points
                # P1: Extend incoming tangent
                p1 = p0 + (in_dir * (dist * 0.5))
                # P2: Extend outgoing tangent backwards
                p2 = p3 - (out_dir * (dist * 0.5))
                
                curve = get_bezier_points(p0, p1, p2, p3, steps=8)
                
                self.connections[(in_lane.id, out_lane.id)] = curve

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
