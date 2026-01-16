from pyglm import glm
from project.vehicle import BaseVehicle

class RaceCar(BaseVehicle):
    def create_geometry(self):
        # Silver Body
        c_silver = glm.vec4(0.8, 0.8, 0.9, 1.0)
        c_yellow = glm.vec4(1.0, 1.0, 0.0, 1.0)
        c_cyan = glm.vec4(0.0, 1.0, 1.0, 1.0)
        c_black = glm.vec4(0.1, 0.1, 0.1, 1.0)
        
        # Base
        self.add_box(c_silver, glm.vec3(2.0, 0.5, 4.8), glm.vec3(0, 0.6, 0), self.body_mat)
        # Cabin Wedge
        self.add_trap(c_silver, glm.vec3(1.6, 0.7, 2.5), glm.vec3(0, 1.2, -0.2), 0.5, self.body_mat)
        # Window
        self.add_trap(c_black, glm.vec3(1.65, 0.5, 2.0), glm.vec3(0, 1.25, -0.2), 0.5, self.glass_mat)
        
        # Skirts
        self.add_box(c_silver, glm.vec3(0.4, 0.4, 3.0), glm.vec3(-1.1, 0.6, 0), self.body_mat)
        self.add_box(c_silver, glm.vec3(0.4, 0.4, 3.0), glm.vec3(1.1, 0.6, 0), self.body_mat)
        
        # Glow
        self.add_box(c_yellow, glm.vec3(2.05, 0.1, 0.2), glm.vec3(0, 0.6, 2.45), self.glow_mat) # Front - Made wider
        self.add_box(c_cyan, glm.vec3(0.1, 0.1, 2.5), glm.vec3(-1.35, 0.4, 0), self.glow_mat) # Side L - Moved out
        self.add_box(c_cyan, glm.vec3(0.1, 0.1, 2.5), glm.vec3(1.35, 0.4, 0), self.glow_mat) # Side R - Moved out
        
        # Wheels
        self.add_wheel(0.45, 0.4, glm.vec3(-1.0, 0.45, 1.5))
        self.add_wheel(0.45, 0.4, glm.vec3(1.0, 0.45, 1.5))
        self.add_wheel(0.5, 0.5, glm.vec3(-1.0, 0.5, -1.5))
        self.add_wheel(0.5, 0.5, glm.vec3(1.0, 0.5, -1.5))
