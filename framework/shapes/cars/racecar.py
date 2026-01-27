from pyglm import glm
from framework.shapes.cars.vehicle import BaseVehicle

import random

class RaceCar(BaseVehicle):
    def create_geometry(self):
        # Randomize Colors
        base_colors = [
            glm.vec4(0.8, 0.8, 0.9, 1.0), # Silver
            glm.vec4(1.0, 0.0, 0.0, 1.0), # Red
            glm.vec4(0.0, 0.0, 1.0, 1.0), # Blue
            glm.vec4(0.1, 0.1, 0.1, 1.0), # Black
            glm.vec4(1.0, 0.5, 0.0, 1.0), # Orange
        ]
        c_body = random.choice(base_colors)
        c_yellow = glm.vec4(1.0, 1.0, 0.0, 1.0)
        c_cyan = glm.vec4(0.0, 1.0, 1.0, 1.0)
        c_black = glm.vec4(0.1, 0.1, 0.1, 1.0)
        
        # Randomize Size
        len_factor = random.uniform(0.9, 1.1)
        width_factor = random.uniform(0.9, 1.1)
        
        # Base
        base_len = 4.8 * len_factor
        self.add_box(c_body, glm.vec3(2.0 * width_factor, 0.5, base_len), glm.vec3(0, 0.6, 0), self.body_mat)
        
        # Cabin Wedge
        cabin_taper = random.uniform(0.4, 0.6)
        self.add_trap(c_body, glm.vec3(1.6 * width_factor, 0.7, 2.5), glm.vec3(0, 1.2, -0.2), cabin_taper, self.body_mat)
        # Window
        self.add_trap(c_black, glm.vec3(1.65 * width_factor, 0.5, 2.0), glm.vec3(0, 1.25, -0.2), cabin_taper, self.glass_mat)
        
        # Skirts
        skirt_x = 1.1 * width_factor
        self.add_box(c_body, glm.vec3(0.4, 0.4, 3.0), glm.vec3(-skirt_x, 0.6, 0), self.body_mat)
        self.add_box(c_body, glm.vec3(0.4, 0.4, 3.0), glm.vec3(skirt_x, 0.6, 0), self.body_mat)
        
        # Glow
        self.add_box(c_yellow, glm.vec3(2.05 * width_factor, 0.1, 0.2), glm.vec3(0, 0.6, (base_len/2) + 0.05), self.glow_mat) 
        
        # Rear Wing (Randomized)
        if random.random() > 0.3:
            wing_height = random.uniform(1.5, 2.0)
            self.add_box(c_body, glm.vec3(2.2 * width_factor, 0.1, 0.8), glm.vec3(0, wing_height, -2.0), self.body_mat)
            self.add_box(c_black, glm.vec3(0.1, wing_height-0.6, 0.4), glm.vec3(-0.8, (wing_height+0.6)/2, -2.0), self.body_mat)
            self.add_box(c_black, glm.vec3(0.1, wing_height-0.6, 0.4), glm.vec3(0.8, (wing_height+0.6)/2, -2.0), self.body_mat)

        # Wheels
        wheel_x = 1.0 * width_factor
        self.add_wheel(0.45, 0.4, glm.vec3(-wheel_x, 0.45, 1.5))
        self.add_wheel(0.45, 0.4, glm.vec3(wheel_x, 0.45, 1.5))
        self.add_wheel(0.5, 0.5, glm.vec3(-wheel_x, 0.5, -1.5))
        self.add_wheel(0.5, 0.5, glm.vec3(wheel_x, 0.5, -1.5))
