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
    # Static cache for geometry to prevent redundant VAO creation
    _geometry_cache = {}

    def __init__(self, transform=glm.mat4(1.0)):
        super().__init__(transform)
        self.parts = []
        self.body_mat, self.wheel_mat, self.glass_mat, self.glow_mat = get_materials()
        self.create_geometry()
        
    def create_geometry(self):
        pass
        
    def draw(self, camera, lights):
        for part in self.parts:
            part.transform = self.transform * part.local_transform
            part.draw(camera, lights)
            
    def _get_cached_shape(self, key, factory_func):
        if key not in BaseVehicle._geometry_cache:
            mesh = factory_func()
            mesh.createGeometry()
            mesh.createBuffers()
            BaseVehicle._geometry_cache[key] = mesh
        return BaseVehicle._geometry_cache[key]

    def add_box(self, color, size, pos, mat):
        # Cache Key: (Type, Color)
        # We use a unit cube, size is applied via transform
        key = ("cube", tuple(color))
        
        mesh = self._get_cached_shape(key, lambda: Cube(color=color, side_length=1.0))

        s = glm.scale(size)
        t = glm.translate(pos)
        obj = MeshObject(mesh, mat, t * s)
        obj.local_transform = t * s
        self.parts.append(obj)

    def add_trap(self, color, size, pos, taper, mat):
        # Cache Key: (Type, Color, Taper)
        key = ("trap", tuple(color), taper)
        
        mesh = self._get_cached_shape(key, lambda: Trapezoid(color=color, side_length=1.0, taper_ratio=taper))
        
        s = glm.scale(size)
        t = glm.translate(pos)
        obj = MeshObject(mesh, mat, t * s)
        obj.local_transform = t * s
        self.parts.append(obj)

    def add_wheel(self, radius, width, pos):
        # Cache Key: (Type, Radius, Width, Color)
        # Cylinder geometry depends on radius/height(width)
        c = glm.vec4(0.2, 0.2, 0.2, 1.0)
        key = ("wheel", radius, width, tuple(c))
        
        mesh = self._get_cached_shape(key, lambda: Cylinder(radius=radius, height=width, segments=16, color=c))

        rot = glm.rotate(glm.radians(90), glm.vec3(0, 0, 1))
        t = glm.translate(pos)
        obj = MeshObject(mesh, self.wheel_mat, t * rot)
        obj.local_transform = t * rot
        self.parts.append(obj)
