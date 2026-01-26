from pyglm import glm
from framework.shapes.cars.vehicle import BaseVehicle

import random

class PoliceCar(BaseVehicle):
    def create_geometry(self):
        # Color Scheme
        c_bw = glm.vec4(0.1, 0.1, 0.1, 1.0) # Black
        if random.random() > 0.5:
            c_bw = glm.vec4(0.1, 0.1, 0.6, 1.0) # Blue-ish for european police
            
        c_stripe = glm.vec4(1,1,1,1)
        
        self.add_box(c_bw, glm.vec3(2.0, 0.7, 4.6), glm.vec3(0, 0.75, 0), self.body_mat)
        self.add_box(c_stripe, glm.vec3(2.02, 0.7, 0.1), glm.vec3(0, 0.75, 0.5), self.body_mat) 
        
        self.add_trap(c_bw, glm.vec3(1.8, 0.6, 2.2), glm.vec3(0, 1.4, -0.2), 0.6, self.body_mat)
        self.add_trap(glm.vec4(0,0,0,1), glm.vec3(1.82, 0.4, 1.8), glm.vec3(0, 1.4, -0.2), 0.65, self.glass_mat)
        
        # Sirens
        light_color_1 = glm.vec4(1,0,0,1) # Red
        light_color_2 = glm.vec4(0,0,1,1) # Blue
        
        if random.random() > 0.5:
             light_color_1 = glm.vec4(0,0,1,1) # Blue
             light_color_2 = glm.vec4(0,0,1,1) # Blue
             
        self.add_box(light_color_1, glm.vec3(0.8, 0.2, 0.2), glm.vec3(-0.5, 1.8, -0.2), self.glow_mat)
        self.add_box(light_color_2, glm.vec3(0.8, 0.2, 0.2), glm.vec3(0.5, 1.8, -0.2), self.glow_mat)
        
        self.add_wheel(0.4, 0.4, glm.vec3(-1.0, 0.4, 1.5))
        self.add_wheel(0.4, 0.4, glm.vec3(1.0, 0.4, 1.5))
        self.add_wheel(0.4, 0.4, glm.vec3(-1.0, 0.4, -1.5))
        self.add_wheel(0.4, 0.4, glm.vec3(1.0, 0.4, -1.5))
