from pyglm import glm
from .shape import Shape
from .cylinder import Cylinder
import numpy as np
import math

class Car(Shape):
    """
    A basic car shape consisting of a triangular prism body and 4 wheels.
    """
    def __init__(self, body_color=glm.vec4(0.8, 0.2, 0.2, 1.0), wheel_color=glm.vec4(0.0, 0.0, 0.0, 1.0)):
        self.body_color = body_color
        self.wheel_color = wheel_color
        super().__init__()

    def createGeometry(self):
        # Lists to accumulate data
        all_vertices = []
        all_normals = []
        all_colors = []
        all_uvs = []
        all_indices = []
        
        index_offset = 0
        
        # Lift everything by wheel radius so it sits on ground
        lift = 0.3 

        # 1. Body (Rectangular Prism)
        body_len = 2.0
        body_width = 1.0
        body_height = 0.6
        
        # Vertices (Lifted)
        # Front face (z = +len/2)
        f_top_l = glm.vec4(-body_width/2, body_height + lift, body_len/2, 1)
        f_top_r = glm.vec4(body_width/2, body_height + lift, body_len/2, 1)
        f_bot_l = glm.vec4(-body_width/2, 0 + lift, body_len/2, 1)
        f_bot_r = glm.vec4(body_width/2, 0 + lift, body_len/2, 1)
        
        # Back face (z = -len/2)
        b_top_l = glm.vec4(-body_width/2, body_height + lift, -body_len/2, 1)
        b_top_r = glm.vec4(body_width/2, body_height + lift, -body_len/2, 1)
        b_bot_l = glm.vec4(-body_width/2, 0 + lift, -body_len/2, 1)
        b_bot_r = glm.vec4(body_width/2, 0 + lift, -body_len/2, 1)
        
        # We need to build faces (verts, norms, uvs)
        
        def add_quad(v1, v2, v3, v4, n):
            nonlocal index_offset
            # v1-v2-v3-v4 (counter clockwise)
            # 1, 2, 3
            # 1, 3, 4
            base = index_offset
            all_vertices.extend([v1, v2, v3, v4])
            all_normals.extend([n, n, n, n])
            all_colors.extend([self.body_color]*4)
            all_uvs.extend([glm.vec2(0,0), glm.vec2(1,0), glm.vec2(1,1), glm.vec2(0,1)]) # Dummy UVs
            all_indices.extend([base, base+1, base+2, base, base+2, base+3])
            index_offset += 4

        # Front Face
        add_quad(f_top_l, f_bot_l, f_bot_r, f_top_r, glm.vec3(0, 0, 1))
        
        # Back Face
        add_quad(b_top_r, b_bot_r, b_bot_l, b_top_l, glm.vec3(0, 0, -1))
        
        # Top Face
        add_quad(b_top_l, f_top_l, f_top_r, b_top_r, glm.vec3(0, 1, 0))
        
        # Bottom Face
        add_quad(f_bot_l, b_bot_l, b_bot_r, f_bot_r, glm.vec3(0, -1, 0))
        
        # Left Face
        add_quad(b_top_l, b_bot_l, f_bot_l, f_top_l, glm.vec3(-1, 0, 0))
        
        # Right Face
        add_quad(f_top_r, f_bot_r, b_bot_r, b_top_r, glm.vec3(1, 0, 0))
        
        # 2. Wheels
        # Use Cylinder class to generate data, then transform and append.
        wheel_radius = 0.3
        wheel_width = 0.2
        wheel_shape = Cylinder(radius=wheel_radius, height=wheel_width, segments=16, color=self.wheel_color)
        wheel_shape.createGeometry()
        
        # Wheel positions (Lifted)
        # Center of wheel should be at y = lift (0.3)
        
        # Front Left
        fl_pos = glm.vec3(-body_width/2, lift, body_len/3)
        # Front Right
        fr_pos = glm.vec3(body_width/2, lift, body_len/3)
        # Back Left
        bl_pos = glm.vec3(-body_width/2, lift, -body_len/3)
        # Back Right
        br_pos = glm.vec3(body_width/2, lift, -body_len/3)
        
        # Cylinder is Y-aligned. We need to rotate it 90 deg around Z to be X-aligned (like wheels).
        # And translate to position.
        
        rot_z = glm.rotate(glm.radians(90), glm.vec3(0, 0, 1))
        
        wheels = [fl_pos, fr_pos, bl_pos, br_pos]
        
        # We need to convert numpy arrays back to lists of glm objects for easy processing
        # Or just process numpy arrays directly.
        w_verts = [glm.vec4(*v) for v in wheel_shape.vertices]
        w_norms = [glm.vec3(*n) for n in wheel_shape.normals]
        w_uvs   = [glm.vec2(*u) for u in wheel_shape.uvs]
        w_idxs  = wheel_shape.indices.tolist()
        
        for pos in wheels:
            # Transform matrix: Translate * Rotate
            model = glm.translate(pos) * rot_z
            
            # Inverse transpose for normals (rotation only is fine since orthogonal)
            normal_mat = glm.mat3(model) 
            
            base = index_offset
            
            for i in range(len(w_verts)):
                v = w_verts[i]
                n = w_norms[i]
                
                v_new = model * v
                n_new = glm.normalize(normal_mat * n)
                
                all_vertices.append(v_new)
                all_normals.append(n_new)
                all_colors.append(self.wheel_color)
                all_uvs.append(w_uvs[i])
            
            for idx in w_idxs:
                all_indices.append(base + idx)
                
            index_offset += len(w_verts)

        # Final conversion to numpy
        # Flatten the glm objects into float lists
        
        # Vertices (N, 4)
        self.vertices = np.array([v.to_list() for v in all_vertices], dtype=np.float32)
        self.normals  = np.array([n.to_list() for n in all_normals], dtype=np.float32)
        self.colors   = np.array([c.to_list() for c in all_colors], dtype=np.float32)
        self.uvs      = np.array([u.to_list() for u in all_uvs], dtype=np.float32)
        self.indices  = np.array(all_indices, dtype=np.uint32)
