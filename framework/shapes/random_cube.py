from pyglm import glm
from .shape import Shape
import numpy as np
import random

class RandomCube(Shape):
    """
    Cube represented by random points on its surface.
    Parameters:
        side_length: length of the cube side
        point_count: number of points to generate
        mode: 'random' or 'regular'
    """
    def __init__(self, side_length=1.0, point_count=10000, color=glm.vec4(1.0), mode='random'):
        self.side_length = side_length
        self.point_count = point_count
        self.color = color
        self.mode = mode
        super().__init__()

    def createGeometry(self):
        verts = []
        norms = []
        uvs = []
        
        s = 0.5 * self.side_length
        
        # 6 faces
        # Front: z = s
        # Back: z = -s
        # Right: x = s
        # Left: x = -s
        # Top: y = s
        # Bottom: y = -s
        
        if self.mode == 'random':
            for _ in range(self.point_count):
                face = random.randint(0, 5)
                u = random.uniform(-s, s)
                v = random.uniform(-s, s)
                
                if face == 0: # Front
                    p = glm.vec3(u, v, s)
                    n = glm.vec3(0, 0, 1)
                elif face == 1: # Back
                    p = glm.vec3(u, v, -s)
                    n = glm.vec3(0, 0, -1)
                elif face == 2: # Right
                    p = glm.vec3(s, u, v)
                    n = glm.vec3(1, 0, 0)
                elif face == 3: # Left
                    p = glm.vec3(-s, u, v)
                    n = glm.vec3(-1, 0, 0)
                elif face == 4: # Top
                    p = glm.vec3(u, s, v)
                    n = glm.vec3(0, 1, 0)
                elif face == 5: # Bottom
                    p = glm.vec3(u, -s, v)
                    n = glm.vec3(0, -1, 0)
                    
                verts.append(glm.vec4(p, 1.0))
                norms.append(n)
                uvs.append(glm.vec2(0.0, 0.0))

        elif self.mode == 'regular':
            # Points per face
            points_per_face = self.point_count // 6
            grid_size = int(np.sqrt(points_per_face))
            step = self.side_length / grid_size
            
            # Helper to generate grid on a face
            def generate_face(c1_idx, c2_idx, fixed_idx, fixed_val, normal):
                for i in range(grid_size):
                    for j in range(grid_size):
                        # Center the grid
                        c1 = -s + (i + 0.5) * step
                        c2 = -s + (j + 0.5) * step
                        
                        coords = [0.0, 0.0, 0.0]
                        coords[c1_idx] = c1
                        coords[c2_idx] = c2
                        coords[fixed_idx] = fixed_val
                        
                        p = glm.vec3(coords[0], coords[1], coords[2])
                        verts.append(glm.vec4(p, 1.0))
                        norms.append(normal)
                        uvs.append(glm.vec2(i/grid_size, j/grid_size))

            # Generate 6 faces
            generate_face(0, 1, 2, s, glm.vec3(0, 0, 1))   # Front
            generate_face(0, 1, 2, -s, glm.vec3(0, 0, -1)) # Back
            generate_face(1, 2, 0, s, glm.vec3(1, 0, 0))   # Right
            generate_face(1, 2, 0, -s, glm.vec3(-1, 0, 0)) # Left
            generate_face(0, 2, 1, s, glm.vec3(0, 1, 0))   # Top
            generate_face(0, 2, 1, -s, glm.vec3(0, -1, 0)) # Bottom

        self.vertices = np.array(verts, dtype=np.float32)
        self.normals  = np.array(norms, dtype=np.float32)
        self.colors   = np.full((len(verts), 4), self.color, dtype=np.float32)
        self.uvs      = np.array(uvs, dtype=np.float32)
        self.indices  = None
