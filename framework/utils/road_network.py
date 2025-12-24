import math
import numpy as np
from pyglm import glm
from framework.shapes.shape import Shape

class RoadNetwork:
    def __init__(self):
        self.nodes = {} # dict of vec2_tuple -> list of (other_node_tuple, width, lanes)
        self.segments = [] # list of (p1, p2, width, lanes)

    def add_segment(self, p1, p2, width, lanes):
        # Snap points to grid/precision to ensure connectivity
        p1_t = self._snap(p1)
        p2_t = self._snap(p2)
        
        if p1_t == p2_t: return
        
        # 1. Check for intersections with existing segments
        # We need to handle:
        # - New segment endpoints lying on existing segments (T-junctions)
        # - New segment crossing existing segments (X-junctions)
        
        # We'll collect all split points for the new segment and existing segments
        # Then we'll apply splits.
        
        # Since splitting modifies the list we are iterating, we have to be careful.
        # Simplest approach:
        # If we find an intersection, split the existing segment, remove it, add two new ones.
        # And split the new segment, and recursively add its parts.
        
        p1_vec = glm.vec2(p1_t)
        p2_vec = glm.vec2(p2_t)
        
        # Check against all existing segments
        # Copy list to allow modification
        current_segments = list(self.segments)
        
        for i, (s1, s2, w, l) in enumerate(current_segments):
            # Check if p1 or p2 lies on s1-s2
            # Check if s1 or s2 lies on p1-p2
            # Check if p1-p2 intersects s1-s2
            
            # Helper to check point on segment
            on_segment = self._is_point_on_segment(p1_vec, s1, s2)
            if on_segment:
                # Split existing segment at p1
                self._split_existing_segment(i, p1_vec)
                # Now the network has changed.
                # We should restart the add_segment process for the current segment
                # because the topology changed.
                # But wait, we might have infinite recursion if we are not careful.
                # p1 is now a node.
                # We just need to continue adding p1-p2.
                # But p1-p2 might still cross other segments.
                # So we should return and call add_segment(p1, p2, ...) again?
                # Yes, but we need to ensure we don't loop.
                # The split reduces the problem size (segments get shorter).
                return self.add_segment(p1, p2, width, lanes)

            on_segment = self._is_point_on_segment(p2_vec, s1, s2)
            if on_segment:
                self._split_existing_segment(i, p2_vec)
                return self.add_segment(p1, p2, width, lanes)
                
            # Check intersection
            intersect, pt = self._get_line_intersection(p1_vec, p2_vec, s1, s2)
            if intersect:
                pt_t = self._snap(pt)
                pt_vec = glm.vec2(pt_t)
                
                if pt_t != p1_t and pt_t != p2_t:
                    # Split existing segment
                    self._split_existing_segment(i, pt_vec)
                    
                    # Split NEW segment into p1-pt and pt-p2
                    self.add_segment(p1, pt, width, lanes)
                    self.add_segment(pt, p2, width, lanes)
                    return

        # If no intersections found, just add it
        self.segments.append((p1_vec, p2_vec, width, lanes))
        
        if p1_t not in self.nodes: self.nodes[p1_t] = []
        if p2_t not in self.nodes: self.nodes[p2_t] = []
        
        # Check if connection already exists to avoid duplicates
        exists = False
        for conn in self.nodes[p1_t]:
            if conn['target'] == p2_t: exists = True; break
        if not exists:
            self.nodes[p1_t].append({'target': p2_t, 'width': width, 'lanes': lanes})
            
        exists = False
        for conn in self.nodes[p2_t]:
            if conn['target'] == p1_t: exists = True; break
        if not exists:
            self.nodes[p2_t].append({'target': p1_t, 'width': width, 'lanes': lanes})

    def _is_point_on_segment(self, p, a, b, tol=0.1):
        # Check if p is close to line segment ab
        # And between a and b
        d_ab = glm.distance(a, b)
        if d_ab < 1e-4: return False
        d_ap = glm.distance(a, p)
        d_pb = glm.distance(p, b)
        
        # Check if on line (triangle inequality equality)
        if abs((d_ap + d_pb) - d_ab) < tol:
            # Check if not endpoints
            if d_ap > tol and d_pb > tol:
                return True
        return False

    def _get_line_intersection(self, p1, p2, p3, p4):
        # Returns (bool, point)
        # Standard line intersection
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = p3.x, p3.y
        x4, y4 = p4.x, p4.y
        
        denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        if denom == 0: return False, None
        
        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
        
        if 0.01 < ua < 0.99 and 0.01 < ub < 0.99: # Strict interior intersection
            x = x1 + ua * (x2 - x1)
            y = y1 + ua * (y2 - y1)
            return True, glm.vec2(x, y)
        return False, None

    def _split_existing_segment(self, index, split_pt):
        # Remove segment at index
        # Add two new segments
        # Update nodes
        
        # We need to find the segment in self.segments
        # But self.segments might have changed if we are recursing?
        # No, we return immediately after calling this.
        # But we need to be sure 'index' is valid.
        # Since we iterate over a copy 'current_segments', and we haven't modified self.segments yet in this call...
        # Wait, self.segments is the master list.
        # We need to find the segment that matches current_segments[index]
        
        target_seg = self.segments[index] # This assumes self.segments matches current_segments order?
        # Yes, if we haven't modified it yet.
        
        # Remove it
        self.segments.pop(index)
        
        s1, s2, w, l = target_seg
        
        # Remove connections from nodes
        s1_t = self._snap(s1)
        s2_t = self._snap(s2)
        
        self._remove_connection(s1_t, s2_t)
        self._remove_connection(s2_t, s1_t)
        
        # Add new segments
        # We call add_segment recursively to handle potential further splits?
        # Or just add them directly?
        # Better to add directly to avoid infinite recursion if logic is slightly off.
        # But adding directly might miss other intersections on the new sub-segments.
        # Safe bet: add directly, but ensure we register nodes.
        
        split_t = self._snap(split_pt)
        split_vec = glm.vec2(split_t)
        
        # Add s1 -> split
        self.segments.append((s1, split_vec, w, l))
        self._add_connection(s1_t, split_t, w, l)
        self._add_connection(split_t, s1_t, w, l)
        
        # Add split -> s2
        self.segments.append((split_vec, s2, w, l))
        self._add_connection(split_t, s2_t, w, l)
        self._add_connection(s2_t, split_t, w, l)

    def _remove_connection(self, n1_t, n2_t):
        if n1_t in self.nodes:
            self.nodes[n1_t] = [c for c in self.nodes[n1_t] if c['target'] != n2_t]

    def _add_connection(self, n1_t, n2_t, w, l):
        if n1_t not in self.nodes: self.nodes[n1_t] = []
        # Check duplicate
        for c in self.nodes[n1_t]:
            if c['target'] == n2_t: return
        self.nodes[n1_t].append({'target': n2_t, 'width': w, 'lanes': l})

    def _snap(self, vec):
        # Round to 1 decimal place to snap close points
        return (round(vec.x, 1), round(vec.y, 1))

    def generate_meshes(self):
        road_shapes = []
        intersection_shapes = []
        road_edges = []
        
        # 1. Compute Intersection Geometry
        # segment_corners = { (p1_t, p2_t): {'p1': (left, right), 'p2': (left, right)} }
        segment_corners = {}
        
        for node_t, connections in self.nodes.items():
            node_pt = glm.vec2(node_t)
            
            # Sort connections by angle
            for conn in connections:
                target_pt = glm.vec2(conn['target'])
                direction = glm.normalize(target_pt - node_pt)
                conn['angle'] = math.atan2(direction.y, direction.x)
                conn['dir'] = direction
                
            connections.sort(key=lambda x: x['angle'])
            
            num_roads = len(connections)
            
            # Calculate corners for this node
            current_node_corners = {} # target_t -> (left, right)
            
            if num_roads < 2:
                # Dead end or single segment start
                # Just use perpendiculars
                conn = connections[0]
                d = conn['dir']
                w = conn['width']
                perp = glm.vec2(-d.y, d.x)
                left = node_pt + perp * (w / 2.0)
                right = node_pt - perp * (w / 2.0)
                current_node_corners[conn['target']] = (left, right)
                
            else:
                # Intersection Polygon
                poly_verts = []
                
                for i in range(num_roads):
                    c1 = connections[i]
                    c2 = connections[(i + 1) % num_roads]
                    
                    # Find corner between C1 (Left) and C2 (Right)
                    # Note: C1 is at angle i, C2 at i+1.
                    # We want the intersection of C1's Left edge and C2's Right edge.
                    
                    w1 = c1['width']
                    w2 = c2['width']
                    d1 = c1['dir']
                    d2 = c2['dir']
                    
                    # Normals
                    n1_left = glm.vec2(-d1.y, d1.x)
                    n2_right = glm.vec2(d2.y, -d2.x)
                    
                    p1_s = node_pt + n1_left * (w1 / 2.0)
                    p2_s = node_pt + n2_right * (w2 / 2.0)
                    
                    # Intersect
                    det = d1.x * (-d2.y) - d1.y * (-d2.x)
                    
                    # Check for parallel or near-parallel (obtuse angle)
                    # d1 points INTO node, d2 points OUT of node?
                    # No, d1 and d2 are edge directions.
                    # If roads are 180 deg apart, d1 approx -d2.
                    # So dot(d1, d2) approx -1.
                    
                    dot = glm.dot(d1, d2)
                    
                    if abs(det) < 1e-3 or dot < -0.95:
                        # Parallel or Obtuse (Straight-ish)
                        # Just use the start point of the first edge
                        corner = p1_s
                    else:
                        delta = p2_s - p1_s
                        t = (delta.x * (-d2.y) - delta.y * (-d2.x)) / det
                        corner = p1_s + d1 * t
                        
                        # Clamp
                        if glm.distance(corner, node_pt) > max(w1, w2) * 1.5:
                             corner = node_pt + glm.normalize(corner - node_pt) * max(w1, w2) * 1.5
                    
                    poly_verts.append(corner)
                    
                    # Assign to segments
                    # This corner is C1's Left-End corner (at this node)
                    # And C2's Right-Start corner (at this node)
                    
                    if c1['target'] not in current_node_corners: current_node_corners[c1['target']] = [None, None]
                    current_node_corners[c1['target']][0] = corner # Left
                    
                    if c2['target'] not in current_node_corners: current_node_corners[c2['target']] = [None, None]
                    current_node_corners[c2['target']][1] = corner # Right

                # Create Intersection Mesh
                shape = Shape()
                verts = []
                norms = []
                cols = []
                inds = []
                
                center = glm.vec4(node_pt.x, 0.051, node_pt.y, 1.0) # Slightly higher than roads? Or same?
                # Intersections should be same height as highest road?
                # Let's use 0.056 (above 0.055)
                y_inter = 0.056
                col = glm.vec4(0.2, 0.2, 0.2, 1.0)
                
                verts.append(glm.vec4(node_pt.x, y_inter, node_pt.y, 1.0))
                norms.append(glm.vec3(0,1,0))
                cols.append(col)
                
                for v in poly_verts:
                    verts.append(glm.vec4(v.x, y_inter, v.y, 1.0))
                    norms.append(glm.vec3(0,1,0))
                    cols.append(col)
                    
                for i in range(len(poly_verts)):
                    inds.extend([0, i+1, (i+1)%len(poly_verts) + 1])
                    
                shape.vertices = np.array([v.to_list() for v in verts], dtype=np.float32)
                shape.normals = np.array([n.to_list() for n in norms], dtype=np.float32)
                shape.uvs = np.zeros((len(verts), 2), dtype=np.float32)
                shape.colors = np.array([c.to_list() for c in cols], dtype=np.float32)
                shape.indices = np.array(inds, dtype=np.uint32)
                intersection_shapes.append(shape)

            # Store in global map
            for target_t, (left, right) in current_node_corners.items():
                key = tuple(sorted((node_t, target_t)))
                if key not in segment_corners: segment_corners[key] = {}
                
                # Identify if node_t is p1 or p2 in the key
                if node_t == key[0]:
                    segment_corners[key]['p1'] = (left, right)
                else:
                    segment_corners[key]['p2'] = (left, right)

        # 2. Generate Road Segments
        for (p1_t, p2_t), corners in segment_corners.items():
            if 'p1' not in corners or 'p2' not in corners: continue
            
            p1_left, p1_right = corners['p1']
            p2_left, p2_right = corners['p2']
            
            if not p1_left or not p1_right or not p2_left or not p2_right: continue
            
            # Retrieve width/lanes (stored in nodes)
            # Just grab from one of the nodes
            width = 14.0
            lanes = 4
            for conn in self.nodes[p1_t]:
                if conn['target'] == p2_t:
                    width = conn['width']
                    lanes = conn['lanes']
                    break
            
            # Determine Y
            if lanes >= 6: y = 0.055
            elif lanes >= 4: y = 0.052
            else: y = 0.050
            
            # Build Mesh
            # Quad: P1_Left, P1_Right, P2_Right, P2_Left
            # Note: P2 corners are stored relative to P2->P1?
            # In the loop above:
            # current_node_corners[target] = (Left, Right)
            # Left is relative to Node->Target.
            # So P1_Left is Left of P1->P2.
            # P2_Left is Left of P2->P1.
            # So P2_Left is on the "Right" side of P1->P2.
            # So the quad is: P1_Left -> P1_Right -> P2_Left -> P2_Right?
            # Let's trace:
            # P1->P2 direction.
            # P1_Left is on Left. P1_Right is on Right.
            # P2_Left is on Left of P2->P1 (which is Right of P1->P2).
            # P2_Right is on Right of P2->P1 (which is Left of P1->P2).
            # So the quad loop (CCW) is:
            # P1_Right -> P2_Left -> P2_Right -> P1_Left
            
            v1 = glm.vec4(p1_right.x, y, p1_right.y, 1.0)
            v2 = glm.vec4(p2_left.x, y, p2_left.y, 1.0)
            v3 = glm.vec4(p2_right.x, y, p2_right.y, 1.0)
            v4 = glm.vec4(p1_left.x, y, p1_left.y, 1.0)
            
            shape = Shape()
            verts = [v1, v2, v3, v4]
            norms = [glm.vec3(0,1,0)] * 4
            cols = [glm.vec4(0.2, 0.2, 0.2, 1.0)] * 4
            inds = [0, 1, 2, 0, 2, 3]
            
            
            shape.vertices = np.array([v.to_list() for v in verts], dtype=np.float32)
            shape.normals = np.array([n.to_list() for n in norms], dtype=np.float32)
            shape.uvs = np.zeros((len(verts), 2), dtype=np.float32)
            shape.colors = np.array([c.to_list() for c in cols], dtype=np.float32)
            shape.indices = np.array(inds, dtype=np.uint32)
            road_shapes.append(shape)
            
            # Record Edges for Street Lights
            # Edge 1: P1_Right -> P2_Left
            edge1_dir = p2_left - p1_right
            if glm.length(edge1_dir) > 0.1:
                edge1_norm = glm.normalize(glm.vec2(edge1_dir.y, -edge1_dir.x))
                road_edges.append({
                    'start': glm.vec3(p1_right.x, y, p1_right.y),
                    'end': glm.vec3(p2_left.x, y, p2_left.y),
                    'normal': glm.vec3(edge1_norm.x, 0, edge1_norm.y)
                })

            # Edge 2: P2_Right -> P1_Left
            edge2_dir = p1_left - p2_right
            if glm.length(edge2_dir) > 0.1:
                edge2_norm = glm.normalize(glm.vec2(edge2_dir.y, -edge2_dir.x))
                road_edges.append({
                    'start': glm.vec3(p2_right.x, y, p2_right.y),
                    'end': glm.vec3(p1_left.x, y, p1_left.y),
                    'normal': glm.vec3(edge2_norm.x, 0, edge2_norm.y)
                })
            
        return road_shapes + intersection_shapes, road_edges
