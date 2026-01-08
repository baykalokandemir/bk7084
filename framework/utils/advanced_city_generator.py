import random
import math
import numpy as np
from pyglm import glm
from .polygon import Polygon
from framework.shapes.shape import Shape
from .road_network import RoadNetwork

class AdvancedCityGenerator:
    def __init__(self, width=400.0, depth=400.0, min_block_area=4000.0, min_lot_area=1000.0, ortho_chance=0.9, town_square_radius=40.0):
        self.width = width
        self.depth = depth
        self.min_block_area = min_block_area
        self.min_lot_area = min_lot_area
        self.ortho_chance = ortho_chance
        self.town_square_radius = town_square_radius
        
        # Root Polygon (Rectangle centered at origin)
        self.root = Polygon([
            glm.vec2(-width/2, -depth/2),
            glm.vec2(width/2, -depth/2),
            glm.vec2(width/2, depth/2),
            glm.vec2(-width/2, depth/2)
        ])
        
        self.blocks = [] 
        self.lots = []   
        self.buildings = [] 
        self.parks = [] 
        self.roads = [] # List of Shapes (Road segments)
        self.sidewalks = [] # List of Shapes
        self.road_network = None
        self.street_light_poses = [] # List of glm.mat4

    def generate(self):
        self.blocks = []
        self.lots = []
        self.buildings = []
        self.parks = []
        self.roads = []
        self.sidewalks = []
        self.street_light_poses = []
        self.road_network = RoadNetwork()
        
        # 1. Carve out Town Square (DISABLED for Hybrid Mode)
        # city_sectors, town_square_poly = self._create_town_square(self.root)
        
        # Process Town Square
        # if town_square_poly:
            # ...
        
        # 2. Generate Blocks (City Layout) directly from Root
        raw_blocks = []
        
        # Start at depth 0 for major arterial roads (20m width)
        self._split_city_recursive(self.root, raw_blocks, 0)
        
        # 3. Generate Road Meshes from Network
        road_meshes, road_edges = self.road_network.generate_meshes()
        self.roads.extend(road_meshes)
        
        # Generator Street Lights from Edges
        light_spacing = 25.0
        sidewalk_offset = 0.5 # Distance from curb
        
        for edge in road_edges:
            start = edge['start']
            end = edge['end']
            normal = edge['normal']
            
            vec = end - start
            length = glm.length(vec)
            direction = glm.normalize(vec)
            
            # Place lights
            # Start a bit in
            curr_dist = light_spacing * 0.5
            
            while curr_dist < length:
                pos = start + direction * curr_dist
                # Offset onto sidewalk
                pos += normal * sidewalk_offset
                
                # Create Transform
                # Position
                mat = glm.translate(pos)
                
                # Rotation
                # Normal points to sidewalk (back of light).
                # Light should face ROAD (negative normal).
                # Default light faces +Z? Check StreetLight class.
                # In StreetLight, arm extends +X.
                # So +X should point to ROAD (-normal).
                # Normal is (nx, 0, nz).
                # We want light's +X to be -normal.
                # We want light's +Y to be +Y (up).
                # We want light's +Z to be cross(X, Y) = cross(-normal, up).
                
                target_x = -normal
                target_y = glm.vec3(0, 1, 0)
                target_z = glm.normalize(glm.cross(target_x, target_y))
                
                # Rotation Matrix from basis vectors
                # mat4 construct from col vectors
                rot = glm.mat4(
                    glm.vec4(target_x, 0.0),
                    glm.vec4(target_y, 0.0),
                    glm.vec4(target_z, 0.0),
                    glm.vec4(0, 0, 0, 1.0)
                )
                
                self.street_light_poses.append(mat * rot)
                
                curr_dist += light_spacing
        
        # 4. Process Blocks & Sidewalks
        for raw_block in raw_blocks:
            # Shrink to create road gaps
            # Sidewalk Outer (Curb)
            curb_poly = raw_block.inset(3.0)
            
            # Sidewalk Inner (Building Lot)
            block = curb_poly.inset(2.0)
            
            self.blocks.append(block)
            
            # Generate Sidewalk Mesh
            self._generate_sidewalk(curb_poly, block)
            
            # 5. Subdivide Block into Lots
            block_lots = []
            self._split_block_recursive(block, block_lots, 0)
            self.lots.extend(block_lots)
            
        # 6. Generate Buildings
        from .building import Building 
        
        for lot in self.lots:
            # Random Corner Style
            r = random.random()
            if r < 0.2:
                lot = lot.chamfer(random.uniform(2.0, 5.0))
            elif r < 0.4:
                lot = lot.fillet(random.uniform(2.0, 5.0), segments=4)
                
            height = random.uniform(10.0, 40.0) 
            
            # Random Style
            style = {
                "floor_height": random.uniform(2.5, 4.0),
                "window_ratio": random.uniform(0.4, 0.8),
                "inset_depth": random.uniform(0.2, 0.8),
                "color": glm.vec4(random.uniform(0.7, 0.9), random.uniform(0.7, 0.9), random.uniform(0.7, 0.9), 1.0),
                "window_color": glm.vec4(0.1, 0.2, 0.3 + random.random()*0.3, 1.0),
                "stepped": (height > 25.0) and (random.random() < 0.4), 
                "window_style": "vertical_stripes" if random.random() < 0.5 else "single"
            }
            
            building = Building(lot, height, style)
            shape = building.generate()
            self.buildings.append(shape)


    def _generate_sidewalk(self, outer, inner):
        # Create a mesh for the ring between outer and inner
        # Elevated at y=0.2
        shape = Shape()
        verts = []
        norms = []
        cols = []
        inds = []
        
        color = glm.vec4(0.7, 0.7, 0.7, 1.0) # Light Gray
        y = 0.2
        
        # We assume outer and inner have same vertex count and winding
        n = len(outer.vertices)
        if len(inner.vertices) != n: return # Should match if scaled
        
        start_idx = 0
        
        for i in range(n):
            o1 = outer.vertices[i]
            o2 = outer.vertices[(i+1)%n]
            i1 = inner.vertices[i]
            i2 = inner.vertices[(i+1)%n]
            
            # --- TOP FACE ---
            # Quad: o1, o2, i2, i1
            verts.extend([
                glm.vec4(o1.x, y, o1.y, 1.0),
                glm.vec4(o2.x, y, o2.y, 1.0),
                glm.vec4(i2.x, y, i2.y, 1.0),
                glm.vec4(i1.x, y, i1.y, 1.0)
            ])
            norms.extend([glm.vec3(0, 1, 0)] * 4)
            cols.extend([color] * 4)
            
            # Calculate base index for TOP
            # Each iteration adds 8 vertices total (4 top + 4 curb).
            # So the start of this iteration's TOP is i * 8.
            base = start_idx + (i * 8)
            inds.extend([base, base+1, base+2, base, base+2, base+3])
            
            # --- CURB FACE ---
            # o1 -> o2 down to y=0
            verts.extend([
                glm.vec4(o1.x, y, o1.y, 1.0),
                glm.vec4(o2.x, y, o2.y, 1.0),
                glm.vec4(o2.x, 0, o2.y, 1.0),
                glm.vec4(o1.x, 0, o1.y, 1.0)
            ])
            
            # Normal approx
            edge = o2 - o1
            norm = glm.normalize(glm.vec3(-edge.y, 0, edge.x))
            norms.extend([norm] * 4)
            cols.extend([color] * 4)
            
            # Calculate base index for CURB
            # The curb vertices are added immediately after the 4 top vertices.
            base_curb = base + 4
            inds.extend([base_curb, base_curb+1, base_curb+2, base_curb, base_curb+2, base_curb+3])

        shape.vertices = np.array([v.to_list() for v in verts], dtype=np.float32)
        shape.normals = np.array([n.to_list() for n in norms], dtype=np.float32)
        shape.uvs = np.zeros((len(verts), 2), dtype=np.float32)
        shape.colors = np.array([c.to_list() for c in cols], dtype=np.float32)
        shape.indices = np.array(inds, dtype=np.uint32)
        
        self.sidewalks.append(shape)


    def _create_town_square(self, root_poly):
        """
        Carves a hexagon/octagon from the center of root_poly.
        Returns (list_of_outside_polys, center_poly)
        """
        center_poly = root_poly
        outside_polys = []
        
        # Define Hexagon Vertices
        radius = self.town_square_radius
        sides = 6
        hex_verts = []
        for i in range(sides):
            angle = i * (math.pi * 2 / sides)
            hex_verts.append(glm.vec2(math.cos(angle) * radius, math.sin(angle) * radius))
            
        # Cut center_poly by each edge of the hexagon
        for i in range(sides):
            v1 = hex_verts[i]
            v2 = hex_verts[(i + 1) % sides]
            
            # Line defined by v1 -> v2
            split_point = v1
            split_dir = glm.normalize(v2 - v1)
            
            intersections = center_poly.intersect_line(split_point, split_dir)
            if len(intersections) >= 2:
                p1 = intersections[0]
                p2 = intersections[1]
                
                # Sort points along the line direction
                points = [p1, p2, v1, v2]
                # Project onto split_dir
                points.sort(key=lambda p: glm.dot(p - v1, split_dir))
                
                # Expected order: SpokeStart -> v1 -> v2 -> SpokeEnd
                # But v1, v2 might be swapped relative to p1, p2 depending on poly shape?
                # v1 is at 0 projection (relative to v1). v2 is at dist.
                # p1, p2 should be at negative and >dist.
                
                s1, s2, s3, s4 = points[0], points[1], points[2], points[3]
                
                # Add segments to RoadNetwork
                if self.road_network:
                    # Spoke 1: s1 -> s2
                    self.road_network.add_segment(s1, s2, 20.0, 6)
                    
                    # Ring Segment: s2 -> s3 (REMOVED - Will be added later as a closed loop)
                    # self.road_network.add_segment(s2, s3, 14.0, 4)
                    
                    # Spoke 2: s3 -> s4
                    self.road_network.add_segment(s3, s4, 20.0, 6)
            
            poly1, poly2 = center_poly.split(split_point, split_dir)
            
            if poly1 and poly2:
                # One contains (0,0), one is outside
                if poly1.contains_point(glm.vec2(0, 0)):
                    center_poly = poly1
                    outside_polys.append(poly2)
                else:
                    center_poly = poly2
                    outside_polys.append(poly1)
            else:
                pass
                
        return outside_polys, center_poly

    def _split_city_recursive(self, poly, result_list, depth):
        # Recursively split until min_block_area is reached
        area = self._get_area(poly)
        
        if area < self.min_block_area or depth > 6: 
            result_list.append(poly)
            return

        # Attempt Split
        min_x, min_y, max_x, max_y = self._get_bounds(poly)
        cx, cy = (min_x + max_x) / 2, (min_y + max_y) / 2
        dx, dy = (max_x - min_x) / 2, (max_y - min_y) / 2
        
        split_point = glm.vec2(
            random.uniform(cx - dx*0.4, cx + dx*0.4),
            random.uniform(cy - dy*0.4, cy + dy*0.4)
        )
        
        # Determine Angle based on Aspect Ratio
        width = max_x - min_x
        height = max_y - min_y
        aspect = width / height if height > 0 else 1.0
        
        if random.random() < self.ortho_chance:
            if aspect > 1.5: angle = math.pi / 2
            elif aspect < 0.66: angle = 0
            else: angle = 0 if random.random() < 0.5 else math.pi / 2
        else:
            angle = random.uniform(0, math.pi * 2)
            
        split_dir = glm.vec2(math.cos(angle), math.sin(angle))
        
        poly1, poly2 = poly.split(split_point, split_dir)
        
        if poly1 and poly2:
            # Record Road Segment
            if self.road_network:
                # Find intersection of split line with poly
                intersections = poly.intersect_line(split_point, split_dir)
                if len(intersections) >= 2:
                    p1 = intersections[0]
                    p2 = intersections[1]
                    
                    # Determine width/lanes based on depth
                    if depth == 0:
                        w, l = 20.0, 6
                    elif depth == 1:
                        w, l = 14.0, 4
                    else:
                        w, l = 8.0, 2
                        
                    self.road_network.add_segment(p1, p2, w, l)

            self._split_city_recursive(poly1, result_list, depth + 1)
            self._split_city_recursive(poly2, result_list, depth + 1)
        else:
            result_list.append(poly)

    def _split_block_recursive(self, poly, result_list, depth):
        # Recursively split until min_lot_area is reached
        area = self._get_area(poly)
        
        if area < self.min_lot_area or depth > 3: # Reduced depth to prevent landlocked lots
            result_list.append(poly)
            return

        self._attempt_split(poly, result_list, depth, self._split_block_recursive, gap=False)

    def _attempt_split(self, poly, result_list, depth, recurse_func, gap=False):
        # Bounding box
        min_x = min(v.x for v in poly.vertices)
        max_x = max(v.x for v in poly.vertices)
        min_y = min(v.y for v in poly.vertices)
        max_y = max(v.y for v in poly.vertices)
        
        cx = (min_x + max_x) / 2
        cy = (min_y + max_y) / 2
        dx = (max_x - min_x) * 0.3
        dy = (max_y - min_y) * 0.3
        
        split_point = glm.vec2(
            random.uniform(cx - dx, cx + dx),
            random.uniform(cy - dy, cy + dy)
        )
        
        # Determine Angle based on Aspect Ratio
        width = max_x - min_x
        height = max_y - min_y
        aspect = width / height if height > 0 else 1.0
        
        if random.random() < self.ortho_chance:
            # Orthogonal split (0 or 90 degrees)
            # Bias towards cutting the long axis to make pieces square
            if aspect > 1.5:
                # Wide: Cut Vertically (Line dir = (0, 1))
                angle = math.pi / 2
            elif aspect < 0.66:
                # Tall: Cut Horizontally (Line dir = (1, 0))
                angle = 0
            else:
                # Square-ish: Randomly pick
                if random.random() < 0.5:
                    angle = 0
                else:
                    angle = math.pi / 2
        else:
            # Random angle
            angle = random.uniform(0, math.pi * 2)
            
        split_dir = glm.vec2(math.cos(angle), math.sin(angle))
        
        poly1, poly2 = poly.split(split_point, split_dir)
        
        if poly1 and poly2:
            recurse_func(poly1, result_list, depth + 1)
            recurse_func(poly2, result_list, depth + 1)
        else:
            result_list.append(poly)

    def _get_area(self, poly):
        area = 0.0
        n = len(poly.vertices)
        for i in range(n):
            v1 = poly.vertices[i]
            v2 = poly.vertices[(i + 1) % n]
            area += (v1.x * v2.y - v2.x * v1.y)
        return abs(area) * 0.5

    def _get_bounds(self, poly):
        min_x = min(v.x for v in poly.vertices)
        max_x = max(v.x for v in poly.vertices)
        min_y = min(v.y for v in poly.vertices)
        max_y = max(v.y for v in poly.vertices)
        return min_x, min_y, max_x, max_y
