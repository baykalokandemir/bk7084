from pyglm import glm
from project.vehicle import BaseVehicle

class Sedan(BaseVehicle):
    def create_geometry(self):
        c_red = glm.vec4(0.8, 0.1, 0.1, 1.0)
        
        self.add_box(c_red, glm.vec3(1.9, 0.6, 4.5), glm.vec3(0, 0.7, 0), self.body_mat)
        # Smooth cabin
        self.add_trap(c_red, glm.vec3(1.7, 0.6, 2.0), glm.vec3(0, 1.3, -0.2), 0.6, self.body_mat)
        self.add_trap(glm.vec4(0,0,0,1), glm.vec3(1.72, 0.45, 1.8), glm.vec3(0, 1.3, -0.2), 0.65, self.glass_mat)
        
        self.add_box(glm.vec4(0,1,1,1), glm.vec3(1.95, 0.1, 4.55), glm.vec3(0, 0.4, 0), self.glow_mat)
        
        self.add_wheel(0.4, 0.3, glm.vec3(-0.95, 0.4, 1.5))
        self.add_wheel(0.4, 0.3, glm.vec3(0.95, 0.4, 1.5))
        self.add_wheel(0.4, 0.3, glm.vec3(-0.95, 0.4, -1.5))
        self.add_wheel(0.4, 0.3, glm.vec3(0.95, 0.4, -1.5))
