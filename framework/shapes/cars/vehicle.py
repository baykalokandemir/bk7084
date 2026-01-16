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

from framework.utils.mesh_batcher import MeshBatcher

class BaseVehicle(Object):
    # Static cache for batched geometry per class
    # Key: Class (e.g. Tank) -> Value: List of (Shape, Material)
    _class_batch_cache = {}

    def __init__(self, transform=glm.mat4(1.0)):
        super().__init__(transform)
        self.parts = []
        self.body_mat, self.wheel_mat, self.glass_mat, self.glow_mat = get_materials()
        
        cls = self.__class__
        
        # Check if we have cached batches for this vehicle type
        if cls not in BaseVehicle._class_batch_cache:
            self._build_class_batches(cls)
            
        # Instantiate MeshObjects from cached shapes
        cached_data = BaseVehicle._class_batch_cache[cls]
        for shape, mat in cached_data:
            # Create a new MeshObject sharing the shape and material
            obj = MeshObject(shape, mat)
            # Batched meshes have transforms baked in, so local transform is Identity
            obj.local_transform = glm.mat4(1.0)
            self.parts.append(obj)
            
    def _build_class_batches(self, cls):
        # 1. Setup Batchers
        self._batchers = {
            'body': MeshBatcher(),
            'wheel': MeshBatcher(),
            'glass': MeshBatcher(),
            'glow': MeshBatcher()
        }
        self._building_batch = True
        
        # 2. Generate Geometry (Calls add_box, add_wheel, etc.)
        self.create_geometry()
        
        self._building_batch = False
        
        # 3. Build & Cache
        cache_entry = []
        mat_map = {
            'body': self.body_mat,
            'wheel': self.wheel_mat,
            'glass': self.glass_mat,
            'glow': self.glow_mat
        }
        
        for key, batcher in self._batchers.items():
            mat = mat_map[key]
            # Build creates a MeshObject with a Shape inside
            batch_obj = batcher.build(mat)
            if batch_obj:
                cache_entry.append((batch_obj.mesh, mat))
                
        BaseVehicle._class_batch_cache[cls] = cache_entry
        del self._batchers

    def create_geometry(self):
        pass
        
    def draw(self, camera, lights):
        for part in self.parts:
            part.transform = self.transform * part.local_transform
            part.draw(camera, lights)

    def _get_batcher(self, mat):
        if mat == self.wheel_mat: return self._batchers['wheel']
        if mat == self.glass_mat: return self._batchers['glass']
        if mat == self.glow_mat: return self._batchers['glow']
        return self._batchers['body']

    def add_box(self, color, size, pos, mat):
        if hasattr(self, '_building_batch') and self._building_batch:
            batcher = self._get_batcher(mat)
            
            mesh = Cube(color=color, side_length=1.0)
            mesh.createGeometry()
            
            s = glm.scale(size)
            t = glm.translate(pos)
            transform = t * s
            
            batcher.add_shape(mesh, transform, color)

    def add_trap(self, color, size, pos, taper, mat):
        if hasattr(self, '_building_batch') and self._building_batch:
            batcher = self._get_batcher(mat)
            
            mesh = Trapezoid(color=color, side_length=1.0, taper_ratio=taper)
            mesh.createGeometry()
            
            s = glm.scale(size)
            t = glm.translate(pos)
            transform = t * s
            
            batcher.add_shape(mesh, transform, color)

    def add_wheel(self, radius, width, pos):
        if hasattr(self, '_building_batch') and self._building_batch:
            batcher = self._batchers['wheel']
            
            c = glm.vec4(0.2, 0.2, 0.2, 1.0)
            mesh = Cylinder(radius=radius, height=width, segments=16, color=c)
            mesh.createGeometry()
            
            rot = glm.rotate(glm.radians(90), glm.vec3(0, 0, 1))
            t = glm.translate(pos)
            transform = t * rot
            
            batcher.add_shape(mesh, transform)
