from pyglm import glm
import random
import OpenGL.GL as gl
from .l_system import LSystem
from .grid_point_cloud_generator import GridPointCloudGenerator
from ..shapes import Cube, UVSphere, Cylinder, Cone
from ..materials import Material
from ..objects import MeshObject

class HologramConfig:
    # L-System Parameters
    L_ITERATIONS = 2
    L_SIZE_LIMIT = 12
    L_LENGTH = 2.5
    L_ANGLE_MIN = 30.0
    L_ANGLE_MAX = 120.0
    
    # Hologram Settings
    GRID_SPACING = 0.2
    POINT_SIZE = 20.0
    POINT_SHAPE = 1 # 0: Circle, 1: Square
    POINT_SHAPES = ["Circle", "Square"]
    POINT_CLOUD_COLOR = [0.0, 0.9, 1.0] # Cyan
    ENABLE_GLOW = True
    USE_POINT_CLOUD = True
    
    # Post Process shared? Or per-object?
    # Usually post-process is global, but these are object properties.

class Holograms3D:
    def __init__(self, root_position=glm.vec3(0, -1.0, 0), scale=1.0):
        self.objects = []
        self.root_position = root_position
        self.scale = scale
        
        # Animation State
        self.group_rotation = 0.0
        self.group_speed = 0.3
        
        # Internal storage for individual animations
        self._anim_data = [] 
        
    def regenerate(self, config):
        """Rebuilds the cluster based on config."""
        self.objects = []
        self._anim_data = []
        
        # Pool of shapes
        pool = [
            Cube(side_length=1.5),
            UVSphere(radius=0.7),
            Cylinder(radius=0.7, height=1.5),
            Cone(radius=0.7, height=1.5)
        ]
        
        # L-System Logic
        lsys = LSystem(
            axiom="F",
            rules={"F": "F[+F][-F][&F][^F]"},
            length=config.L_LENGTH,
            angle_range=(config.L_ANGLE_MIN, config.L_ANGLE_MAX)
        )
        s = lsys.generate_string(iterations=config.L_ITERATIONS)
        transforms = lsys.interpret_transforms(s, max_points=config.L_SIZE_LIMIT)
        
        # Create Objects
        pool_idx = 0
        
        # Prepare Slice Material if needed (lazy load or just init)
        slice_mat = Material(vertex_shader="slice_shader.vert", fragment_shader="slice_shader.frag")
        
        for local_t in transforms:
            shape = pool[pool_idx % len(pool)]
            pool_idx += 1
            
            if config.USE_POINT_CLOUD:
                # Wrap as Hologram (Internal Helper)
                obj = self._create_hologram_object(
                    shape,
                    spacing=config.GRID_SPACING,
                    color=glm.vec3(*config.POINT_CLOUD_COLOR),
                    transform=local_t
                )
            else:
                # Solid / Slice Mode
                if shape.VAO is None:
                    shape.createGeometry()
                    shape.createBuffers()
                
                obj = MeshObject(shape, slice_mat, transform=local_t, draw_mode=gl.GL_TRIANGLES)
            
            self.objects.append(obj)
            
            # Init Anim Data
            self._anim_data.append({
                'obj': obj,
                'initial_local_transform': glm.mat4(local_t),
                'axis': glm.normalize(glm.vec3(random.uniform(-1,1), random.uniform(-1,1), random.uniform(-1,1))),
                'speed': random.uniform(0.5, 2.0),
                'angle': 0.0
            })
            
    def update(self, dt):
        """Updates group and individual animations."""
        # 1. Update Group
        self.group_rotation += self.group_speed * dt
        # Apply Translation * Rotation * Scale
        model = glm.translate(self.root_position) * glm.rotate(self.group_rotation, glm.vec3(0, 1, 0))
        group_parent_transform = glm.scale(model, glm.vec3(self.scale))
        
        # 2. Update Individuals
        for data in self._anim_data:
            data['angle'] += data['speed'] * dt
            
            # Local Spin
            spin_rot = glm.rotate(data['angle'], data['axis'])
            
            # Compose: Parent * LSystemPos * Spin
            local_final = data['initial_local_transform'] * spin_rot
            
            # Apply Global
            data['obj'].transform = group_parent_transform * local_final
            
    def update_uniforms(self, config, time):
        """Updates visual uniforms (color, size, etc)."""
        for obj in self.objects:
             # Check if it has our custom uniforms (not slice mat)
             # Slice mat has different uniform names
             if hasattr(obj.material, 'uniforms') and "enable_glow" in obj.material.uniforms:
                 obj.material.uniforms["enable_glow"] = config.ENABLE_GLOW
                 obj.material.uniforms["base_color"] = glm.vec3(*config.POINT_CLOUD_COLOR)
                 obj.material.uniforms["point_size"] = config.POINT_SIZE
                 obj.material.uniforms["time"] = time

    def _create_hologram_object(self, source_shape, spacing, color, transform):
        """Internal helper to create a Point Cloud MeshObject."""
        # 1. Generate Point Cloud Geometry
        pc_shape = GridPointCloudGenerator.generate(source_shape, spacing=spacing)
        pc_shape.createBuffers()
        
        # 2. Create Unique Material Instance
        mat = Material(vertex_shader="mikoshi_shader.vert", fragment_shader="mikoshi_shader.frag")
        
        # 3. Configure Material Uniforms (Defaults)
        mat.uniforms["enable_glow"] = True
        mat.uniforms["is_point_mode"] = True
        mat.uniforms["base_color"] = color
        mat.uniforms["point_size"] = 10.0
        mat.uniforms["shape_type"] = 0
        mat.uniforms["anim_x"] = True 
        mat.uniforms["anim_y"] = True 
        mat.uniforms["time"] = 0.0
        
        # 4. Create and Return MeshObject
        obj = MeshObject(pc_shape, mat, transform=transform, draw_mode=gl.GL_POINTS)
        return obj
