from pyglm import glm
import random
import math

class CityGenerator:
    def __init__(self, width=200.0, depth=200.0, min_block_size=20.0, road_width=2.0, flat=False):
        self.width = width
        self.depth = depth
        self.min_block_size = min_block_size
        self.road_width = road_width
        self.flat = flat
        
        self.road_cubes = [] # Transforms for road cubes
        self.building_cubes = [] # Transforms for building cubes
        self.building_colors = [] # Colors for building cubes
        
        # Root node: (min_x, min_z, max_x, max_z)
        self.root = (-width/2, -depth/2, width/2, depth/2)
        self.leaves = [] # List of blocks (rects)

    def generate(self):
        self.road_cubes = []
        self.building_cubes = []
        self.building_colors = []
        self.leaves = []
        
        # Recursive split starting at level 0
        self._split(self.root, level=0)
        
        # Generate Buildings on leaves
        self._generate_buildings()

    def _split(self, rect, level=0):
        min_x, min_z, max_x, max_z = rect
        w = max_x - min_x
        d = max_z - min_z
        
        # Determine road width based on level
        # Level 0: 6 lanes (~15.0 width)
        # Level 1-2: 4 lanes (~10.0 width)
        # Level 3+: 2 lanes (~6.0 width)
        
        current_road_width = 6.0
        if level == 0:
            current_road_width = 15.0
        elif level <= 2:
            current_road_width = 10.0
        else:
            current_road_width = 6.0
            
        # Check if we should split
        if w < self.min_block_size * 2 or d < self.min_block_size * 2:
            self.leaves.append(rect)
            return
            
        # Decide split axis
        split_axis = 0 if w > d else 1 # 0=X (vertical line), 1=Z (horizontal line)
        if 0.5 < w/d < 2.0:
            split_axis = 0 if random.random() < 0.5 else 1
            
        margin = self.min_block_size
        
        if split_axis == 0: # Split X
            if w < margin * 2:
                self.leaves.append(rect)
                return
            split_val = random.uniform(min_x + margin, max_x - margin)
            
            # Create Road Cube (Vertical strip)
            road_pos = glm.vec3(split_val, 0, (min_z + max_z) / 2)
            road_scale = glm.vec3(current_road_width, 0.1, d)
            
            T = glm.translate(road_pos) * glm.scale(road_scale)
            self.road_cubes.append(T)
            
            # Recurse
            rect1 = (min_x, min_z, split_val - current_road_width/2, max_z)
            rect2 = (split_val + current_road_width/2, min_z, max_x, max_z)
            self._split(rect1, level + 1)
            self._split(rect2, level + 1)
            
        else: # Split Z
            if d < margin * 2:
                self.leaves.append(rect)
                return
            split_val = random.uniform(min_z + margin, max_z - margin)
            
            # Create Road Cube (Horizontal strip)
            road_pos = glm.vec3((min_x + max_x) / 2, 0, split_val)
            road_scale = glm.vec3(w, 0.1, current_road_width)
            
            T = glm.translate(road_pos) * glm.scale(road_scale)
            self.road_cubes.append(T)
            
            # Recurse
            rect1 = (min_x, min_z, max_x, split_val - current_road_width/2)
            rect2 = (min_x, split_val + current_road_width/2, max_x, max_z)
            self._split(rect1, level + 1)
            self._split(rect2, level + 1)

    def _generate_buildings(self):
        for rect in self.leaves:
            min_x, min_z, max_x, max_z = rect
            
            # Shrink for sidewalk
            margin = 1.0
            if max_x - min_x < margin*2 or max_z - min_z < margin*2:
                continue
                
            sx = min_x + margin
            sz = min_z + margin
            ex = max_x - margin
            ez = max_z - margin
            
            # Subdivide block into lots
            lots = []
            self._subdivide_block((sx, sz, ex, ez), lots)
            
            for lot in lots:
                lx, lz, rx, rz = lot
                width = rx - lx
                depth = rz - lz
                
                # Height
                if self.flat:
                    h = 0.1
                else:
                    h = random.uniform(5.0, 35.0) # Taller buildings
                
                color = glm.vec4(random.uniform(0.3, 0.8), random.uniform(0.3, 0.8), random.uniform(0.3, 0.8), 1.0)
                
                # Create Building Cube
                pos = glm.vec3((lx + rx) / 2, h/2, (lz + rz) / 2)
                scale = glm.vec3(width, h, depth)
                
                T = glm.translate(pos) * glm.scale(scale)
                
                self.building_cubes.append(T)
                self.building_colors.append(color)

    def _subdivide_block(self, rect, lots):
        min_x, min_z, max_x, max_z = rect
        w = max_x - min_x
        d = max_z - min_z
        
        min_lot_size = 10.0 # Minimum building size
        
        # Stop if too small
        if w < min_lot_size * 2 or d < min_lot_size * 2:
            lots.append(rect)
            return
            
        # Decide split
        split_axis = 0 if w > d else 1
        if 0.5 < w/d < 2.0:
            split_axis = 0 if random.random() < 0.5 else 1
            
        if split_axis == 0: # Split X
            if w < min_lot_size * 2:
                lots.append(rect)
                return
            split_val = random.uniform(min_x + min_lot_size, max_x - min_lot_size)
            
            self._subdivide_block((min_x, min_z, split_val, max_z), lots)
            self._subdivide_block((split_val, min_z, max_x, max_z), lots)
        else: # Split Z
            if d < min_lot_size * 2:
                lots.append(rect)
                return
            split_val = random.uniform(min_z + min_lot_size, max_z - min_lot_size)
            
            self._subdivide_block((min_x, min_z, max_x, split_val), lots)
            self._subdivide_block((min_x, split_val, max_x, max_z), lots)
