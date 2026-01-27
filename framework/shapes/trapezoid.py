from pyglm import glm
from .shape import Shape
import numpy as np

class Trapezoid(Shape):
    """
    A cube-like shape where the top face is scaled down (tapered).
    Useful for car cabins.
    """
    def __init__(self, color=glm.vec4(1.0), side_length=1.0, taper_ratio=0.7):
        self.side_length = side_length
        self.taper_ratio = taper_ratio
        self.color = color
        super().__init__()

    def createGeometry(self):
        s = 0.5 * self.side_length
        ts = s * self.taper_ratio # Tapered size for top vertices

        # 24 vertices (4 per face)
        self.vertices = np.array([
            # front
            glm.vec4(-s, -s, s, 1.0), glm.vec4(s, -s, s, 1.0),
            glm.vec4(ts, s, ts, 1.0), glm.vec4(-ts, s, ts, 1.0),
            # back
            glm.vec4(-s, -s, -s, 1.0), glm.vec4(s, -s, -s, 1.0),
            glm.vec4(ts, s, -ts, 1.0), glm.vec4(-ts, s, -ts, 1.0),
            # top
            glm.vec4(-ts, s, -ts, 1.0), glm.vec4(ts, s, -ts, 1.0),
            glm.vec4(ts, s, ts, 1.0), glm.vec4(-ts, s, ts, 1.0),
            # bottom
            glm.vec4(-s, -s, -s, 1.0), glm.vec4(s, -s, -s, 1.0),
            glm.vec4(s, -s, s, 1.0), glm.vec4(-s, -s, s, 1.0),
            # right
            glm.vec4(s, -s, -s, 1.0), glm.vec4(ts, s, -ts, 1.0),
            glm.vec4(ts, s, ts, 1.0), glm.vec4(s, -s, s, 1.0),
            # left
            glm.vec4(-s, -s, -s, 1.0), glm.vec4(-ts, s, -ts, 1.0),
            glm.vec4(-ts, s, ts, 1.0), glm.vec4(-s, -s, s, 1.0),
        ], dtype=np.float32)

        # Normals need to be recalculated because faces are slanted.
        # For simplicity in this low-poly style, we can approximate or calculate per face.
        # Since we want flat shading, face normals are best.
        
        # Helper to calculate normal of a triangle/quad
        def calc_normal(p1, p2, p3):
            v1 = glm.vec3(p2) - glm.vec3(p1)
            v2 = glm.vec3(p3) - glm.vec3(p1)
            return glm.normalize(glm.cross(v1, v2))

        # We can compute normals for each face based on the vertices we just defined.
        # Front face: 0, 1, 2
        n_front = calc_normal(self.vertices[0], self.vertices[1], self.vertices[2])
        # Back face: 5, 4, 7 (reversed winding for back) -> 4, 5, 6 is back facing away? 
        # Let's stick to the standard cube order and compute.
        # Back indices in cube were: 5, 4, 7, 5, 7, 6. 
        # Verts 4,5,6,7 are back. 4 is bottom-left-back (-s,-s,-s). 5 is bottom-right-back.
        # 6 is top-right-back. 7 is top-left-back.
        # Normal should point -Z roughly.
        n_back = calc_normal(self.vertices[5], self.vertices[4], self.vertices[7]) 
        
        n_top = glm.vec3(0, 1, 0) # Top is flat
        n_bottom = glm.vec3(0, -1, 0) # Bottom is flat
        
        # Right face: 16, 17, 18 (bottom-back, top-back, top-front)
        n_right = calc_normal(self.vertices[16], self.vertices[17], self.vertices[18])
        
        # Left face: 20, 21, 22
        n_left = calc_normal(self.vertices[20], self.vertices[21], self.vertices[22])

        self.normals = np.array([
            *([n_front] * 4),
            *([n_back] * 4),
            *([n_top] * 4),
            *([n_bottom] * 4),
            *([n_right] * 4),
            *([n_left] * 4),
        ], dtype=np.float32)

        # colors
        self.colors = np.full((len(self.vertices),4), self.color, dtype=np.float32)

        # UVs - simple mapping
        self.uvs = np.array([
            glm.vec2(0, 0), glm.vec2(1, 0), glm.vec2(1, 1), glm.vec2(0, 1),
            glm.vec2(1, 0), glm.vec2(0, 0), glm.vec2(0, 1), glm.vec2(1, 1),
            glm.vec2(0, 1), glm.vec2(0, 0), glm.vec2(1, 0), glm.vec2(1, 1),
            glm.vec2(0, 0), glm.vec2(0, 1), glm.vec2(1, 1), glm.vec2(1, 0),
            glm.vec2(0, 0), glm.vec2(0, 1), glm.vec2(1, 1), glm.vec2(1, 0),
            glm.vec2(1, 0), glm.vec2(1, 1), glm.vec2(0, 1), glm.vec2(0, 0),
        ], dtype=np.float32)

        # indices - same as cube
        self.indices = np.array([
            0, 1, 2, 0, 2, 3,  # front
            5, 4, 7, 5, 7, 6, # back
            9, 8, 11, 9, 11, 10,  # top
            12, 13, 14, 12, 14, 15,  # bottom
            16, 17, 18, 16, 18, 19,  # right
            21, 20, 23, 21, 23, 22 # left
        ], dtype=np.uint32)
