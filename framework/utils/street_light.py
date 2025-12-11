from framework.shapes.shape import Shape
import numpy as np
from pyglm import glm

class StreetLight:
    def __init__(self):
        self.height = 6.0
        self.arm_length = 2.0
        self.pole_width = 0.3
        
        # Calculate bulb position relative to base (0,0,0)
        # Pole goes up to height
        # Arm extends arm_length
        # Bulb is at end of arm, slightly down?
        self.bulb_offset = glm.vec3(self.arm_length * 0.9, self.height - 0.5, 0.0)

    def generate_mesh(self):
        shape = Shape()
        verts = []
        norms = []
        cols = []
        inds = []
        
        color_pole = glm.vec4(0.1, 0.1, 0.1, 1.0)
        color_bulb = glm.vec4(1.0, 1.0, 0.8, 1.0)
        
        # 1. Pole (Box for simplicity)
        h = self.height
        w = self.pole_width
        
        # Vertical Part
        self._add_box(verts, norms, cols, inds, 
                      glm.vec3(-w/2, 0, -w/2), 
                      glm.vec3(w/2, h, w/2), 
                      color_pole)
                      
        # horizontal Part (Arm)
        arm_start = glm.vec3(0, h - w, 0) # Near top
        arm_end = glm.vec3(self.arm_length, h, w) # Extend +X
        self._add_box(verts, norms, cols, inds,
                      glm.vec3(0, h - w, -w/2),
                      glm.vec3(self.arm_length, h, w/2),
                      color_pole)
                      
        # Bulb (Small box at end)
        b_pos = self.bulb_offset
        b_size = 0.4
        self._add_box(verts, norms, cols, inds,
                      b_pos - glm.vec3(b_size/2, b_size/2, b_size/2),
                      b_pos + glm.vec3(b_size/2, b_size/2, b_size/2),
                      color_bulb)

        shape.vertices = np.array([v.to_list() for v in verts], dtype=np.float32)
        shape.normals = np.array([n.to_list() for n in norms], dtype=np.float32)
        shape.uvs = np.zeros((len(verts), 2), dtype=np.float32)
        shape.colors = np.array([c.to_list() for c in cols], dtype=np.float32)
        shape.indices = np.array(inds, dtype=np.uint32)
        
        return shape

    def _add_box(self, verts, norms, cols, inds, min_p, max_p, color):
        # Adds a box from min_p to max_p
        idx = len(verts)
        
        # 8 corners
        p0 = glm.vec3(min_p.x, min_p.y, min_p.z)
        p1 = glm.vec3(max_p.x, min_p.y, min_p.z)
        p2 = glm.vec3(max_p.x, max_p.y, min_p.z)
        p3 = glm.vec3(min_p.x, max_p.y, min_p.z)
        
        p4 = glm.vec3(min_p.x, min_p.y, max_p.z)
        p5 = glm.vec3(max_p.x, min_p.y, max_p.z)
        p6 = glm.vec3(max_p.x, max_p.y, max_p.z)
        p7 = glm.vec3(min_p.x, max_p.y, max_p.z)
        
        # Faces
        # Front (Z min)
        self._add_quad(verts, norms, cols, inds, p0, p1, p2, p3, glm.vec3(0, 0, -1), color)
        # Back (Z max)
        self._add_quad(verts, norms, cols, inds, p5, p4, p7, p6, glm.vec3(0, 0, 1), color)
        # Left (X min)
        self._add_quad(verts, norms, cols, inds, p4, p0, p3, p7, glm.vec3(-1, 0, 0), color)
        # Right (X max)
        self._add_quad(verts, norms, cols, inds, p1, p5, p6, p2, glm.vec3(1, 0, 0), color)
        # Top (Y max)
        self._add_quad(verts, norms, cols, inds, p3, p2, p6, p7, glm.vec3(0, 1, 0), color)
        # Bottom (Y min)
        self._add_quad(verts, norms, cols, inds, p4, p5, p1, p0, glm.vec3(0, -1, 0), color)

    def _add_quad(self, verts, norms, cols, inds, p1, p2, p3, p4, normal, color):
        idx = len(verts)
        verts.extend([glm.vec4(p1, 1.0), glm.vec4(p2, 1.0), glm.vec4(p3, 1.0), glm.vec4(p4, 1.0)])
        norms.extend([normal] * 4)
        cols.extend([color] * 4)
        inds.extend([idx, idx+1, idx+2, idx, idx+2, idx+3])
