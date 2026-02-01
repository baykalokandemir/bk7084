from pyglm import glm
from ..shapes.quad import Quad
from .instanced_mesh_object import InstancedMeshObject
from ..materials import Material
import random

class Cloud:
    def __init__(self, renderer, pos=glm.vec3(0), scale=1.0, color=glm.vec4(1.0)):
        self.renderer = renderer
        self.pos = pos
        self.scale = scale
        self.color = color

        # L-System Configuration
        # Minkowski Sausage (Quadratic Koch Island)
        self.axiom = "F-F-F-F"
        self.rules = {
            "F": "F+F-F-FF+F+F-F" 
        }
        self.iterations = 2
        self.angle = glm.radians(90.0)

        # Generate String
        s = self.axiom
        for _ in range(self.iterations):
            s = self._apply_rules(s)
            
        # Interpret String
        transforms, colors = self.interpret(s)
        
        # Create Object
        leaf = Quad(width=1, height=1)
        mat = Material()
        mat.color = self.color
        mat.ambient_strength = 1.0 
        
        self.inst = InstancedMeshObject(leaf, mat, transforms, colors)
        self.renderer.addObject(self.inst)

    def _apply_rules(self, s):
        res = ""
        for char in s:
            res += self.rules.get(char, char)
        return res

    def interpret(self, s):
        # Nested State class as per framework
        class State:
            def __init__(self, pos, ang):
                self.pos = pos
                self.ang = ang
            
            def clone(self):
                return State(glm.vec3(self.pos), self.ang)

        transforms = []
        colors = []
        
        # Turtle State
        st = State(pos=glm.vec3(0.0), ang=0.0)
        stack = []
        
        # Heuristic step length calculation
        step_len = 1.0 * (1.0 / (4**self.iterations)) * self.scale * 10.0
        
        # First pass: Collect points to calculate center
        points = []
        sim_pos = glm.vec3(0.0)
        sim_ang = 0.0
        
        for char in s:
            if char == "F":
                # Save current position
                points.append(st.pos)
                
                # Move forward
                direction = glm.vec3(glm.cos(st.ang), glm.sin(st.ang), 0.0)
                st.pos = st.pos + direction * step_len
                
            elif char == "+":
                st.ang -= self.angle
            elif char == "-":
                st.ang += self.angle
            elif char == "[":
                stack.append(st.clone())
            elif char == "]":
                st = stack.pop()

        # Calculate Center
        avg_pos = glm.vec3(0.0)
        if len(points) > 0:
            avg_pos = sum(points, glm.vec3(0)) / len(points)
            
        # Second pass: Generate Transforms centered around self.pos
        
        puff_size = glm.vec3(step_len * 2.5)
        # Rotation for flat cloud (face up)
        base_quat = glm.rotate(glm.radians(-90), glm.vec3(1, 0, 0))
        
        for p in points:
            # Center relative to local origin
            local_p = p - avg_pos
            
            # Map 2D turtle (x,y) to 3D world (x,0,z) + Global Position
            final_pos = self.pos + glm.vec3(local_p.x, 0.0, local_p.y)
            
            T = glm.translate(final_pos) * base_quat * glm.scale(puff_size)
            
            transforms.append(T)
            colors.append(self.color)
            
        return transforms, colors
