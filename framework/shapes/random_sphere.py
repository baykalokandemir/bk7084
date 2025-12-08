from pyglm import glm
from .shape import Shape
import numpy as np
import random

class RandomSphere(Shape):
    """
    Sphere represented by random points on its surface.
    Parameters:
        radius: sphere radius
        point_count: number of points to generate
    """
    def __init__(self, radius=0.5, point_count=10000, color=glm.vec4(1.0), mode='random'):
        self.radius = radius
        self.point_count = point_count
        self.color = color
        self.mode = mode
        super().__init__()

    def createGeometry(self):
        verts = []
        norms = []
        uvs = []
        
        if self.mode == 'random':
            # Golden Section Spiral on Sphere (Fibonacci Sphere)
            # This gives a very even but "random-looking" distribution without grid artifacts.
            # Alternatively, we can use pure random for a more "noisy" look.
            # Let's use pure random for the "glitchy/data" aesthetic.
            
            for _ in range(self.point_count):
                # Uniform random point on sphere
                z = random.uniform(-1.0, 1.0)
                theta = random.uniform(0.0, 2.0 * np.pi)
                r = np.sqrt(1.0 - z*z)
                x = r * np.cos(theta)
                y = r * np.sin(theta)
                
                p = glm.vec3(x, y, z) * self.radius
                verts.append(glm.vec4(p, 1.0))
                norms.append(glm.normalize(p)) # Normal is just the direction from center
                uvs.append(glm.vec2(0.0, 0.0)) # Dummy UVs

        elif self.mode == 'regular':
            # Regular grid distribution (Latitude/Longitude)
            # We need to approximate the point count to find stacks and sectors
            # stacks * sectors ~= point_count
            # Let's assume stacks ~= sectors for roughly square patches at equator
            
            resolution = int(np.sqrt(self.point_count))
            stacks = resolution
            sectors = resolution
            
            sectorStep = 2 * np.pi / sectors
            stackStep = np.pi / stacks
            
            for i in range(stacks + 1):
                stackAngle = np.pi / 2 - i * stackStep        # starting from pi/2 to -pi/2
                xy = self.radius * np.cos(stackAngle)             # r * cos(u)
                z = self.radius * np.sin(stackAngle)              # r * sin(u)
                
                for j in range(sectors + 1):
                    sectorAngle = j * sectorStep           # starting from 0 to 2pi
                    
                    x = xy * np.cos(sectorAngle)             # r * cos(u) * cos(v)
                    y = xy * np.sin(sectorAngle)             # r * cos(u) * sin(v)
                    
                    p = glm.vec3(x, y, z)
                    verts.append(glm.vec4(p, 1.0))
                    norms.append(glm.normalize(p))
                    uvs.append(glm.vec2(float(j) / sectors, float(i) / stacks))

        self.vertices = np.array(verts, dtype=np.float32)
        self.normals  = np.array(norms, dtype=np.float32)
        self.colors   = np.full((len(verts), 4), self.color, dtype=np.float32)
        self.uvs      = np.array(uvs, dtype=np.float32)
        self.indices  = None # No indices for pure point cloud
