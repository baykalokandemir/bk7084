import math
import random
from framework.utils.city_graph import CityGraph, Node, Edge
from framework.utils.polygon import Polygon
from framework.utils.building import Building
from pyglm import glm

class TrafficGraphBuilder:
    """
    Traffic Graph Builder.
    Converts a spatial layout (BSP) into a Node/Edge graph for traffic simulation.
    Also handles zoning/building placement along the graph edges.
    """
    def __init__(self):
        self.graph = CityGraph()

    def build_graph_from_layout(self, layout_generator):
        """
        Converts road network from layout generator into traffic graph.
        
        Ingests road segments from AdvancedCityGenerator's road network,
        creates nodes at segment endpoints (with spatial hashing to merge
        duplicates), creates bidirectional edges between nodes, generates
        intersection connection curves for smooth lane transitions, and
        calculates traffic signal phases for each intersection.
        
        Args:
            layout_generator: AdvancedCityGenerator instance with road_network
        
        Produces:
            - self.graph: Populated CityGraph with nodes, edges, and lanes
            - Intersection curves stored in node.connections
            - Traffic signal phases in node.phases
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
                # Spatial hashing: round to 10cm precision to merge nearby endpoints
                # This prevents duplicate nodes from floating-point inaccuracies
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

    def audit_graph(self, print_no_outlet=False):
        """
        Audits graph connectivity and identifies problematic lanes.
        
        Detects dead-end lanes (lanes with no outgoing connections at their
        destination node) and loop edges (edges connecting a node to itself).
        Stores dead-end lanes in self.dead_end_lanes for visualization or
        debugging purposes.
        
        Args:
            print_no_outlet: If True, prints all dead-end lane IDs to console
        
        Produces:
            - self.dead_end_lanes: List of Lane objects with no outlets
            - Console output summarizing audit results
        """
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
                
                if not lane.waypoints: continue
                
                # Determine which node is the exit for this lane
                # Forward lanes exit at edge.end_node, backward lanes at edge.start_node
                # We detect this by checking which node is closest to the last waypoint
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
        if (print_no_outlet):
            for i, lane in enumerate(self.dead_end_lanes):
                print(f"[FAIL] Lane {lane.id} has no outlets.")