"""

  /$$$$$$$  /$$   /$$ /$$$$$$$$ /$$$$$$   /$$$$$$  /$$   /$$
 | $$__  $$| $$  /$$/|_____ $$//$$$_  $$ /$$__  $$| $$  | $$
 | $$  \\ $$| $$ /$$/      /$$/| $$$$\\ $$| $$  \\ $$| $$  | $$
 | $$$$$$$ | $$$$$/      /$$/ | $$ $$ $$|  $$$$$$/| $$$$$$$$
 | $$__  $$| $$  $$     /$$/  | $$\\ $$$$ >$$__  $$|_____  $$
 | $$  \\ $$| $$\\  $$   /$$/   | $$ \\ $$$| $$  \\ $$      | $$
 | $$$$$$$/| $$ \\  $$ /$$/    |  $$$$$$/|  $$$$$$/      | $$
 |_______/ |__/  \\__/|__/      \\______/  \\______/       |__/

Welcome to the lab exercises of BK7084!
In this assignment, we will introduce you to the basics of transformations:
0. Translation, rotation and scale
1. Concatenating transformations
2. Hierarchical transformations
3. Creating a scene (getting creative!)

This assignment is divided into 2 tasks:
1. Basic transformations + animation (single cube)
2. Windmill (hierarchical transforms)

For each task, you will be asked to complete certain tasks.
The tasks are marked with a TODO: comment. (edit the lines labeled # adjust this to ...)
If you're not sure what to do, look for these comments.
For now, scroll down to TASK 1.
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.camera import *
from framework.renderer import *
from framework.light import *
from framework.shapes import Cube, Triangle, Quad
from framework.objects import MeshObject
from framework.materials import Material
from pyglm import glm
import numpy as np

# ----------------------------
# Windmill (hierarchical transforms)
# ----------------------------
class Windmill:
    # TASK 2: create a windmill

    def transform(self):
        # base (scaled up in Y)
        # TODO[2.1]: Set self.base.transform to place the base at y = base_height/2
        #            and scale it up along Y by self.base_height.
        self.base.transform = self.base_translation * glm.scale(glm.vec3(1, self.base_height, 1)) # adjust this to scale the base up along Y


        # top (rotates around Y on top of base)
        # TODO[2.2]: Set self.top.transform so the top sits on the base and
        #            rotates around the global Y-axis by self.top_rotation (degrees).
        self.top.transform = self.base_translation * self.top_translation * glm.rotate(glm.radians(self.top_rotation), glm.vec3(0, 1, 0)) # adjust this to rotate the top around the global Y-axis

        
        
        # blades (rotate around Z, positioned in front of the top)
        # TODO[2.3]: Set each blade's transform so blades rotate around Z by self.blades_rotation
        #            and are evenly spaced by 120° around the hub, positioned in front of the top,
        #            and scaled to self.blade_size.
        spin = glm.rotate(glm.radians(self.blades_rotation), glm.vec3(0, 0, 1))
        self.blades[0].transform = self.top.transform * glm.rotate(glm.radians(0), glm.vec3(0, 0, 1)) * spin * self.blade_translation * self.blade_scale # adjust this to rotate the blades around Z
        self.blades[1].transform = self.top.transform * glm.rotate(glm.radians(120), glm.vec3(0, 0, 1)) * spin * self.blade_translation * self.blade_scale # adjust this to rotate the blades around Z
        self.blades[2].transform = self.top.transform * glm.rotate(glm.radians(240), glm.vec3(0, 0, 1)) * spin * self.blade_translation * self.blade_scale # adjust this to rotate the blades around Z
        # add other two blades
        # self.blades[1].transform = ... * ... * ... * ... * ...
        # self.blades[2].transform = ... * ... * ... * ... * ...

    def animate(self):
        # increase rotations each frame (degrees)
        rot = 1
        self.blades_rotation = (self.blades_rotation + rot) % 360.0
        self.top_rotation = (self.top_rotation + rot * 0.5) % 360.0
        self.transform()


    def __init__(self, renderer):
        # --- Base (tower) ---
        # [2.0.a]: Choose a reasonable base height (e.g., 5) and color.
        self.base_height = 5
        self.base = MeshObject(Cube(side_length=1, color=glm.vec4(0.7, 0.9, 0.7, 0.8)), Material())
        # [2.0.b]: Set a translation that lifts the base so it sits on the ground.
        self.base_translation = glm.translate(glm.vec3(0, self.base_height / 2, -2)) # the cube is originally centered at the origin

        # --- Top ---
        # [2.0.c]: Initialize top size and rotation accumulator.
        self.top_rotation = 0
        self.top_size = 2
        self.top = MeshObject(Cube(side_length=self.top_size, color=glm.vec4(0.8, 0.3, 0.3, 1.0)), Material())
        # [2.0.d]: Set the relative translation that places the top on the base.
        self.top_translation = glm.translate(glm.vec3(0, self.base_height / 2 + self.top_size / 2, 0))

        # --- Blades ---
        # [2.0.e]: Initialize blade rotation and size accumulators.
        self.blades = []
        self.blades_rotation = 0
        # [2.0.f]: Decide blade dimensions (x,y,z) and precompute scale matrix.
        self.blade_size = glm.vec3(1, 3, 0.1)
        self.blade_scale = glm.scale(self.blade_size)
        # [2.0.g]: Compute initial translation that positions blades in front of the top.
        self.blade_translation = glm.translate(glm.vec3(0, self.blade_size.y / 2, self.top_size / 2 + self.blade_size.z / 2))

        for i in range(3):
            # [2.0.h]: You may change blade color/mesh if desired.
            blade_mesh = Cube(side_length=1, color=glm.vec4(0.2, 0.3, 0.8, 1.0))
            blade = MeshObject(blade_mesh, Material(), )
            self.blades.append(blade)

        # Create the windmill by adding all components (base, top, blades) to the renderer.
        self.transform()

        # Register objects with renderer
        renderer.addObject(self.base)
        renderer.addObject(self.top)
        for blade in self.blades:
            renderer.addObject(blade)


def main():
    width, height = 600, 600

    # Window
    glwindow = OpenGLWindow(width, height)

    # Camera
    camera = Flycamera(width, height, 70.0, 0.1, 100.0)
    camera.draw_camera = False
    camera.position += glm.vec3(0.0, 1.0, 0.0)
    camera.updateView()

    # Renderer
    glrenderer = GLRenderer(glwindow, camera)

    # Lights
    glrenderer.addLight(PointLight(glm.vec4(10.0, 10.0, 0.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))
    glrenderer.addLight(PointLight(glm.vec4(0.0, 10.0, 10.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))

    # Floor
    floor_shape = Quad(width=100, height=100)
    floor_mat = Material(fragment_shader="grid.frag")
    floor_obj = MeshObject(floor_shape, floor_mat)
    floor_obj.transform = glm.rotate(glm.radians(-90), glm.vec3(1, 0, 0))
    glrenderer.addObject(floor_obj)

    # ----------------------------
    # Task 1: Basic transformations + animation (single cube)
    # ----------------------------

    # TODO[1.0]: Create a Cube mesh with a custom color and side_length (e.g., 2.0).
    # Hint: use the Cube class from the shapes module
    cube_mesh = Cube(color=glm.vec4(1.0,1.0,1.0,1.0), side_length=1.0) # adjust this with a custom color and side_length


    # [1.1]: Create a Material object (it defines the way the object looks; think colors and how it interacts with lights).
    cube_mat = Material()  # left it blank as default material


    # TODO[1.2]: Create an initial transform that places the cube at (0, 1, -2).
    # Hint: use the glm.translate function
    cube_transform = glm.translate(glm.vec3(0, 1, -2)) # adjust this to place the cube at (0, 1, -2)


    # [1.3]: Create the MeshObject for the cube and add it to the renderer.
    cube_obj = MeshObject(mesh=cube_mesh, material=cube_mat, transform=cube_transform)
    glrenderer.addObject(cube_obj)


    # ----------------------------
    # Task 2: Windmill (hierarchical transforms)
    # ----------------------------
    windmill = Windmill(glrenderer)

    # RENDER LOOP
    while not glfw.window_should_close(glwindow.window):
        # TODO[1.4]: Animate the cube with a slow spin each frame. (e.g., +1/50 deg)
        rot_deg = 0.3   # adjust this value to change the speed of the cube's rotation
        cube_obj.transform = cube_obj.transform * glm.rotate(glm.radians(rot_deg), glm.vec3(1, 0, 0)) # adjust this to rotate the cube along the x and y axes

        # [2.5]: Call windmill.animate() to update rotations every frame.
        windmill.animate()

        glrenderer.render()

    glrenderer.delete()
    glwindow.delete()
    return 0


if __name__ == "__main__":
    main()
