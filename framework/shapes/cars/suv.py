from pyglm import glm
from framework.shapes.cars.vehicle import BaseVehicle

class SUV(BaseVehicle):
    def create_geometry(self):
        c_black = glm.vec4(0.2, 0.2, 0.2, 1.0)
        
        # Body Blocky
        self.add_box(c_black, glm.vec3(2.2, 0.8, 5.0), glm.vec3(0, 0.9, 0), self.body_mat)
        # Cabin Boxy
        self.add_box(c_black, glm.vec3(2.0, 0.8, 2.5), glm.vec3(0, 1.7, -0.5), self.body_mat)
        # Windows
        self.add_box(glm.vec4(0,0,0,1), glm.vec3(2.05, 0.6, 2.0), glm.vec3(0, 1.7, -0.5), self.glass_mat)
        
        # Glow strip
        self.add_box(glm.vec4(1,0,1,1), glm.vec3(2.3, 0.1, 5.05), glm.vec3(0, 0.5, 0), self.glow_mat)
        
        self.add_wheel(0.5, 0.4, glm.vec3(-1.1, 0.5, 1.8))
        self.add_wheel(0.5, 0.4, glm.vec3(1.1, 0.5, 1.8))
        self.add_wheel(0.5, 0.4, glm.vec3(-1.1, 0.5, -1.8))
        self.add_wheel(0.5, 0.4, glm.vec3(1.1, 0.5, -1.8))
