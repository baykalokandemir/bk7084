from pyglm import glm
from project.vehicle import BaseVehicle

class PoliceCar(BaseVehicle):
    def create_geometry(self):
        c_bw = glm.vec4(0.1, 0.1, 0.1, 1.0) # Black
        
        self.add_box(c_bw, glm.vec3(2.0, 0.7, 4.6), glm.vec3(0, 0.75, 0), self.body_mat)
        self.add_box(glm.vec4(1,1,1,1), glm.vec3(2.02, 0.7, 0.1), glm.vec3(0, 0.75, 0.5), self.body_mat) # Stripe? Nah just simple block
        
        self.add_trap(c_bw, glm.vec3(1.8, 0.6, 2.2), glm.vec3(0, 1.4, -0.2), 0.6, self.body_mat)
        self.add_trap(glm.vec4(0,0,0,1), glm.vec3(1.82, 0.4, 1.8), glm.vec3(0, 1.4, -0.2), 0.65, self.glass_mat)
        
        # Sirens
        self.add_box(glm.vec4(1,0,0,1), glm.vec3(0.8, 0.2, 0.2), glm.vec3(-0.5, 1.8, -0.2), self.glow_mat)
        self.add_box(glm.vec4(0,0,1,1), glm.vec3(0.8, 0.2, 0.2), glm.vec3(0.5, 1.8, -0.2), self.glow_mat)
        
        self.add_wheel(0.4, 0.4, glm.vec3(-1.0, 0.4, 1.5))
        self.add_wheel(0.4, 0.4, glm.vec3(1.0, 0.4, 1.5))
        self.add_wheel(0.4, 0.4, glm.vec3(-1.0, 0.4, -1.5))
        self.add_wheel(0.4, 0.4, glm.vec3(1.0, 0.4, -1.5))
