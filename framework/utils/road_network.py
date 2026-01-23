import math
import numpy as np
from pyglm import glm
from framework.shapes.shape import Shape

class RoadNetwork:
    def __init__(self):
        self.nodes = {} # dict of vec2_tuple -> list of (other_node_tuple, width, lanes)
        self.segments = [] # list of (p1, p2, width, lanes)

    '''
        We need to handle:
        - New segment endpoints lying on existing segments (T-junctions)
        - New segment crossing existing segments (X-junctions)
        
        We'll collect all split points for the new segment and existing segments
        Then we'll apply splits.
        If we find an intersection, split the existing segment, remove it, add two new ones.
        And split the new segment, and recursively add its parts.

        Void function, returns None.
    '''
    def add_segment(self, p1, p2, width, lanes):
        # Snap points to grid/precision to ensure connectivity
        p1_t = self._snap(p1)
        p2_t = self._snap(p2)
        
        if p1_t == p2_t: return # Road has length 0?

        # 2d vectors
        p1_vec = glm.vec2(p1_t)
        p2_vec = glm.vec2(p2_t)
        
        # Check against all existing segments on a copy of the segments list
        current_segments = list(self.segments)
        
        for i, (s1, s2, w, l) in enumerate(current_segments):
            
            # Check if p1 or p2 lies on s1-s2 (T-junction)
            on_segment = self._is_point_on_segment(p1_vec, s1, s2)
            if on_segment:
                self._split_existing_segment(i, p1_vec)
                return self.add_segment(p1, p2, width, lanes)

            # Check if s1 or s2 lies on p1-p2 (T-junction)
            on_segment = self._is_point_on_segment(p2_vec, s1, s2)
            if on_segment:
                self._split_existing_segment(i, p2_vec)
                return self.add_segment(p1, p2, width, lanes)
                
            # Check if p1-p2 intersects s1-s2 (X-junction)
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

    '''
        Triangle inequality equality check: distance(a, b) = distance(a, p) + distance(p, b)
        Returns True if p is on the line segment ab.
    '''
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

    '''
        Checks if two lines intersect with "Cramer's Rule". Thank you stackoverflow.

        Returns intersection point of two lines.
        Returns (True, point) if intersection exists, (False, None) otherwise.
    '''
    def _get_line_intersection(self, p1, p2, p3, p4):

        # unpack vectors
        x1, y1 = p1.x, p1.y
        x2, y2 = p2.x, p2.y
        x3, y3 = p3.x, p3.y
        x4, y4 = p4.x, p4.y
        
        denom = (y4 - y3) * (x2 - x1) - (x4 - x3) * (y2 - y1)
        if denom == 0: return False, None
        
        ua = ((x4 - x3) * (y1 - y3) - (y4 - y3) * (x1 - x3)) / denom
        ub = ((x2 - x1) * (y1 - y3) - (y2 - y1) * (x1 - x3)) / denom
        
        # Ignore intersections at/near endpoints
        if 0.01 < ua < 0.99 and 0.01 < ub < 0.99:
            x = x1 + ua * (x2 - x1)
            y = y1 + ua * (y2 - y1)
            return True, glm.vec2(x, y)
        return False, None

    '''
        Splits an existing segment into two at a given point.
        Removes the original segment and adds two new ones.
        Updates the nodes to reflect the new connections.

        Void function, returns None.
    '''
    def _split_existing_segment(self, index, split_pt):

        target_seg = self.segments[index]
        self.segments.pop(index)
        # unpack segment
        s1, s2, w, l = target_seg
        
        # Remove connections from nodes
        s1_t = self._snap(s1)
        s2_t = self._snap(s2)
        
        self._remove_connection(s1_t, s2_t)
        self._remove_connection(s2_t, s1_t)
        
        # Add new segments
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

    '''
        Removes a connection from the nodes.
        Void function, returns None.
    '''
    def _remove_connection(self, n1_t, n2_t):
        if n1_t in self.nodes:
            self.nodes[n1_t] = [c for c in self.nodes[n1_t] if c['target'] != n2_t]

    '''
        Adds a connection to the nodes.
        Void function, returns None.
    '''
    def _add_connection(self, n1_t, n2_t, w, l):
        if n1_t not in self.nodes: self.nodes[n1_t] = []
        # Check duplicate
        for c in self.nodes[n1_t]:
            if c['target'] == n2_t: return
        self.nodes[n1_t].append({'target': n2_t, 'width': w, 'lanes': l})

    '''
        Snaps a point to the nearest grid point.
        Returns the snapped point.
    '''
    def _snap(self, vec):
        # Round to 1 decimal place to snap close points
        return (round(vec.x, 1), round(vec.y, 1))

    '''
        Generates the meshes for the road network.
        Returns a list of road shapes, intersection shapes, and road edges.
    '''
    def generate_meshes(self):
        road_shapes = []
        intersection_shapes = []
        road_edges = []
        
        # Compute Intersection Geometry
        # segment_corners = { (p1_t, p2_t): {'p1': (left, right), 'p2': (left, right)} }
        segment_corners = {}
        
        # For each node
        for node_t, connections in self.nodes.items():
            node_pt = glm.vec2(node_t)
            
            # Sort all roads connected to this node by angle
            # This is important because we want to build the mesh around the intersection 
            # in a consistent order, without the "edge"s crossing over each other
            for conn in connections:
                target_pt = glm.vec2(conn['target'])
                direction = glm.normalize(target_pt - node_pt)
                conn['angle'] = math.atan2(direction.y, direction.x)
                conn['dir'] = direction
                
            connections.sort(key=lambda x: x['angle'])
            
            num_roads = len(connections)
            
            # Calculate corners for this node
            current_node_corners = {} # target_t -> (left, right)
            
            # Intersection only has 1 segment, i.e. dead end. just make the road itself, pointed at the 
            # 'dir' of the connection and with width 'width' specified in the datastructure. 
            if num_roads < 2:
                conn = connections[0]
                d = conn['dir']
                w = conn['width']
                perp = glm.vec2(-d.y, d.x)
                left = node_pt + perp * (w / 2.0)
                right = node_pt - perp * (w / 2.0)
                current_node_corners[conn['target']] = (left, right)
            # Intersection has multiple segments.
            else:
                poly_verts = []
                
                for i in range(num_roads):
                    # connections is sorted by angle, so i and i+1 are neighboring segments
                    c1 = connections[i]
                    c2 = connections[(i + 1) % num_roads]
                    
                    w1 = c1['width']
                    w2 = c2['width']
                    d1 = c1['dir']
                    d2 = c2['dir']
                    
                    # Normals
                    n1_left = glm.vec2(-d1.y, d1.x) # points out of the left side of c1
                    n2_right = glm.vec2(d2.y, -d2.x) # points out of the right side of c2
                    
                    # start points of the segments, half width away from the center
                    p1_s = node_pt + n1_left * (w1 / 2.0)
                    p2_s = node_pt + n2_right * (w2 / 2.0)
                    
                    # Intersection point
                    det = d1.x * (-d2.y) - d1.y * (-d2.x) # 0 / very small if lines are parallel
                    dot = glm.dot(d1, d2) # angle between roads, -1 if they are opposite
                    
                    if abs(det) < 1e-3 or dot < -0.95:
                        # edges are parallel, will never intersect
                        # Just use the start point of the first edge
                        corner = p1_s
                    else:
                        # Cramer's rule again
                        delta = p2_s - p1_s
                        t = (delta.x * (-d2.y) - delta.y * (-d2.x)) / det
                        corner = p1_s + d1 * t
                        
                        # Clamp to the width of the road
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
                
                center = glm.vec4(node_pt.x, 0.051, node_pt.y, 1.0)
                # slightly different z height to avoid buggy visuals
                y_inter = 0.056
                col = glm.vec4(0.2, 0.2, 0.2, 1.0)
                
                # Triangle fan build 
                # First vertex is the center of the intersection. 
                verts.append(glm.vec4(node_pt.x, y_inter, node_pt.y, 1.0))
                norms.append(glm.vec3(0,1,0))
                cols.append(col)
                
                # By extension of the connections array, poly_verts is also sorted by angle
                # Rest of the vertices are the corners of the intersection polygon
                for v in poly_verts:
                    verts.append(glm.vec4(v.x, y_inter, v.y, 1.0))
                    norms.append(glm.vec3(0,1,0))
                    cols.append(col)
                    
                for i in range(len(poly_verts)):
                    inds.extend([0, i+1, (i+1)%len(poly_verts) + 1])
                    
                # turn everything into np arrays because that sounds like a good thing to do
                shape.vertices = np.array([v.to_list() for v in verts], dtype=np.float32)
                shape.normals = np.array([n.to_list() for n in norms], dtype=np.float32)
                shape.uvs = np.zeros((len(verts), 2), dtype=np.float32) # texture coordinates are set to 9 / black
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

        # Generate road segments
        # we are no longer using the center points, but the corners we calculated above
        for (p1_t, p2_t), corners in segment_corners.items():
            if 'p1' not in corners or 'p2' not in corners: continue
            
            # "left" and "right" corners are relative to the direction of the segment
            p1_left, p1_right = corners['p1']
            p2_left, p2_right = corners['p2']
            
            # abort if any of the corners are missing
            if not p1_left or not p1_right or not p2_left or not p2_right: continue
            
            # width and lanes are stored in the connections, however this is now a bit 
            # old since we gave up on 4/6 lane roads
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

            v1 = glm.vec4(p1_right.x, y, p1_right.y, 1.0)
            v2 = glm.vec4(p2_left.x, y, p2_left.y, 1.0)
            v3 = glm.vec4(p2_right.x, y, p2_right.y, 1.0)
            v4 = glm.vec4(p1_left.x, y, p1_left.y, 1.0)
            
            shape = Shape()
            verts = [v1, v2, v3, v4]
            norms = [glm.vec3(0,1,0)] * 4
            cols = [glm.vec4(0.2, 0.2, 0.2, 1.0)] * 4
            inds = [0, 1, 2, 0, 2, 3]
            
            # turn everything into np arrays
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
