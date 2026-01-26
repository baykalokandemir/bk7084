from pyglm import glm
from framework.shapes.cars.vehicle import BaseVehicle

import random

class SUV(BaseVehicle):
    def create_geometry(self):
        suv_color = random.choice([
            glm.vec4(0.2, 0.2, 0.2, 1.0), # Black
            glm.vec4(0.8, 0.8, 0.8, 1.0), # Silver
            glm.vec4(0.1, 0.1, 0.4, 1.0), # Navy
            glm.vec4(0.4, 0.1, 0.1, 1.0), # Maroon
        ])
        
        # Random dimensions
        width_f = random.uniform(0.95, 1.1)
        height_f = random.uniform(0.95, 1.1)
        
        body_width = 2.2 * width_f
        
        # Body Blocky
        self.add_box(suv_color, glm.vec3(body_width, 0.8 * height_f, 5.0), glm.vec3(0, 0.9 * height_f, 0), self.body_mat)
        # Cabin Boxy
        self.add_box(suv_color, glm.vec3(body_width - 0.2, 0.8 * height_f, 2.5), glm.vec3(0, 1.7 * height_f, -0.5), self.body_mat)
        # Windows
        self.add_box(glm.vec4(0,0,0,1), glm.vec3(body_width - 0.15, 0.6 * height_f, 2.0), glm.vec3(0, 1.7 * height_f, -0.5), self.glass_mat)
        
        # Glow strip
        self.add_box(glm.vec4(1,0,1,1), glm.vec3(body_width + 0.1, 0.1, 5.05), glm.vec3(0, 0.5, 0), self.glow_mat)
        
        wheel_x = (body_width / 2)
        self.add_wheel(0.5, 0.4, glm.vec3(-wheel_x, 0.5, 1.8))
        self.add_wheel(0.5, 0.4, glm.vec3(wheel_x, 0.5, 1.8))
        self.add_wheel(0.5, 0.4, glm.vec3(-wheel_x, 0.5, -1.8))
        self.add_wheel(0.5, 0.4, glm.vec3(wheel_x, 0.5, -1.8))
