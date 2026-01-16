from pyglm import glm
from framework.shapes.cars.vehicle import BaseVehicle

class Pickup(BaseVehicle):
    def create_geometry(self):
        c_orange = glm.vec4(0.8, 0.4, 0.0, 1.0)
        
        # Lower Body
        self.add_box(c_orange, glm.vec3(2.2, 0.8, 5.2), glm.vec3(0, 0.9, 0), self.body_mat)
        # Cab
        self.add_box(c_orange, glm.vec3(2.0, 0.9, 1.8), glm.vec3(0, 1.7, 1.0), self.body_mat)
        # Bed walls
        self.add_box(c_orange, glm.vec3(2.0, 0.5, 2.0), glm.vec3(0, 1.5, -1.5), self.body_mat)
        
        # Windows
        self.add_box(glm.vec4(0,0,0,1), glm.vec3(2.05, 0.6, 1.5), glm.vec3(0, 1.7, 1.0), self.glass_mat)
        
        # Glow
        self.add_box(glm.vec4(1,0.5,0,1), glm.vec3(2.25, 0.2, 0.1), glm.vec3(0, 0.5, 2.62), self.glow_mat)
        
        self.add_wheel(0.5, 0.4, glm.vec3(-1.1, 0.5, 1.8))
        self.add_wheel(0.5, 0.4, glm.vec3(1.1, 0.5, 1.8))
        self.add_wheel(0.5, 0.4, glm.vec3(-1.1, 0.5, -1.8))
        self.add_wheel(0.5, 0.4, glm.vec3(1.1, 0.5, -1.8))
