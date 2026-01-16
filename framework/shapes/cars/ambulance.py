from pyglm import glm
from framework.shapes.cars.vehicle import BaseVehicle

class Ambulance(BaseVehicle):
    def create_geometry(self):
        c_white = glm.vec4(1.0, 1.0, 1.0, 1.0)
        
        self.add_box(c_white, glm.vec3(2.4, 1.0, 6.0), glm.vec3(0, 1.0, 0), self.body_mat)
        self.add_box(c_white, glm.vec3(2.2, 1.5, 4.0), glm.vec3(0, 2.0, -1.0), self.body_mat)
        
        # Red cross (just a box)
        self.add_box(glm.vec4(1,0,0,1), glm.vec3(0.2, 1.0, 2.0), glm.vec3(1.15, 2.0, -1.0), self.body_mat)
        
        # Windows
        self.add_box(glm.vec4(0,0,0,1), glm.vec3(2.25, 0.6, 0.1), glm.vec3(0, 2.0, 2.8), self.glass_mat)
        
        # Lights
        self.add_box(glm.vec4(1,1,0,1), glm.vec3(2.0, 0.2, 0.2), glm.vec3(0, 2.8, 0.8), self.glow_mat)

        self.add_wheel(0.5, 0.5, glm.vec3(-1.2, 0.5, 2.0))
        self.add_wheel(0.5, 0.5, glm.vec3(1.2, 0.5, 2.0))
        self.add_wheel(0.5, 0.5, glm.vec3(-1.2, 0.5, -2.0))
        self.add_wheel(0.5, 0.5, glm.vec3(1.2, 0.5, -2.0))
