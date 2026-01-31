from pyglm import glm
from framework.objects import MeshObject, Object
from framework.shapes import Cube, Cylinder
from framework.shapes.trapezoid import Trapezoid
from framework.materials import Material

# Shared Materials Builder
def get_materials():
    # grey body
    body = Material()
    body.diffuse_strength = 0.6
    body.specular_strength = 0.9
    body.shininess = 64.0
    
    # black wheels
    wheel = Material()
    wheel.diffuse_strength = 0.2
    
    # window glass (black shiny)
    glass = Material()
    glass.diffuse_strength = 0.1
    glass.specular_strength = 1.0
    glass.shininess = 128.0
    
    # glow
    glow = Material()
    glow.ambient_strength = 2.0
    glow.diffuse_strength = 0.0
    
    return body, wheel, glass, glow

class BaseVehicle(Object):
    def __init__(self, transform=glm.mat4(1.0)):
        super().__init__(transform)
        self.parts = []
        self.max_x = 0.0
        self.max_z = 0.0
        self.bounding_radius = 2.0  # Will be auto-calculated
        
        self.body_mat, self.wheel_mat, self.glass_mat, self.glow_mat = get_materials()
        self.create_geometry()
        self.finalize_bounds()
        
    def regenerate(self):
        self.parts = []
        self.max_x = 0.0
        self.max_z = 0.0
        self.create_geometry()
        self.finalize_bounds()

    def create_geometry(self):
        pass

    def finalize_bounds(self):
       """Calculate bounding radius from tracked extents"""
       import math
       self.bounding_radius = math.sqrt(self.max_x**2 + self.max_z**2)
       print(f"{self.__class__.__name__}: radius={self.bounding_radius:.2f}m (x={self.max_x:.2f}, z={self.max_z:.2f})")
        
    def draw(self, camera, lights):
        for part in self.parts:
            part.transform = self.transform * part.local_transform
            part.draw(camera, lights)
            
    def add_box(self, color, size, pos, mat):
        # Track bounding extents (2D top-down, ignore Y height)
        extent_x = abs(pos.x) + size.x / 2.0
        extent_z = abs(pos.z) + size.z / 2.0
        self.max_x = max(self.max_x, extent_x)
        self.max_z = max(self.max_z, extent_z)

        mesh = Cube(color=color, side_length=1.0)
        s = glm.scale(size)
        t = glm.translate(pos)
        obj = MeshObject(mesh, mat, t * s)
        obj.local_transform = t * s
        self.parts.append(obj)

    def add_trap(self, color, size, pos, taper, mat):
        # Track bounding extents
        extent_x = abs(pos.x) + size.x / 2.0
        extent_z = abs(pos.z) + size.z / 2.0
        self.max_x = max(self.max_x, extent_x)
        self.max_z = max(self.max_z, extent_z)

        mesh = Trapezoid(color=color, side_length=1.0, taper_ratio=taper)
        s = glm.scale(size)
        t = glm.translate(pos)
        obj = MeshObject(mesh, mat, t * s)
        obj.local_transform = t * s
        self.parts.append(obj)

    def add_wheel(self, radius, width, pos):
        # Track bounding extents
        extent_x = abs(pos.x) + radius
        extent_z = abs(pos.z) + radius
        self.max_x = max(self.max_x, extent_x)
        self.max_z = max(self.max_z, extent_z)

        mesh = Cylinder(radius=radius, height=width, segments=16, color=glm.vec4(0.2, 0.2, 0.2, 1.0))
        rot = glm.rotate(glm.radians(90), glm.vec3(0, 0, 1))
        t = glm.translate(pos)
        obj = MeshObject(mesh, self.wheel_mat, t * rot)
        obj.local_transform = t * rot
        self.parts.append(obj)
