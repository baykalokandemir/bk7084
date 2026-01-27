from pyglm import glm
from framework.shapes.cars.vehicle import BaseVehicle

import random

class Sedan(BaseVehicle):
    def create_geometry(self):
        sedan_color = random.choice([
            glm.vec4(0.8, 0.1, 0.1, 1.0), # Red
            glm.vec4(0.1, 0.1, 0.8, 1.0), # Blue
            glm.vec4(0.8, 0.8, 0.8, 1.0), # Silver
            glm.vec4(0.1, 0.1, 0.1, 1.0), # Black
            glm.vec4(0.9, 0.9, 0.9, 1.0), # White
        ])
        
        # Dimensions
        len_f = random.uniform(4.2, 4.8)
        width_f = random.uniform(1.8, 2.0)
        
        self.add_box(sedan_color, glm.vec3(width_f, 0.6, len_f), glm.vec3(0, 0.7, 0), self.body_mat)
        # Smooth cabin
        cabin_len = len_f * 0.5
        self.add_trap(sedan_color, glm.vec3(width_f - 0.2, 0.6, cabin_len), glm.vec3(0, 1.3, -0.2), 0.6, self.body_mat)
        self.add_trap(glm.vec4(0,0,0,1), glm.vec3(width_f - 0.18, 0.45, cabin_len - 0.2), glm.vec3(0, 1.3, -0.2), 0.65, self.glass_mat)
        
        self.add_box(glm.vec4(0,1,1,1), glm.vec3(width_f + 0.05, 0.1, len_f + 0.05), glm.vec3(0, 0.4, 0), self.glow_mat)
        
        wheel_x = (width_f / 2)
        wheel_z = (len_f / 2) - 0.8
        
        self.add_wheel(0.4, 0.3, glm.vec3(-wheel_x, 0.4, wheel_z))
        self.add_wheel(0.4, 0.3, glm.vec3(wheel_x, 0.4, wheel_z))
        self.add_wheel(0.4, 0.3, glm.vec3(-wheel_x, 0.4, -wheel_z))
        self.add_wheel(0.4, 0.3, glm.vec3(wheel_x, 0.4, -wheel_z))
