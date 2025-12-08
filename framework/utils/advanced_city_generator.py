import random
import math
from pyglm import glm
from .polygon import Polygon

class AdvancedCityGenerator:
    def __init__(self, width=400.0, depth=400.0, min_block_area=4000.0, min_lot_area=1000.0, ortho_chance=0.9):
        self.width = width
        self.depth = depth
        self.min_block_area = min_block_area # Stop city splitting here
        self.min_lot_area = min_lot_area     # Stop block splitting here
        self.ortho_chance = ortho_chance
        
        # Root Polygon (Rectangle centered at origin)
        self.root = Polygon([
            glm.vec2(-width/2, -depth/2),
            glm.vec2(width/2, -depth/2),
            glm.vec2(width/2, depth/2),
            glm.vec2(-width/2, depth/2)
        ])
        
        self.blocks = [] # List of Polygons (shrunk leaves of city tree)
        self.lots = []   # List of Polygons (leaves of block trees)
        self.buildings = [] # List of Shapes

    def generate(self):
        self.blocks = []
        self.lots = []
        self.buildings = []
        
        # 1. Generate Blocks (City Layout)
        # These splits define the roads.
        raw_blocks = []
        self._split_city_recursive(self.root, raw_blocks, 0)
        
        # 2. Process Blocks
        for raw_block in raw_blocks:
            # Shrink to create road gaps
            # Scale relative to centroid
            block = raw_block.scale(0.85) 
            self.blocks.append(block)
            
            # 3. Subdivide Block into Lots (No gaps)
            block_lots = []
            self._split_block_recursive(block, block_lots, 0)
            self.lots.extend(block_lots)
            
        # 4. Generate Buildings
        for lot in self.lots:
            # Extrude
            height = random.uniform(5.0, 20.0)
            shape = lot.extrude(height)
            self.buildings.append(shape)

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
