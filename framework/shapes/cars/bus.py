from pyglm import glm
from framework.shapes.cars.vehicle import BaseVehicle

import random

class Bus(BaseVehicle):
    def create_geometry(self):
        # Random parameters
        bus_len = random.uniform(7.5, 9.0)
        bus_color = random.choice([
            glm.vec4(0.2, 0.2, 0.8, 1.0), # Blue
            glm.vec4(0.8, 0.2, 0.2, 1.0), # Red
            glm.vec4(0.2, 0.8, 0.2, 1.0), # Green
            glm.vec4(0.9, 0.9, 0.1, 1.0), # Yellow
            glm.vec4(0.9, 0.9, 0.9, 1.0), # White
        ])
        
        c_window = glm.vec4(0.1, 0.1, 0.1, 1.0)
        
        # Body
        self.add_box(bus_color, glm.vec3(2.4, 2.2, bus_len), glm.vec3(0, 1.6, 0), self.body_mat)
        
        # Windows strip
        self.add_box(c_window, glm.vec3(2.45, 0.8, bus_len - 1.0), glm.vec3(0, 1.8, 0), self.glass_mat)
        
        # Glow
        self.add_box(glm.vec4(0,1,0,1), glm.vec3(2.45, 0.1, bus_len + 0.05), glm.vec3(0, 0.6, 0), self.glow_mat)
        
        # Wheels
        wheel_z = (bus_len/2) - 1.5
        self.add_wheel(0.5, 0.5, glm.vec3(-1.2, 0.5, wheel_z))
        self.add_wheel(0.5, 0.5, glm.vec3(1.2, 0.5, wheel_z))
        self.add_wheel(0.5, 0.5, glm.vec3(-1.2, 0.5, -wheel_z))
        self.add_wheel(0.5, 0.5, glm.vec3(1.2, 0.5, -wheel_z))
