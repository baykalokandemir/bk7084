from pyglm import glm
import random
import OpenGL.GL as gl
from .l_system import LSystem
from .hologram_wrapper import HologramWrapper
from ..shapes import Cube, UVSphere, Cylinder, Cone
from ..materials import Material
from ..objects import MeshObject

class HologramCluster:
    def __init__(self, root_position=glm.vec3(0, -1.0, 0)):
        self.objects = []
        self.root_position = root_position
        
        # Animation State
        self.group_rotation = 0.0
        self.group_speed = 0.3
        
        # Internal storage for individual animations
        # List of dicts: { 'obj': MeshObject, 'initial_local_transform': mat4, 'axis': vec3, 'speed': float, 'angle': float }
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
                # Wrap as Hologram
                obj = HologramWrapper.create(
                    shape,
                    spacing=config.GRID_SPACING,
                    color=glm.vec3(*config.POINT_CLOUD_COLOR),
                    transform=local_t # Initial placement is purely local L-System layout
                )
            else:
                # Solid / Slice Mode
                if shape.VAO is None:
                    shape.createGeometry()
                    shape.createBuffers()
                
                # We need to clone the shape logic or just use MeshObject. 
                # MeshObject shares VAO.
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
        group_parent_transform = glm.translate(self.root_position) * glm.rotate(self.group_rotation, glm.vec3(0, 1, 0))
        
        # 2. Update Individuals
        for data in self._anim_data:
            data['angle'] += data['speed'] * dt
            
            # Local Spin
            spin_rot = glm.rotate(data['angle'], data['axis'])
            
            # Compose: Parent * LSystemPos * Spin
            # Note: LSystemPos (initial_local_transform) includes the translation from the center of the cluster.
            # If we do LSystemPos * Spin, we spin in place at that offset? 
            # Yes, because LSystem logic T matrix is T * R * S. 
            # If we append Spin: T * R * S * Spin. Spin happens in local object space. Correct.
            
            local_final = data['initial_local_transform'] * spin_rot
            
            # Apply Global
            data['obj'].transform = group_parent_transform * local_final
            
    def update_uniforms(self, config, time):
        """Updates visual uniforms (color, size, etc)."""
        for obj in self.objects:
             if hasattr(obj.material, 'uniforms'):
                 obj.material.uniforms["enable_glow"] = config.ENABLE_GLOW
                 obj.material.uniforms["base_color"] = glm.vec3(*config.POINT_CLOUD_COLOR)
                 obj.material.uniforms["point_size"] = config.POINT_SIZE
                 obj.material.uniforms["time"] = time
