from pyglm import glm
from framework.shapes.cars.vehicle import BaseVehicle

import random

class Pickup(BaseVehicle):
    def create_geometry(self):
        pickup_color = random.choice([
            glm.vec4(0.8, 0.4, 0.0, 1.0), # Orange
            glm.vec4(0.1, 0.3, 0.1, 1.0), # Dark Green
            glm.vec4(0.5, 0.1, 0.1, 1.0), # Dark Red
            glm.vec4(0.3, 0.3, 0.3, 1.0), # Grey
        ])
        
        # Parametric
        bed_length = random.uniform(1.8, 2.5)
        cab_pos_z = 1.0
        
        # Lower Body
        total_len = 3.2 + bed_length
        self.add_box(pickup_color, glm.vec3(2.2, 0.8, total_len), glm.vec3(0, 0.9, 0), self.body_mat)
        
        # Cab
        self.add_box(pickup_color, glm.vec3(2.0, 0.9, 1.8), glm.vec3(0, 1.7, cab_pos_z), self.body_mat)
        
        # Bed walls
        bed_z = cab_pos_z - (1.8/2) - (bed_length/2) - 0.1
        self.add_box(pickup_color, glm.vec3(2.0, 0.5, bed_length), glm.vec3(0, 1.5, bed_z), self.body_mat)
        
        # Windows
        self.add_box(glm.vec4(0,0,0,1), glm.vec3(2.05, 0.6, 1.5), glm.vec3(0, 1.7, cab_pos_z), self.glass_mat)
        
        # Glow
        self.add_box(glm.vec4(1,0.5,0,1), glm.vec3(2.25, 0.2, 0.1), glm.vec3(0, 0.5, total_len/2 + 0.05), self.glow_mat)
        
        self.add_wheel(0.5, 0.4, glm.vec3(-1.1, 0.5, 1.8))
        self.add_wheel(0.5, 0.4, glm.vec3(1.1, 0.5, 1.8))
        self.add_wheel(0.5, 0.4, glm.vec3(-1.1, 0.5, -1.8))
        self.add_wheel(0.5, 0.4, glm.vec3(1.1, 0.5, -1.8))
