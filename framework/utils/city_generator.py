import math
import random
from framework.utils.city_graph import CityGraph, Node, Edge
from framework.utils.polygon import Polygon
from framework.utils.building import Building
from pyglm import glm

class CityGenerator:
    """
    Traffic Graph Builder.
    Converts a spatial layout (BSP) into a Node/Edge graph for traffic simulation.
    Also handles zoning/building placement along the graph edges.
    """
    def __init__(self):
        self.graph = CityGraph()
        self.buildings = []

    def build_graph_from_layout(self, layout_generator):
        """
        Ingests the road network from a layout generator (e.g., AdvancedCityGenerator).
        """
        self.graph.clear()
        rn = layout_generator.road_network
        raw_segments = getattr(rn, 'segments', [])

        print(f"DEBUG: Processing {len(raw_segments)} raw segments from layout...")

        # Spatial Hash: Key = (round(x,1), round(y,1)) -> Val = Node Object
        node_map = {} 
        edges_created = 0

        for i, seg in enumerate(raw_segments):
            # STRICT UNPACKING for (p1, p2, width, lanes)
            if isinstance(seg, tuple) and len(seg) >= 2:
                # Assuming (p1, p2, width, lanes) or (p1, p2, width)
                p1_raw = seg[0]
                p2_raw = seg[1]
                width = seg[2] if len(seg) > 2 else 10.0
            else:
                if isinstance(seg, dict):
                     p1_raw = seg.get('start')
                     p2_raw = seg.get('end')
                     width = seg.get('width', 10.0)
                else:
                    continue

            if p1_raw is None or p2_raw is None:
                continue

            # Convert to simple (x, y) tuples for safety
            v1_x = float(getattr(p1_raw, 'x', p1_raw[0]))
            v1_y = float(getattr(p1_raw, 'y', p1_raw[1]))
            v2_x = float(getattr(p2_raw, 'x', p2_raw[0]))
            v2_y = float(getattr(p2_raw, 'y', p2_raw[1]))
            
            v1 = (v1_x, v1_y)
            v2 = (v2_x, v2_y)

            # 1. Skip zero-length segments
            dist_sq = (v2[0]-v1[0])**2 + (v2[1]-v1[1])**2
            if dist_sq < 0.1: 
                continue

            # 2. Get/Create Nodes (Spatial Hashing)
            def get_node(v):
                # Key is rounded to 1 decimal place (10cm precision)
                key = (round(v[0], 1), round(v[1], 1))
                if key not in node_map:
                    node_map[key] = self.graph.add_node(key[0], key[1])
                return node_map[key]

            n1 = get_node(v1)
            n2 = get_node(v2)

            # 3. Create Edge
            if n1 != n2:
                self.graph.add_edge(n1, n2, width=float(width))
                edges_created += 1

        # 4. Generate Intersection Connections
        print("DEBUG: Generating Intersection Curves...")
        for node in self.graph.nodes:
            node.generate_connections()
            node.calculate_phases() # [NEW] Traffic Lights
            
        # 5. [NEW] Audit Graph
        self.audit_graph()

        print(f"DEBUG: Graph Built. Nodes: {len(self.graph.nodes)} (Merged from raw endpoints). Edges: {edges_created}")

    def audit_graph(self):
        print("DEBUG: Auditing Graph Connectivity...")
        self.dead_end_lanes = []
        loop_count = 0
        
        for edge in self.graph.edges:
            if not hasattr(edge, 'lanes'): continue
            
            # Check Looping Edge
            if edge.start_node == edge.end_node:
                loop_count += 1
                
            for lane in edge.lanes:
                end_node = edge.end_node
                
                # If Lane is Backward (odd index usually, or stored in list), direction matters.
                # In Edge.generate_lanes:
                # Lanes 0..N-1 are Forward (Start->End)
                # Lanes N..M are Backward (End->Start)
                # Wait, my Edge logic splits them.
                # If lane is in 'forward' set, end_node is edge.end_node.
                # If lane is in 'backward' set, end_node is edge.start_node.
                
                # Let's rely on Lane Waypoints?
                # Waypoints are ordered travel direction. 
                # So lane.waypoints[-1] is near the "Exit Node".
                # But which Node object is that?
                # Lane doesn't store "Exit Node" reference directly, only Parent Edge.
                
                # Recalculate which node is the exit:
                # Forward Lane: exit is edge.end_node
                # Backward Lane: exit is edge.start_node
                
                # Check Edge.lanes structure:
                # It currently generates a flat list. But how do we know which is Fwd/Bwd?
                # We can check distance from last waypoint to nodes.
                
                if not lane.waypoints: continue
                last_wp = lane.waypoints[-1]
                
                n1_pos = glm.vec3(edge.start_node.x, 0, edge.start_node.y)
                n2_pos = glm.vec3(edge.end_node.x, 0, edge.end_node.y)
                
                d1 = glm.distance(last_wp, n1_pos)
                d2 = glm.distance(last_wp, n2_pos)
                
                exit_node = edge.start_node if d1 < d2 else edge.end_node
                
                # Check connections starting from this lane
                # keys are (from_id, to_id)
                outgoing_count = 0
                for k in exit_node.connections.keys():
                    if k[0] == lane.id:
                        outgoing_count += 1
                        
                if outgoing_count == 0:
                    self.dead_end_lanes.append(lane)
                    
        print(f"[AUDIT] Found {len(self.dead_end_lanes)} lanes with no outlets.")
        if loop_count > 0:
            print(f"[AUDIT] Found {loop_count} zero-length loop edges.")
            
        # Log first few
        for i, lane in enumerate(self.dead_end_lanes[:5]):
            print(f"[FAIL] Lane {lane.id} has no outlets.")

    def generate_buildings(self):
        """
        Populate the city with buildings along the road edges.
        """
        self.buildings = []
        
        for edge in self.graph.edges:
            # 1. Edge Vector & Normal
            p1 = glm.vec2(edge.start_node.x, edge.start_node.y)
            p2 = glm.vec2(edge.end_node.x, edge.end_node.y)
            
            vec = p2 - p1
            length = glm.length(vec)
            if length < 1.0: continue
            
            direction = glm.normalize(vec)
            normal = glm.vec2(-direction.y, direction.x) # Perpendicular
            
            # Simple shrinking
            start_dist = 2.0 
            end_dist = length - 2.0
            
            if end_dist <= start_dist: continue
            
            # 3. Iterate along edge
            curr_dist = start_dist
            
            while curr_dist + 10.0 < end_dist: # Ensure fits
                # Current position on road center
                pos = p1 + direction * curr_dist
                
                frontage_dist = (edge.width / 2) + 2.0
                
                # We place two buildings: Left (-Normal) and Right (+Normal)
                for side in [-1, 1]:
                    # Randomize Lot Size
                    width = random.uniform(10.0, 14.0)
                    depth = random.uniform(12.0, 20.0)
                    
                    # Calculate Center
                    center_dist = frontage_dist + depth / 2.0
                    center_pos = pos + (normal * side) * center_dist
                    
                    b_forward = normal * side
                    b_right = direction
                    
                    # Corners
                    half_w = width / 2.0
                    half_d = depth / 2.0
                    
                    c1 = center_pos - b_right * half_w - b_forward * half_d
                    c2 = center_pos + b_right * half_w - b_forward * half_d
                    c3 = center_pos + b_right * half_w + b_forward * half_d
                    c4 = center_pos - b_right * half_w + b_forward * half_d
                    
                    poly = Polygon([c1, c2, c3, c4])
                    
                    # Create Building Instance
                    height = random.uniform(20.0, 60.0)
                    
                    # Random Style
                    style = {
                        "color": glm.vec4(random.random(), random.random(), random.random(), 1.0),
                        "stepped": random.random() < 0.4,
                        "window_ratio": random.uniform(0.4, 0.7)
                    }
                    
                    b = Building(poly, height, style)
                    self.buildings.append(b.generate())
                
                # Advance
                curr_dist += width + random.uniform(2.0, 5.0) # Gap between buildings