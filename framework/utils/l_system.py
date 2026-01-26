from pyglm import glm
import random

class LSystem:
    def __init__(self, axiom="F", rules=None, angle=30.0, length=2.0):
        self.axiom = axiom
        self.rules = rules if rules is not None else {"F": "F[+F][-F]"}
        self.angle = glm.radians(angle)
        self.length = length

    def generate_string(self, iterations=2):
        s = self.axiom
        for _ in range(iterations):
            next_s = ""
            for char in s:
                next_s += self.rules.get(char, char)
            s = next_s
        return s

    def interpret_transforms(self, s, max_points=None):
        """
        Interprets the string 's' into a list of glm.mat4 transforms.
        Returns at most max_points transforms (if specified).
        """
        stack = []
        # State: position, rotation (quat or angle?), length
        # Simple turtle in 3D:
        # Start at origin, pointing UP (Y axis) or FORWARD (Z axis)?
        # Let's say Y axis to build trees.
        
        pos = glm.vec3(0, 0, 0)
        heading = glm.vec3(0, 1, 0) # Up
        # We need a full orientation matrix/quat ideally.
        # Let's use a 4x4 matrix as state.
        current_transform = glm.mat4(1.0)
        
        results = []
        
        # Helper to append current state
        def add_result(mat):
            if max_points is None or len(results) < max_points:
                results.append(glm.mat4(mat)) # Copy

        # We assume F means "Move forward AND place an object there" or "Draw line".
        # For object placement, we usually place at the start or end of the segment.
        # Let's place at the END of the move.
        
        for char in s:
            if max_points is not None and len(results) >= max_points:
                break
                
            if char == "F":
                # Move forward along LOCAL Y axis of current transform
                # translate(0, length, 0)
                move = glm.translate(glm.vec3(0, self.length, 0))
                current_transform = current_transform * move
                
                # capture position
                add_result(current_transform)
                
            elif char == "+": # Rotate Z
                rot = glm.rotate(self.angle, glm.vec3(0, 0, 1))
                current_transform = current_transform * rot
            elif char == "-": # Rotate -Z
                rot = glm.rotate(-self.angle, glm.vec3(0, 0, 1))
                current_transform = current_transform * rot
            elif char == "&": # Rotate X
                rot = glm.rotate(self.angle, glm.vec3(1, 0, 0))
                current_transform = current_transform * rot
            elif char == "^": # Rotate -X
                rot = glm.rotate(-self.angle, glm.vec3(1, 0, 0))
                current_transform = current_transform * rot
            elif char == "\\": # Rotate Y
                rot = glm.rotate(self.angle, glm.vec3(0, 1, 0))
                current_transform = current_transform * rot
            elif char == "/": # Rotate -Y
                rot = glm.rotate(-self.angle, glm.vec3(0, 1, 0))
                current_transform = current_transform * rot
            elif char == "[":
                stack.append(glm.mat4(current_transform))
            elif char == "]":
                if stack:
                    current_transform = stack.pop()
                    
        return results

from .hologram_wrapper import HologramWrapper
from ..shapes import Cube, UVSphere, Cone, Cylinder
from ..materials import Material
from ..objects import MeshObject
import OpenGL.GL as gl

class HologramLSystem:
    @staticmethod
    def create_group(root_transform, 
                     source_shapes_pool, 
                     axiom="F", 
                     rules={"F":"F[+F]F[-F]F"}, 
                     iterations=2, 
                     size_limit=4,
                     grid_spacing=0.2, 
                     color=glm.vec3(0,1,1),
                     use_point_cloud=True):
        """
        Generates a group of MeshObjects based on an L-System.
        
        Args:
            root_transform (glm.mat4): The parent transform for the whole group.
            source_shapes_pool (list): A list of Shape objects to cycle through.
            axiom (str): Start string.
            rules (dict): Production rules.
            iterations (int): Number of recursions.
            size_limit (int): Max number of objects to spawn.
            
        Returns:
            list[MeshObject]: The generated objects.
        """
        
        lsys = LSystem(axiom=axiom, rules=rules, length=2.0, angle=45.0)
        s = lsys.generate_string(iterations)
        local_transforms = lsys.interpret_transforms(s, max_points=size_limit)
        
        objects = []
        
        # We assume source_shapes_pool has at least one shape
        if not source_shapes_pool:
            source_shapes_pool = [Cube(1.0)]
            
        pool_idx = 0
        
        slice_mat_ref = Material(vertex_shader="slice_shader.vert", fragment_shader="slice_shader.frag")

        for local_t in local_transforms:
            # Combine root transform with local L-System transform
            # Global = Root * Local
            final_transform = root_transform * local_t
            
            # Pick a shape from the pool
            shape = source_shapes_pool[pool_idx % len(source_shapes_pool)]
            pool_idx += 1
            
            if use_point_cloud:
                obj = HologramWrapper.create(
                    shape,
                    spacing=grid_spacing,
                    color=color,
                    transform=final_transform
                )
                objects.append(obj)
            else:
                # Manual slice fallback
                if shape.VAO is None:
                    shape.createGeometry()
                    shape.createBuffers()
                    
                obj = MeshObject(shape, slice_mat_ref, transform=final_transform, draw_mode=gl.GL_TRIANGLES)
                # Need to manually set slice uniforms later? 
                # Yes, scene manager handles that usually.
                objects.append(obj)
                
        return objects
