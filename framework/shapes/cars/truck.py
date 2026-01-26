from pyglm import glm
from framework.shapes.cars.vehicle import BaseVehicle

import random

class Truck(BaseVehicle):
    def create_geometry(self):
        c_grey = glm.vec4(0.5, 0.5, 0.5, 1.0)
        
        # Random parameters
        trailer_len = random.uniform(5.5, 7.5)
        trailer_height = random.uniform(2.5, 3.2)
        cab_color = random.choice([
            glm.vec4(1.0, 0.0, 0.0, 1.0), # Red
            glm.vec4(0.0, 0.0, 1.0, 1.0), # Blue
            glm.vec4(1.0, 1.0, 1.0, 1.0), # White
            glm.vec4(0.1, 0.1, 0.1, 1.0), # Black
        ])
        c_glass = glm.vec4(0.0, 0.0, 0.0, 1.0)
        
        # Cab
        self.add_box(cab_color, glm.vec3(2.2, 2.0, 1.5), glm.vec3(0, 1.5, 2.5), self.body_mat)
        # Window
        self.add_box(c_glass, glm.vec3(2.0, 0.8, 0.1), glm.vec3(0, 2.0, 3.26), self.glass_mat) 
        
        # Trailer
        trailer_color = random.choice([c_grey, glm.vec4(0.9, 0.9, 0.9, 1.0), cab_color])
        self.add_box(trailer_color, glm.vec3(2.4, trailer_height, trailer_len), glm.vec3(0, 1.8, -1.5), self.body_mat)
        
        # Glow
        self.add_box(cab_color, glm.vec3(2.25, 0.2, 0.1), glm.vec3(0, 0.6, 3.3), self.glow_mat) 
        
        # Wheels (6 wheels)
        w_y = 0.5
        self.add_wheel(0.5, 0.5, glm.vec3(-1.1, w_y, 2.5))
        self.add_wheel(0.5, 0.5, glm.vec3(1.1, w_y, 2.5))
        
        # Trailer wheels
        self.add_wheel(0.5, 0.5, glm.vec3(-1.1, w_y, -2.5))
        self.add_wheel(0.5, 0.5, glm.vec3(1.1, w_y, -2.5))
        self.add_wheel(0.5, 0.5, glm.vec3(-1.1, w_y, -3.8))
        self.add_wheel(0.5, 0.5, glm.vec3(1.1, w_y, -3.8))
