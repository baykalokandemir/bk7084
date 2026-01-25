import numpy as np
import random
from pyglm import glm
from framework.shapes.shape import Shape
from framework.utils.polygon import Polygon

class Building:
    def __init__(self, footprint, height, style_params=None):
        self.footprint = footprint
        self.height = height
        self.style_params = style_params or {}
        
        # Style defaults
        self.floor_height = self.style_params.get("floor_height", 3.0)
        self.window_ratio = self.style_params.get("window_ratio", 0.6) # 60% of floor is window
        self.inset_depth = self.style_params.get("inset_depth", 0.5)
        self.color = self.style_params.get("color", glm.vec4(0.8, 0.8, 0.8, 1.0))
        self.window_color = self.style_params.get("window_color", glm.vec4(0.1, 0.2, 0.4, 1.0))

    def generate(self):
        """
        Generates the 3D mesh for the building.
        Returns a Shape object.
        """
        shape = Shape()
        
        # Store assigned texture
        shape.texture_name = self.style_params.get("texture", "concrete.jpg")

        
        all_vertices = []
        all_normals = []
        all_uvs = []
        all_colors = []
        all_indices = []
        
        # Determine Style
        is_stepped = self.style_params.get("stepped", False)
        
        if is_stepped and self.height > 15.0:
            # Generate Stepped Building
            # 3 Tiers
            h1 = self.height * 0.5
            h2 = self.height * 0.3
            h3 = self.height * 0.2
            
            # Tier 1 (Base)
            self._generate_block(self.footprint, 0, h1, all_vertices, all_normals, all_colors, all_indices, all_uvs)
            
            # Tier 2
            poly2 = self.footprint.scale(0.7)
            self._generate_block(poly2, h1, h1+h2, all_vertices, all_normals, all_colors, all_indices, all_uvs)
            
            # Tier 3
            poly3 = poly2.scale(0.6) # relative to poly2? No, scale method is relative to self centroid.
            # poly2 is already scaled. poly3 should be smaller.
            # Let's just scale original
            poly3 = self.footprint.scale(0.4)
            self._generate_block(poly3, h1+h2, h1+h2+h3, all_vertices, all_normals, all_colors, all_indices, all_uvs)
            
            # Antenna on top
            if random.random() < 0.5:
                self._add_antenna(poly3.centroid, h1+h2+h3, all_vertices, all_normals, all_colors, all_indices, all_uvs)
                
        else:
            # Single Block
            self._generate_block(self.footprint, 0, self.height, all_vertices, all_normals, all_colors, all_indices, all_uvs)
            
            # Antenna
            if random.random() < 0.3:
                self._add_antenna(self.footprint.centroid, self.height, all_vertices, all_normals, all_colors, all_indices, all_uvs)

        # Populate Shape
        shape.vertices = np.array([v.to_list() for v in all_vertices], dtype=np.float32)
        shape.normals = np.array([n.to_list() for n in all_normals], dtype=np.float32)
        shape.uvs = np.array([u.to_list() for u in all_uvs], dtype=np.float32)
        shape.colors = np.array([c.to_list() for c in all_colors], dtype=np.float32)
        shape.indices = np.array(all_indices, dtype=np.uint32)
        
        return shape

        # 1. Top Face (Roof)
        top_start_idx = len(verts)
        for v in poly.vertices:
            verts.append(glm.vec4(v.x, y_end, v.y, 1.0))
            norms.append(glm.vec3(0, 1, 0))
            cols.append(self.color)
            # Planar UV for roof
            all_uvs = cols # Variable name mismatch in original code, fixed below by passing separate list?
            # Wait, helper function signature change means we need to pass list to _add_quad.
            # But here we are manually adding vertices.
            # Let's add to uvs list.
            # Use 'uvs' argument name from function def? No, func def uses 'verts, norms, cols, inds'.
            # I need to add 'uvs' to _generate_block signature first.
        
    def _generate_block(self, poly, y_start, y_end, verts, norms, cols, inds, uvs=None):
        if uvs is None: uvs = [] # Should be passed from generate
            
        # 1. Top Face (Roof)
        top_start_idx = len(verts)
        for v in poly.vertices:
            verts.append(glm.vec4(v.x, y_end, v.y, 1.0))
            norms.append(glm.vec3(0, 1, 0))
            cols.append(self.color)
            uvs.append(glm.vec2(v.x * 0.1, v.y * 0.1)) # Scale UVs for roof
            
        top_indices = poly.triangulate()
        for idx in top_indices:
            inds.append(top_start_idx + idx)
            
        # 2. Walls with Columns and Inset Windows
        n_verts = len(poly.vertices)
        height = y_end - y_start
        num_floors = max(1, int(height / self.floor_height))
        real_floor_h = height / num_floors
        
        for i in range(n_verts):
            curr_v = poly.vertices[i]
            next_v = poly.vertices[(i + 1) % n_verts]
            
            p1 = glm.vec3(curr_v.x, 0, curr_v.y)
            p2 = glm.vec3(next_v.x, 0, next_v.y)
            edge_vec = p2 - p1
            edge_len = glm.length(edge_vec)
            edge_dir = glm.normalize(edge_vec)
            normal = glm.normalize(glm.cross(glm.vec3(0, 1, 0), edge_vec))
            
            # Columns
            margin = min(1.0, edge_len * 0.15) # 15% margin or max 1.0 unit
            
            w_start = p1 + edge_dir * margin
            w_end = p2 - edge_dir * margin
            
            # For each floor
            for f in range(num_floors):
                y_bottom = y_start + f * real_floor_h
                y_top = y_start + (f + 1) * real_floor_h
                
                # Left Column
                self._add_quad(verts, norms, cols, inds, uvs,
                               p1 + glm.vec3(0, y_bottom, 0), w_start + glm.vec3(0, y_bottom, 0),
                               w_start + glm.vec3(0, y_top, 0), p1 + glm.vec3(0, y_top, 0),
                               normal, self.color,
                               uv1=glm.vec2(0, y_bottom), uv2=glm.vec2(margin, y_bottom),
                               uv3=glm.vec2(margin, y_top), uv4=glm.vec2(0, y_top))
                               
                # Right Column
                self._add_quad(verts, norms, cols, inds, uvs,
                               w_end + glm.vec3(0, y_bottom, 0), p2 + glm.vec3(0, y_bottom, 0),
                               p2 + glm.vec3(0, y_top, 0), w_end + glm.vec3(0, y_top, 0),
                               normal, self.color,
                               uv1=glm.vec2(edge_len - margin, y_bottom), uv2=glm.vec2(edge_len, y_bottom),
                               uv3=glm.vec2(edge_len, y_top), uv4=glm.vec2(edge_len - margin, y_top))
                
                # Center Area Logic
                wall_vec = w_end - w_start
                wall_len = glm.length(wall_vec)
                wall_dir = glm.normalize(wall_vec)
                
                window_style = self.style_params.get("window_style", "single")
                
                window_intervals = [] # List of (start_dist, end_dist)
                
                if window_style == "vertical_stripes" and wall_len > 2.0:
                    # Thin vertical windows
                    win_w = 0.8
                    gap_w = 0.8
                    period = win_w + gap_w
                    
                    # Calculate how many fit
                    count = int(wall_len / period)
                    if count < 1: count = 1
                    
                    # Center them
                    total_content = count * period - gap_w
                    base_offset = (wall_len - total_content) / 2
                    
                    # Shift every other floor
                    row_shift = 0
                    if (f % 2) == 1:
                        row_shift = period * 0.5
                        
                    # Generate intervals
                    for i in range(count):
                        s = base_offset + row_shift + i * period
                        e = s + win_w
                        
                        # Clip to wall bounds
                        if s < 0: s = 0
                        if e > wall_len: e = wall_len
                        
                        if e > s + 0.1: # Only if visible
                            window_intervals.append((s, e))
                            
                else:
                    # Single wide window
                    window_intervals.append((0.0, wall_len))
                
                # Draw Walls and Windows
                curr_dist = 0.0
                
                for (s, e) in window_intervals:
                    # Draw Wall before window (if any gap)
                    if s > curr_dist + 0.01:
                        p_wall_start = w_start + wall_dir * curr_dist
                        p_wall_end = w_start + wall_dir * s
                        self._add_quad(verts, norms, cols, inds, uvs,
                                       p_wall_start + glm.vec3(0, y_bottom, 0), p_wall_end + glm.vec3(0, y_bottom, 0),
                                       p_wall_end + glm.vec3(0, y_top, 0), p_wall_start + glm.vec3(0, y_top, 0),
                                       normal, self.color,
                                       uv1=glm.vec2(margin + curr_dist, y_bottom), uv2=glm.vec2(margin + s, y_bottom),
                                       uv3=glm.vec2(margin + s, y_top), uv4=glm.vec2(margin + curr_dist, y_top))
                    
                    # Draw Window
                    p_win_start = w_start + wall_dir * s
                    p_win_end = w_start + wall_dir * e
                    
                    # Window dimensions
                    win_h = real_floor_h * self.window_ratio
                    sill_h = (real_floor_h - win_h) / 2
                    
                    y_sill = y_bottom + sill_h
                    y_head = y_top - sill_h
                    
                    # Sill
                    self._add_quad(verts, norms, cols, inds, uvs,
                                   p_win_start + glm.vec3(0, y_bottom, 0), p_win_end + glm.vec3(0, y_bottom, 0),
                                   p_win_end + glm.vec3(0, y_sill, 0), p_win_start + glm.vec3(0, y_sill, 0),
                                   normal, self.color,
                                   uv1=glm.vec2(margin + s, y_bottom), uv2=glm.vec2(margin + e, y_bottom),
                                   uv3=glm.vec2(margin + e, y_sill), uv4=glm.vec2(margin + s, y_sill))
                                   
                    # Header
                    self._add_quad(verts, norms, cols, inds, uvs,
                                   p_win_start + glm.vec3(0, y_head, 0), p_win_end + glm.vec3(0, y_head, 0),
                                   p_win_end + glm.vec3(0, y_top, 0), p_win_start + glm.vec3(0, y_top, 0),
                                   normal, self.color,
                                   uv1=glm.vec2(margin + s, y_head), uv2=glm.vec2(margin + e, y_head),
                                   uv3=glm.vec2(margin + e, y_top), uv4=glm.vec2(margin + s, y_top))
                                   
                    # Inset Window
                    inset = -normal * self.inset_depth
                    
                    w_p1 = p_win_start + glm.vec3(0, y_sill, 0)
                    w_p2 = p_win_end + glm.vec3(0, y_sill, 0)
                    w_p3 = p_win_end + glm.vec3(0, y_head, 0)
                    w_p4 = p_win_start + glm.vec3(0, y_head, 0)
                    
                    i_p1 = w_p1 + inset
                    i_p2 = w_p2 + inset
                    i_p3 = w_p3 + inset
                    i_p4 = w_p4 + inset
                    
                    # Glass
                    self._add_quad(verts, norms, cols, inds, uvs, i_p1, i_p2, i_p3, i_p4, normal, self.window_color,
                                   uv1=glm.vec2(margin + s, y_sill), uv2=glm.vec2(margin + e, y_sill),
                                   uv3=glm.vec2(margin + e, y_head), uv4=glm.vec2(margin + s, y_head))
                                   
                    # Frames
                    zero_uv = glm.vec2(0, 0)
                    self._add_quad(verts, norms, cols, inds, uvs, w_p1, w_p2, i_p2, i_p1, glm.vec3(0, 1, 0), self.color, zero_uv, zero_uv, zero_uv, zero_uv) # Bot
                    self._add_quad(verts, norms, cols, inds, uvs, i_p4, i_p3, w_p3, w_p4, glm.vec3(0, -1, 0), self.color, zero_uv, zero_uv, zero_uv, zero_uv) # Top
                    self._add_quad(verts, norms, cols, inds, uvs, w_p4, w_p1, i_p1, i_p4, edge_dir, self.color, zero_uv, zero_uv, zero_uv, zero_uv) # Left
                    self._add_quad(verts, norms, cols, inds, uvs, w_p2, w_p3, i_p3, i_p2, -edge_dir, self.color, zero_uv, zero_uv, zero_uv, zero_uv) # Right
                    
                    curr_dist = e
                    
                # Draw final wall segment
                if curr_dist < wall_len - 0.01:
                    p_wall_start = w_start + wall_dir * curr_dist
                    p_wall_end = w_end
                    p_wall_start = w_start + wall_dir * curr_dist
                    p_wall_end = w_end
                    self._add_quad(verts, norms, cols, inds, uvs,
                                   p_wall_start + glm.vec3(0, y_bottom, 0), p_wall_end + glm.vec3(0, y_bottom, 0),
                                   p_wall_end + glm.vec3(0, y_top, 0), p_wall_start + glm.vec3(0, y_top, 0),
                                   normal, self.color,
                                   uv1=glm.vec2(margin + curr_dist, y_bottom), uv2=glm.vec2(edge_len - margin, y_bottom),
                                   uv3=glm.vec2(edge_len - margin, y_top), uv4=glm.vec2(margin + curr_dist, y_top))

    def _add_antenna(self, pos, y_start, verts, norms, cols, inds, uvs):
        # Simple pole
        h = random.uniform(2.0, 8.0)
        w = 0.2
        
        p = glm.vec3(pos.x, 0, pos.y)
        
        # 4 sides
        p1 = p + glm.vec3(-w, y_start, -w)
        p2 = p + glm.vec3(w, y_start, -w)
        p3 = p + glm.vec3(w, y_start, w)
        p4 = p + glm.vec3(-w, y_start, w)
        
        t1 = p1 + glm.vec3(0, h, 0)
        t2 = p2 + glm.vec3(0, h, 0)
        t3 = p3 + glm.vec3(0, h, 0)
        t4 = p4 + glm.vec3(0, h, 0)
        
        color = glm.vec4(0.5, 0.5, 0.5, 1.0)
        
        # Antenna just uses simple coloring, no specific texture mapping needed, use 0
        zu = glm.vec2(0,0)
        self._add_quad(verts, norms, cols, inds, uvs, p1, p2, t2, t1, glm.vec3(0, 0, -1), color, zu, zu, zu, zu)
        self._add_quad(verts, norms, cols, inds, uvs, p2, p3, t3, t2, glm.vec3(1, 0, 0), color, zu, zu, zu, zu)
        self._add_quad(verts, norms, cols, inds, uvs, p3, p4, t4, t3, glm.vec3(0, 0, 1), color, zu, zu, zu, zu)
        self._add_quad(verts, norms, cols, inds, uvs, p4, p1, t1, t4, glm.vec3(-1, 0, 0), color, zu, zu, zu, zu)

    def _add_quad(self, verts, norms, cols, inds, uvs, p1, p2, p3, p4, normal, color, uv1, uv2, uv3, uv4):
        idx = len(verts)
        verts.extend([glm.vec4(p1, 1.0), glm.vec4(p2, 1.0), glm.vec4(p3, 1.0), glm.vec4(p4, 1.0)])
        norms.extend([normal] * 4)
        cols.extend([color] * 4)
        uvs.extend([uv1, uv2, uv3, uv4])
        inds.extend([idx, idx+1, idx+2, idx, idx+2, idx+3])
