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

    def generate(self):
        self.blocks = []
        self.lots = []
        self.buildings = []
        self.parks = []
        self.roads = []
        self.sidewalks = []
        self.road_network = RoadNetwork()
        
        # 1. Carve out Town Square
        city_sectors, town_square_poly = self._create_town_square(self.root)
        
        # Process Town Square
        if town_square_poly:
            # Generate Roundabout Ring (Closed Loop)
            # Iterate vertices of the final town_square_poly
            # These vertices correspond to the endpoints of the spoke roads (s2, s3 from _create_town_square)
            # So connecting them creates the ring, and they should snap to the spoke nodes.
            
            verts = town_square_poly.vertices
            n = len(verts)
            for i in range(n):
                v1 = verts[i]
                v2 = verts[(i+1)%n]
                # Width 14.0 (3 lanes + spacing)
                self.road_network.add_segment(v1, v2, 14.0, 4)

            # Sidewalk (Inner Ring, adjacent to park)
            # The RoadNetwork now generates the road at the boundary of town_square_poly.
            # town_square_poly IS the inner edge of the road ring?
            # No, town_square_poly is the hexagon defined by v1-v2.
            # In _create_town_square, we added v1-v2 as the road segment.
            # So the road runs ALONG the edge of town_square_poly.
            # Width 14.0. So it extends 7.0 inside and 7.0 outside.
            
            # We want a sidewalk INSIDE the road.
            # So we need to inset town_square_poly by 7.0 (half road) + sidewalk_width.
            
            half_road_w = 7.0
            sidewalk_w = 4.0
            
            sidewalk_outer = town_square_poly.inset(half_road_w)
            sidewalk_inner = sidewalk_outer.inset(sidewalk_w)
            
            self._generate_sidewalk(sidewalk_outer, sidewalk_inner)
            
            # Park (Center)
            park_poly = sidewalk_inner
            
            # Extrude slightly (grass)
            park_shape = park_poly.extrude(0.5)
            park_shape.colors = np.array([[0.2, 0.8, 0.2, 1.0]] * len(park_shape.vertices), dtype=np.float32)
            self.parks.append(park_shape)
        
        # 2. Generate Blocks (City Layout) from Sectors
        raw_blocks = []
        
        for sector in city_sectors:
            # Start at depth 1 so sectors are split into 4-lane roads, then 2-lane.
            self._split_city_recursive(sector, raw_blocks, 1)
        
        # 3. Generate Road Meshes from Network
        self.roads.extend(self.road_network.generate_meshes())
        
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
            
            # Quad: o1, o2, i2, i1
            verts.extend([
                glm.vec4(o1.x, y, o1.y, 1.0),
                glm.vec4(o2.x, y, o2.y, 1.0),
                glm.vec4(i2.x, y, i2.y, 1.0),
                glm.vec4(i1.x, y, i1.y, 1.0)
            ])
            norms.extend([glm.vec3(0, 1, 0)] * 4)
            cols.extend([color] * 4)
            
            base = start_idx + i * 4
            inds.extend([base, base+1, base+2, base, base+2, base+3])
            
            # Curb (Side face)
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
            
            base_curb = start_idx + n * 4 + i * 4
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
            
            # Capture Spoke Road (Main Artery)
            # Find intersection with CURRENT center_poly
            # Note: center_poly is shrinking, but for the first cut it's root_poly.
            # Actually, we want the intersection with the ROOT poly (or the current outer boundary).
            # But center_poly is the one being cut.
            # The split line is v1->v2.
            # Intersections with center_poly will be p1, p2.
            # Since v1, v2 are inside center_poly (before cut), p1 and p2 must be outside v1-v2 segment?
            # No, v1, v2 are ON the cut line.
            # p1, p2 are on the boundary of center_poly.
            # So p1, p2 bracket v1, v2.
            
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
