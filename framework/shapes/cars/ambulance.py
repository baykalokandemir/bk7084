from pyglm import glm
from framework.shapes.cars.vehicle import BaseVehicle

import random

class Ambulance(BaseVehicle):
    def create_geometry(self):
        c_white = glm.vec4(1.0, 1.0, 1.0, 1.0)
        
        amb_len = random.uniform(5.5, 6.5)
        amb_height = random.uniform(1.4, 1.6)
        
        # Base
        self.add_box(c_white, glm.vec3(2.4, 1.0, amb_len), glm.vec3(0, 1.0, 0), self.body_mat)
        # Rear box
        self.add_box(c_white, glm.vec3(2.2, amb_height, amb_len - 2.0), glm.vec3(0, 1.0 + (amb_height/2), -1.0), self.body_mat)
        
        # Red cross (just a box)
        self.add_box(glm.vec4(1,0,0,1), glm.vec3(0.2, 1.0, 2.0), glm.vec3(1.15, 2.0, -1.0), self.body_mat)
        
        # Windows
        self.add_box(glm.vec4(0,0,0,1), glm.vec3(2.25, 0.6, 0.1), glm.vec3(0, 2.0, (amb_len/2) - 0.2), self.glass_mat)
        
        # Lights
        self.add_box(glm.vec4(1,1,0,1), glm.vec3(2.0, 0.2, 0.2), glm.vec3(0, 1.0 + amb_height + 0.1, 0.8), self.glow_mat)

        wheel_z = (amb_len/2) - 1.0
        self.add_wheel(0.5, 0.5, glm.vec3(-1.2, 0.5, wheel_z))
        self.add_wheel(0.5, 0.5, glm.vec3(1.2, 0.5, wheel_z))
        self.add_wheel(0.5, 0.5, glm.vec3(-1.2, 0.5, -wheel_z))
        self.add_wheel(0.5, 0.5, glm.vec3(1.2, 0.5, -wheel_z))
