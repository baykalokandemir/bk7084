from pyglm import glm
from project.vehicle import BaseVehicle

class Bus(BaseVehicle):
    def create_geometry(self):
        c_blue = glm.vec4(0.2, 0.2, 0.8, 1.0)
        c_window = glm.vec4(0.1, 0.1, 0.1, 1.0)
        
        # Body
        self.add_box(c_blue, glm.vec3(2.4, 2.2, 8.0), glm.vec3(0, 1.6, 0), self.body_mat)
        
        # Windows strip
        self.add_box(c_window, glm.vec3(2.45, 0.8, 7.0), glm.vec3(0, 1.8, 0), self.glass_mat)
        
        # Glow
        self.add_box(glm.vec4(0,1,0,1), glm.vec3(2.45, 0.1, 8.05), glm.vec3(0, 0.6, 0), self.glow_mat)
        
        # Wheels
        self.add_wheel(0.5, 0.5, glm.vec3(-1.2, 0.5, 2.5))
        self.add_wheel(0.5, 0.5, glm.vec3(1.2, 0.5, 2.5))
        self.add_wheel(0.5, 0.5, glm.vec3(-1.2, 0.5, -2.5))
        self.add_wheel(0.5, 0.5, glm.vec3(1.2, 0.5, -2.5))
