from pyglm import glm
from project.vehicle import BaseVehicle

class Truck(BaseVehicle):
    def create_geometry(self):
        c_grey = glm.vec4(0.5, 0.5, 0.5, 1.0)
        c_red = glm.vec4(1.0, 0.0, 0.0, 1.0)
        c_glass = glm.vec4(0.0, 0.0, 0.0, 1.0)
        
        # Cab
        self.add_box(c_grey, glm.vec3(2.2, 2.0, 1.5), glm.vec3(0, 1.5, 2.5), self.body_mat)
        # Window
        self.add_box(c_glass, glm.vec3(2.0, 0.8, 0.1), glm.vec3(0, 2.0, 3.26), self.glass_mat) 
        
        # Trailer
        self.add_box(c_grey, glm.vec3(2.4, 2.5, 6.0), glm.vec3(0, 1.8, -1.5), self.body_mat)
        
        # Glow
        self.add_box(c_red, glm.vec3(2.25, 0.2, 0.1), glm.vec3(0, 0.6, 3.3), self.glow_mat) # Wider than cab
        
        # Wheels (6 wheels)
        w_y = 0.5
        self.add_wheel(0.5, 0.5, glm.vec3(-1.1, w_y, 2.5))
        self.add_wheel(0.5, 0.5, glm.vec3(1.1, w_y, 2.5))
        
        self.add_wheel(0.5, 0.5, glm.vec3(-1.1, w_y, -2.5))
        self.add_wheel(0.5, 0.5, glm.vec3(1.1, w_y, -2.5))
        self.add_wheel(0.5, 0.5, glm.vec3(-1.1, w_y, -3.8))
        self.add_wheel(0.5, 0.5, glm.vec3(1.1, w_y, -3.8))
