import numpy as np
from pyglm import glm
from framework.shapes.shape import Shape

class Polygon:
    def __init__(self, vertices):
        """
        vertices: List of glm.vec2 or (x, z) tuples representing the polygon corners in order (CCW).
        """
        self.vertices = [glm.vec2(v) if not isinstance(v, glm.vec2) else v for v in vertices]

    def is_convex(self):
        # TODO: Implement convexity check if needed. For now assume convex.
        return True

    def triangulate(self):
        """
        Returns a list of indices (0-based relative to self.vertices) forming triangles.
        Assumes Convex Polygon (Triangle Fan).
        """
        indices = []
        if len(self.vertices) < 3:
            return indices
            
        # Triangle Fan from vertex 0
        # 0, 1, 2
        # 0, 2, 3
        # ...
        for i in range(1, len(self.vertices) - 1):
            indices.extend([0, i, i + 1])
            
        return indices

    def extrude(self, height):
        """
        Extrudes the polygon into a 3D prism.
        Returns a Shape object (or data compatible with Shape).
        """
        # We will return a Shape-like object or just populate a generic Shape
        shape = Shape()
        
        all_vertices = []
        all_normals = []
        all_uvs = [] # Optional
        all_indices = []
        
        # 1. Top Face (y = height)
        # Vertices are the polygon vertices at y=height
        top_start_idx = len(all_vertices)
        for v in self.vertices:
            all_vertices.append(glm.vec4(v.x, height, v.y, 1.0))
            all_normals.append(glm.vec3(0, 1, 0))
            all_uvs.append(glm.vec2(v.x, v.y)) # Planar mapping
            
        # Triangulate Top
        top_indices = self.triangulate()
        for idx in top_indices:
            all_indices.append(top_start_idx + idx)
            
        # 2. Bottom Face (y = 0)
        # Vertices are the polygon vertices at y=0
        # Winding order needs to be reversed for bottom face to point down?
        # Or we just use normal (0, -1, 0) and standard winding (0, 2, 1)
        bot_start_idx = len(all_vertices)
        for v in self.vertices:
            all_vertices.append(glm.vec4(v.x, 0, v.y, 1.0))
            all_normals.append(glm.vec3(0, -1, 0))
            all_uvs.append(glm.vec2(v.x, v.y))
            
        # Triangulate Bottom (Reverse winding: 0, i+1, i)
        # The triangulate method gives 0, i, i+1.
        # We want 0, i+1, i for bottom face to face down.
        for i in range(0, len(top_indices), 3):
            # top_indices[i], top_indices[i+1], top_indices[i+2]
            # We want bot_start + idx
            v1 = top_indices[i]
            v2 = top_indices[i+1]
            v3 = top_indices[i+2]
            all_indices.extend([bot_start_idx + v1, bot_start_idx + v3, bot_start_idx + v2])
            
        # 3. Side Walls
        # For each edge (i, i+1), create a quad
        n_verts = len(self.vertices)
        for i in range(n_verts):
            curr_v = self.vertices[i]
            next_v = self.vertices[(i + 1) % n_verts]
            
            # Calculate face normal
            # Edge vector
            edge = next_v - curr_v
            # Normal is perpendicular to edge in 2D (x, z) -> (z, -x)?
            # Or just cross product in 3D.
            # edge3 = (edge.x, 0, edge.y)
            # up = (0, 1, 0)
            # normal = cross(up, edge3) ? No, cross(edge3, up) -> (z, 0, -x) ?
            
            # Let's do cross product
            p1 = glm.vec3(curr_v.x, 0, curr_v.y)
            p2 = glm.vec3(next_v.x, 0, next_v.y)
            edge_vec = p2 - p1
            normal = glm.normalize(glm.cross(edge_vec, glm.vec3(0, 1, 0)))
            # Wait, cross(edge, up).
            # If edge is along X (1,0,0), up is (0,1,0). Cross is (0,0,1) -> Z. Correct.
            # If edge is along -X (-1,0,0), up is (0,1,0). Cross is (0,0,-1) -> -Z. Correct.
            # But we want outward facing normal.
            # If polygon is CCW, edge goes counter-clockwise.
            # Right hand rule: edge x up points INWARDS?
            # Let's check.
            # Square: (0,0) -> (1,0). Edge (1,0,0). Normal should be (0,0,-1) (facing -Z? No, facing -Z is "out" if center is 0.5, 0.5? No.)
            # If vertices are (0,0), (1,0), (1,1), (0,1).
            # Edge 1: (0,0)->(1,0). Edge=(1,0,0). Center is (0.5, 0.5). Normal should be (0,0,-1).
            # Cross((1,0,0), (0,1,0)) = (0,0,1). This is +Z. This is INWARD.
            # So we need cross(up, edge).
            # Cross((0,1,0), (1,0,0)) = (0,0,-1). Correct.
            
            normal = glm.normalize(glm.cross(glm.vec3(0, 1, 0), edge_vec))
            
            # 4 Vertices for the quad
            # Top-Left (curr, top)
            # Top-Right (next, top)
            # Bot-Right (next, bot)
            # Bot-Left (curr, bot)
            
            # We need unique vertices for flat shading (normals are different from top/bot)
            base_idx = len(all_vertices)
            
            # TL
            all_vertices.append(glm.vec4(curr_v.x, height, curr_v.y, 1.0))
            all_normals.append(normal)
            all_uvs.append(glm.vec2(0, 1))
            
            # TR
            all_vertices.append(glm.vec4(next_v.x, height, next_v.y, 1.0))
            all_normals.append(normal)
            all_uvs.append(glm.vec2(1, 1))
            
            # BR
            all_vertices.append(glm.vec4(next_v.x, 0, next_v.y, 1.0))
            all_normals.append(normal)
            all_uvs.append(glm.vec2(1, 0))
            
            # BL
            all_vertices.append(glm.vec4(curr_v.x, 0, curr_v.y, 1.0))
            all_normals.append(normal)
            all_uvs.append(glm.vec2(0, 0))
            
            # Indices (CCW)
            # TL, BL, BR
            # TL, BR, TR
            all_indices.extend([base_idx, base_idx+3, base_idx+2])
            all_indices.extend([base_idx, base_idx+2, base_idx+1])

        # Populate Shape
        shape.vertices = np.array([v.to_list() for v in all_vertices], dtype=np.float32)
        shape.normals = np.array([n.to_list() for n in all_normals], dtype=np.float32)
        shape.uvs = np.array([u.to_list() for u in all_uvs], dtype=np.float32)
        shape.indices = np.array(all_indices, dtype=np.uint32)
        # Colors? Default white
        shape.colors = np.array([[1.0, 1.0, 1.0, 1.0]] * len(all_vertices), dtype=np.float32)
        
        return shape

    def split(self, split_point, split_dir):
        """
        Splits the polygon into two new Polygons using a line defined by split_point and split_dir.
        Returns (poly1, poly2). If no split occurs (line misses), returns (self, None).
        """
        # Line: P = split_point + t * split_dir
        # Normal to line: (-dir.y, dir.x)
        normal = glm.vec2(-split_dir.y, split_dir.x)
        
        # Classify vertices
        dists = []
        for v in self.vertices:
            d = glm.dot(v - split_point, normal)
            dists.append(d)
            
        # Check if all on one side (with tolerance)
        all_pos = all(d >= -1e-5 for d in dists)
        all_neg = all(d <= 1e-5 for d in dists)
        
        if all_pos or all_neg:
            return self, None
            
        poly1_verts = [] # Positive side
        poly2_verts = [] # Negative side
        
        n_verts = len(self.vertices)
        for i in range(n_verts):
            curr_v = self.vertices[i]
            next_v = self.vertices[(i + 1) % n_verts]
            curr_d = dists[i]
            next_d = dists[(i + 1) % n_verts]
            
            # Add current vertex to appropriate list(s)
            # Use tolerance for "on line"
            if curr_d >= -1e-5:
                poly1_verts.append(curr_v)
            if curr_d <= 1e-5:
                poly2_verts.append(curr_v)
                
            # Check for strict crossing
            if curr_d * next_d < -1e-10: # Signs differ significantly
                # Calculate intersection point
                t = -curr_d / (next_d - curr_d)
                intersect_v = curr_v + t * (next_v - curr_v)
                
                poly1_verts.append(intersect_v)
                poly2_verts.append(intersect_v)
        
        # Filter out polygons with too few vertices
        # Remove duplicates? (e.g. if vertex was on line, it might be added twice if we are not careful? No, logic above adds curr_v once, then intersect only if crossing.)
        # If curr_d is 0 and next_d is 0, no crossing.
        # If curr_d is 0 and next_d is 1, no crossing.
        # If curr_d is -1 and next_d is 1, crossing.
        
        if len(poly1_verts) < 3 or len(poly2_verts) < 3:
             return self, None

        return Polygon(poly1_verts), Polygon(poly2_verts)

    @property
    def centroid(self):
        if not self.vertices:
            return glm.vec2(0, 0)
        return sum(self.vertices, glm.vec2(0, 0)) / len(self.vertices)

    def scale(self, factor):
        """
        Scales the polygon relative to its centroid.
        Returns a new Polygon.
        """
        c = self.centroid
        new_verts = []
        for v in self.vertices:
            # v_new = c + (v - c) * factor
            new_verts.append(c + (v - c) * factor)
        return Polygon(new_verts)

    def contains_point(self, point):
        """
        Checks if the point is inside the convex polygon.
        """
        # Check if point is on the same side of all edges
        n = len(self.vertices)
        for i in range(n):
            v1 = self.vertices[i]
            v2 = self.vertices[(i + 1) % n]
            edge = v2 - v1
            to_point = point - v1
            
            # Cross product (2D) = x1*y2 - x2*y1
            cross = edge.x * to_point.y - edge.y * to_point.x
            
            # Assuming CCW winding, point must be to the left (cross > 0)
            # Allow some tolerance
            if cross < -1e-5:
                return False
        return True

    def chamfer(self, radius):
        """
        Chamfers the corners of the polygon.
        radius: Size of the chamfer cut.
        Returns a new Polygon.
        """
        if radius <= 0:
            return self
            
        new_verts = []
        n = len(self.vertices)
        
        for i in range(n):
            curr_v = self.vertices[i]
            prev_v = self.vertices[(i - 1) % n]
            next_v = self.vertices[(i + 1) % n]
            
            # Vectors to neighbors
            to_prev = glm.normalize(prev_v - curr_v)
            to_next = glm.normalize(next_v - curr_v)
            
            # Check edge lengths
            dist_prev = glm.distance(curr_v, prev_v)
            dist_next = glm.distance(curr_v, next_v)
            
            # Limit radius to half the shortest edge to avoid overlap
            limit = min(dist_prev, dist_next) * 0.45
            r = min(radius, limit)
            
            p1 = curr_v + to_prev * r
            p2 = curr_v + to_next * r
            
            new_verts.append(p1)
            new_verts.append(p2)
            
        return Polygon(new_verts)

    def fillet(self, radius, segments=4):
        """
        Rounds the corners of the polygon.
        radius: Size of the corner cut.
        segments: Number of segments for the curve.
        Returns a new Polygon.
        """
        if radius <= 0 or segments < 1:
            return self
            
        new_verts = []
        n = len(self.vertices)
        
        for i in range(n):
            curr_v = self.vertices[i]
            prev_v = self.vertices[(i - 1) % n]
            next_v = self.vertices[(i + 1) % n]
            
            # Vectors to neighbors
            to_prev = glm.normalize(prev_v - curr_v)
            to_next = glm.normalize(next_v - curr_v)
            
            # Check edge lengths
            dist_prev = glm.distance(curr_v, prev_v)
            dist_next = glm.distance(curr_v, next_v)
            
            # Limit radius to half the shortest edge to avoid overlap
            limit = min(dist_prev, dist_next) * 0.45
            r = min(radius, limit)
            
            p1 = curr_v + to_prev * r
            p2 = curr_v + to_next * r
            
            # Generate curve points (Quadratic Bezier)
            # Control points: p1, curr_v, p2
            for s in range(segments):
                t = s / float(segments) # 0 to almost 1
                # Quadratic Bezier: B(t) = (1-t)^2 * P0 + 2(1-t)t * P1 + t^2 * P2
                inv_t = 1.0 - t
                pt = (inv_t * inv_t) * p1 + 2 * inv_t * t * curr_v + (t * t) * p2
                new_verts.append(pt)
            
            # Add the last point p2 (t=1)
            new_verts.append(p2)
            
        return Polygon(new_verts)

    def intersect_line(self, line_point, line_dir):
        """
        Finds the intersection points of an infinite line with the polygon edges.
        Returns a list of glm.vec2 points.
        """
        intersections = []
        n = len(self.vertices)
        
        for i in range(n):
            p1 = self.vertices[i]
            p2 = self.vertices[(i + 1) % n]
            
            # Edge segment
            edge_vec = p2 - p1
            
            # Check intersection between Segment (p1, p2) and Line (line_point, line_dir)
            # p1 + t * edge_vec = line_point + u * line_dir
            # Cross product method to solve 2D linear system
            
            # v x w = v.x * w.y - v.y * w.x
            def cross(v, w):
                return v.x * w.y - v.y * w.x
                
            denom = cross(edge_vec, line_dir)
            
            if abs(denom) > 1e-6:
                t = cross(line_point - p1, line_dir) / denom
                
                # Check if t is within segment [0, 1]
                if 0 <= t <= 1:
                    pt = p1 + t * edge_vec
                    intersections.append(pt)
                    
        return intersections

    def inset(self, amount):
        """
        Shrinks the polygon by moving edges inward by 'amount'.
        Assumes convex polygon (CCW winding).
        Returns a new Polygon.
        """
        if amount <= 0: return self
        
        new_verts = []
        n = len(self.vertices)
        
        # Line equations: P + t * D
        # We need to find intersection of shifted lines.
        
        for i in range(n):
            # Current vertex and neighbors
            curr_v = self.vertices[i]
            prev_v = self.vertices[(i - 1) % n]
            next_v = self.vertices[(i + 1) % n]
            
            # Edge vectors
            v_in = glm.normalize(curr_v - prev_v)
            v_out = glm.normalize(next_v - curr_v)
            
            # Normals (CCW)
            # Normal is (-dy, dx)
            n1 = glm.vec2(-v_in.y, v_in.x)
            n2 = glm.vec2(-v_out.y, v_out.x)
            
            # Shifted lines pass through:
            # L1: (prev_v + n1 * amount) + t * v_in
            # L2: (curr_v + n2 * amount) + u * v_out
            
            p1_s = prev_v + n1 * amount
            p2_s = curr_v + n2 * amount
            
            # Find intersection of L1 and L2
            # p1_s + t * v_in = p2_s + u * v_out
            # t * v_in - u * v_out = p2_s - p1_s
            
            # Solve 2D system
            # | v_in.x  -v_out.x | | t | = | dx |
            # | v_in.y  -v_out.y | | u |   | dy |
            
            det = v_in.x * (-v_out.y) - v_in.y * (-v_out.x)
            
            if abs(det) < 1e-6:
                # Parallel edges? Just use the shifted point
                new_verts.append(curr_v + n1 * amount)
            else:
                delta = p2_s - p1_s
                t = (delta.x * (-v_out.y) - delta.y * (-v_out.x)) / det
                
                pt = p1_s + t * v_in
                new_verts.append(pt)
                
        return Polygon(new_verts)
