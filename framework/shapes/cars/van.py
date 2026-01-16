from pyglm import glm
from project.vehicle import BaseVehicle

class Van(BaseVehicle):
    def create_geometry(self):
        c_white = glm.vec4(0.9, 0.9, 0.9, 1.0)
        c_black = glm.vec4(0.0, 0.0, 0.0, 1.0)
        
        # Body
        self.add_box(c_white, glm.vec3(2.0, 1.8, 5.0), glm.vec3(0, 1.3, 0), self.body_mat)
        # Windshield
        self.add_trap(c_black, glm.vec3(1.8, 0.8, 0.5), glm.vec3(0, 1.8, 2.5), 0.8, self.glass_mat)
        
        # Glow
        self.add_box(glm.vec4(1,0.5,0,1), glm.vec3(2.05, 0.1, 5.05), glm.vec3(0, 0.5, 0), self.glow_mat)

        self.add_wheel(0.4, 0.4, glm.vec3(-1.0, 0.4, 1.8))
        self.add_wheel(0.4, 0.4, glm.vec3(1.0, 0.4, 1.8))
        self.add_wheel(0.4, 0.4, glm.vec3(-1.0, 0.4, -1.8))
        self.add_wheel(0.4, 0.4, glm.vec3(1.0, 0.4, -1.8))
