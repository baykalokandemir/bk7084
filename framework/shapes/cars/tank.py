from pyglm import glm
from framework.shapes.cars.vehicle import BaseVehicle
from framework.shapes import Cylinder
from framework.objects import MeshObject

class Tank(BaseVehicle):
    def create_geometry(self):
        c_green = glm.vec4(0.2, 0.3, 0.2, 1.0)
        
        # Tracks/Body housing
        self.add_box(c_green, glm.vec3(3.0, 1.2, 5.5), glm.vec3(0, 0.6, 0), self.body_mat)
        # Turret
        self.add_box(c_green, glm.vec3(1.8, 0.8, 2.5), glm.vec3(0, 1.5, 0), self.body_mat)
        # Barrel
        barrel = Cylinder(radius=0.2, height=3.0, segments=16, color=c_green)
        rot = glm.rotate(glm.radians(90), glm.vec3(1, 0, 0)) # Point forward Z?
        t = glm.translate(glm.vec3(0, 1.5, 2.5))
        obj = MeshObject(barrel, self.body_mat, t * rot)
        obj.local_transform = t * rot
        self.parts.append(obj)
        
        # Glow
        self.add_box(glm.vec4(0,1,0,1), glm.vec3(3.15, 0.1, 5.0), glm.vec3(0, 0.2, 0), self.glow_mat)

        # Wheels hidden or many
        for z in [-2.0, -1.0, 0.0, 1.0, 2.0]:
            self.add_wheel(0.4, 0.6, glm.vec3(-1.5, 0.4, z))
            self.add_wheel(0.4, 0.6, glm.vec3(1.5, 0.4, z))
