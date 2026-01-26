from pyglm import glm
from framework.shapes.cars.vehicle import BaseVehicle

import random

class Van(BaseVehicle):
    def create_geometry(self):
        c_white = glm.vec4(0.9, 0.9, 0.9, 1.0)
        
        # Parametric
        van_color = random.choice([
            c_white,
            glm.vec4(0.5, 0.0, 0.0, 1.0), # Dark Red
            glm.vec4(0.1, 0.1, 0.4, 1.0), # Navy
            glm.vec4(0.2, 0.2, 0.2, 1.0), # Grey
        ])
        
        length_factor = random.uniform(4.5, 5.5)
        height_factor = random.uniform(1.6, 2.0)
        
        c_black = glm.vec4(0.0, 0.0, 0.0, 1.0)
        
        # Body
        self.add_box(van_color, glm.vec3(2.0, height_factor, length_factor), glm.vec3(0, 1.3, 0), self.body_mat)
        # Windshield
        self.add_trap(c_black, glm.vec3(1.8, 0.8, 0.5), glm.vec3(0, 1.8, (length_factor/2)), 0.8, self.glass_mat)
        
        # Glow
        self.add_box(glm.vec4(1,0.5,0,1), glm.vec3(2.05, 0.1, length_factor + 0.05), glm.vec3(0, 0.5, 0), self.glow_mat)

        wheel_z = (length_factor/2) - 1.0
        self.add_wheel(0.4, 0.4, glm.vec3(-1.0, 0.4, wheel_z))
        self.add_wheel(0.4, 0.4, glm.vec3(1.0, 0.4, wheel_z))
        self.add_wheel(0.4, 0.4, glm.vec3(-1.0, 0.4, -wheel_z))
        self.add_wheel(0.4, 0.4, glm.vec3(1.0, 0.4, -wheel_z))
