import random
import math
import numpy as np
from pyglm import glm
from .polygon import Polygon
from framework.shapes.shape import Shape
from .road_network import RoadNetwork

class AdvancedCityGenerator:
    """
    Procedural city generator using Binary Space Partitioning (BSP).
    
    Generates a city layout with roads, sidewalks, building lots, and buildings
    through recursive spatial subdivision. The algorithm:
    1. Recursively splits the root polygon into blocks using BSP
    2. Records split lines as road segments in a road network
    3. Insets blocks to create sidewalks
    4. Further subdivides blocks into individual building lots
    5. Generates procedural buildings on each lot with randomized heights and styles
    
    The generator creates a road network mesh, sidewalk meshes, and building shapes
    that can be batched for efficient rendering.
    """
    
    def __init__(self, width=400.0, depth=400.0, min_block_area=4000.0, min_lot_area=1000.0, ortho_chance=0.9):
        # City dimensions
        self.width = width
        self.depth = depth
        self.min_block_area = min_block_area
        self.min_lot_area = min_lot_area
        self.ortho_chance = ortho_chance
        
        # Road & Sidewalk Constants
        self.ROAD_WIDTH = 8.0
        self.ROAD_LANES = 2
        self.ROAD_GAP = 3.0  # Space between block and curb
        self.SIDEWALK_WIDTH = 2.0  # Curb to building
        self.SIDEWALK_HEIGHT = 0.2
        
        # Building Generation
        self.MIN_HEIGHT = 10.0
        self.MAX_HEIGHT = 40.0
        self.TALL_BUILDING_THRESHOLD = 25.0
        self.STEPPED_CHANCE = 0.4
        self.CHAMFER_CHANCE = 0.2
        self.FILLET_CHANCE = 0.2  # Total corner modification = 0.4
        
        # Recursion Limits
        self.MAX_CITY_DEPTH = 6
        self.MAX_BLOCK_DEPTH = 3
        
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

    def generate(self, texture_list=None):
        """
        Generate complete city layout.
        
        Args:
            texture_list: Optional list of texture filenames for building facades.
                         If None, uses default hardcoded textures.
        
        Produces:
            - self.roads: List of road mesh shapes
            - self.sidewalks: List of sidewalk mesh shapes  
            - self.buildings: List of building mesh shapes
            - self.blocks: List of block polygons
            - self.lots: List of lot polygons
        """
        self.blocks = []
        self.lots = []
        self.buildings = []
        self.parks = []
        self.roads = []
        self.sidewalks = []
        self.road_network = RoadNetwork()
        
        # 1. Generate Blocks (City Layout) directly from Root
        raw_blocks = []
        
        # Start at depth 0 for major arterial roads (20m width)
        self._split_city_recursive(self.root, raw_blocks, 0)
        
        # 2. Generate Road Meshes from Network
        road_meshes, road_edges = self.road_network.generate_meshes()
        self.roads.extend(road_meshes)
        
        # 3. Process Blocks & Sidewalks
        for raw_block in raw_blocks:
            # Shrink to create road gaps
            # Sidewalk Outer (Curb)
            curb_poly = raw_block.inset(self.ROAD_GAP)
            
            # Sidewalk Inner (Building Lot)
            # Create sidewalk and building lot by insetting
            block = curb_poly.inset(self.SIDEWALK_WIDTH)
            
            self.blocks.append(block)
            
            # Generate Sidewalk Mesh
            self._generate_sidewalk(curb_poly, block)
            
            # 4. Subdivide Block into Lots
            block_lots = []
            self._split_block_recursive(block, block_lots, 0)
            self.lots.extend(block_lots)
            
        # 5. Generate Buildings
        from .building import Building 
        
        if texture_list and len(texture_list) > 0:
            available_textures = texture_list
        else:
            available_textures = ["brick1.png", "brick2.jpg", "brick3.jpg", "brick4.jpg", "concrete.jpg", "tile.jpg"]
        
        for lot in self.lots:
            # Random Corner Style
            # Randomly modify lot corners for visual variety
            # 20% chamfered (cut corners), 20% filleted (rounded corners), 60% unchanged
            r = random.random()
            if r < self.CHAMFER_CHANCE:
                lot = lot.chamfer(random.uniform(2.0, 5.0))
            elif r < (self.CHAMFER_CHANCE + self.FILLET_CHANCE):
                lot = lot.fillet(random.uniform(2.0, 5.0), segments=4)
                
            height = random.uniform(self.MIN_HEIGHT, self.MAX_HEIGHT)
            
            # Random Style
            style = {
                "floor_height": random.uniform(2.5, 4.0),
                "window_ratio": random.uniform(0.4, 0.8),
                "inset_depth": random.uniform(0.2, 0.8),
                "color": glm.vec4(random.uniform(0.7, 0.9), random.uniform(0.7, 0.9), random.uniform(0.7, 0.9), 1.0),
                "window_color": glm.vec4(0.1, 0.2, 0.3 + random.random()*0.3, 1.0),
                "stepped": (height > self.TALL_BUILDING_THRESHOLD) and (random.random() < self.STEPPED_CHANCE),
                "window_style": "vertical_stripes" if random.random() < 0.5 else "single",
                "texture": random.choice(available_textures)
            }
            
            building = Building(lot, height, style)
            shape = building.generate()
            self.buildings.append(shape)

    def _generate_sidewalk(self, outer, inner):
        """
        Generate sidewalk mesh as a ring between two polygons.
        
        Args:
            outer: Curb polygon (outer edge)
            inner: Building lot polygon (inner edge)
        
        Creates a raised platform (0.2m height) with top face and outer curb face.
        """
        # Create a mesh for the ring between outer and inner
        # Elevated at y=0.2
        shape = Shape()
        verts = []
        norms = []
        cols = []
        inds = []
        
        color = glm.vec4(0.7, 0.7, 0.7, 1.0) # Light Gray
        y = self.SIDEWALK_HEIGHT
        
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

    def _split_city_recursive(self, poly, result_list, depth):
        """
        Recursively split polygon into city blocks using BSP.
        
        Creates road network as a side effect by recording split lines.
        Stops when area < min_block_area or max depth reached.
        Uses orthogonal splits (90° angles) most of the time for grid-like streets.
        """
        # Recursively split until min_block_area is reached
        area = self._get_area(poly)
        
        if area < self.min_block_area or depth > self.MAX_CITY_DEPTH: 
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
        # Determine split angle based on polygon aspect ratio
        # Prefer cutting across the long axis to create square-ish blocks
        width = max_x - min_x
        height = max_y - min_y
        aspect = width / height if height > 0 else 1.0
        
        if random.random() < self.ortho_chance:
            if aspect > 1.5: angle = math.pi / 2 # Wide polygon: cut vertically
            elif aspect < 0.66: angle = 0 # Tall polygon: cut horizontally
            else: angle = 0 if random.random() < 0.5 else math.pi / 2 # Square: random
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
                    
                    # UNIFORM ROAD NETWORK (Width 8.0, 2 Lanes)
                    # No more depth-based hierarchy
                    w, l = self.ROAD_WIDTH, self.ROAD_LANES
                        
                    self.road_network.add_segment(p1, p2, w, l)

            self._split_city_recursive(poly1, result_list, depth + 1)
            self._split_city_recursive(poly2, result_list, depth + 1)
        else:
            result_list.append(poly)

    def _split_block_recursive(self, poly, result_list, depth):
        """
        Recursively split block polygon into building lots.
        
        Similar to city splitting but operates on smaller scale (lots vs blocks).
        Stops when area < min_lot_area or max depth reached.
        """
        # Recursively split until min_lot_area is reached
        area = self._get_area(poly)
        
        if area < self.min_lot_area or depth > self.MAX_BLOCK_DEPTH: 
            result_list.append(poly)
            return

        self._attempt_split(poly, result_list, depth, self._split_block_recursive)

    def _attempt_split(self, poly, result_list, depth, recurse_func):
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
