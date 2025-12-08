import random
import math
import numpy as np
from pyglm import glm
from .polygon import Polygon

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
        self.parks = [] # List of Shapes (Green spaces)

    def generate(self):
        self.blocks = []
        self.lots = []
        self.buildings = []
        self.parks = []
        
        # 1. Carve out Town Square
        city_sectors, town_square_poly = self._create_town_square(self.root)
        
        # Process Town Square
        if town_square_poly:
            # Shrink for Roundabout
            park_poly = town_square_poly.scale(0.8) # Bigger gap for roundabout
            
            # Extrude slightly (grass)
            park_shape = park_poly.extrude(0.5)
            # Color will be handled in renderer or here if we support vertex colors
            # Let's set vertex colors to Green
            park_shape.colors = np.array([[0.2, 0.8, 0.2, 1.0]] * len(park_shape.vertices), dtype=np.float32)
            self.parks.append(park_shape)
        
        # 2. Generate Blocks (City Layout) from Sectors
        raw_blocks = []
        for sector in city_sectors:
            self._split_city_recursive(sector, raw_blocks, 0)
        
        # 3. Process Blocks
        for raw_block in raw_blocks:
            # Shrink to create road gaps
            block = raw_block.scale(0.85) 
            self.blocks.append(block)
            
            # 4. Subdivide Block into Lots
            block_lots = []
            self._split_block_recursive(block, block_lots, 0)
            self.lots.extend(block_lots)
            
        # 5. Generate Buildings
        from .building import Building # Import here to avoid circular dep if any
        
        for lot in self.lots:
            # Random Corner Style
            r = random.random()
            if r < 0.2:
                # Chamfer
                lot = lot.chamfer(random.uniform(2.0, 5.0))
            elif r < 0.4:
                # Fillet (Rounded)
                lot = lot.fillet(random.uniform(2.0, 5.0), segments=4)
                
            height = random.uniform(10.0, 40.0) # Taller buildings
            
            # Random Style
            style = {
                "floor_height": random.uniform(2.5, 4.0),
                "window_ratio": random.uniform(0.4, 0.8),
                "inset_depth": random.uniform(0.2, 0.8),
                "color": glm.vec4(random.uniform(0.7, 0.9), random.uniform(0.7, 0.9), random.uniform(0.7, 0.9), 1.0),
                "window_color": glm.vec4(0.1, 0.2, 0.3 + random.random()*0.3, 1.0),
                "stepped": (height > 25.0) and (random.random() < 0.4), # 40% chance for tall buildings
                "window_style": "vertical_stripes" if random.random() < 0.5 else "single"
            }
            
            building = Building(lot, height, style)
            shape = building.generate()
            self.buildings.append(shape)

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
                # Split failed? Should not happen if root covers center.
                pass
                
        return outside_polys, center_poly

    def _split_city_recursive(self, poly, result_list, depth):
        # Recursively split until min_block_area is reached
        area = self._get_area(poly)
        
        if area < self.min_block_area or depth > 6: # Reduced depth
            result_list.append(poly)
            return

        self._attempt_split(poly, result_list, depth, self._split_city_recursive, gap=False)

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
