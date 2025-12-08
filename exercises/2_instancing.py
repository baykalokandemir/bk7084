"""

  /$$$$$$$  /$$   /$$ /$$$$$$$$ /$$$$$$   /$$$$$$  /$$   /$$
 | $$__  $$| $$  /$$/|_____ $$//$$$_  $$ /$$__  $$| $$  | $$
 | $$  \\ $$| $$ /$$/      /$$/| $$$$\\ $$| $$  \\ $$| $$  | $$
 | $$$$$$$ | $$$$$/      /$$/ | $$ $$ $$|  $$$$$$/| $$$$$$$$
 | $$__  $$| $$  $$     /$$/  | $$\\ $$$$ >$$__  $$|_____  $$
 | $$  \\ $$| $$\\  $$   /$$/   | $$ \\ $$$| $$  \\ $$      | $$
 | $$$$$$$/| $$ \\  $$ /$$/    |  $$$$$$/|  $$$$$$/      | $$
 |_______/ |__/  \\__/|__/      \\______/  \\______/       |__/

In this assignment, we will introduce you to the basics of Instancing:

Overview
- Build your own Minecraft-like scene using cubes (vary sizes, colors, and placements).
- Use GPU instancing when rendering large numbers of cubes to reduce draw calls.
- Add simple animation (e.g., moving objects, slow global rotation, changing colors).
- The tasks are marked with a TODO: comment. (edit the lines labeled # adjust this to ...)

What this script shows
- Generating per-instance transforms (random positions) and colors.
- Updating instance data on the fly (slow global Y rotation, periodic recolor).
- Performance benefits of instancing for large object counts.

This assignment is divided into 3 tasks:
1. Minecraft-style scene (Instancing)
2. Minecraft-style scene (Animations)
3. Minecraft-style scene (Performance)

Controls
- Camera: mouse + WASDEC to move (Flycamera).
- Scene: tiled floor + two point lights for shading.

"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.camera import *
from framework.renderer import *
from framework.light import *
from framework.shapes import Cube, Quad
from framework.objects import MeshObject, InstancedMeshObject
from framework.materials import Material
from pyglm import glm
import random
import numpy as np

# ----------------------------
# MinecraftScene (Instancing)
# ----------------------------
class MinecraftScene:

    def __init__(self, renderer, n=5000, use_instancing=True):
        self.renderer = renderer
        self.n = n
        self.use_instancing = use_instancing
        self.frames = 0

        # create many different transformations (matrices) and colors (vec4) for the instances
        self.transforms = []
        self.colors = []

        # TODO[1.0]: Use random.randint / random.random to position cubes in space
        # Example: create random positions and colors for the cubes
        for _ in range(n):
            random_position = glm.vec3(
                random.randint(-50, 50),  # adjust this to the range of the positions on the x axis
                random.randint(1, 5),    # adjust this to the range of the positions on the y axis
                random.randint(-50, 50)   # adjust this to the range of the positions on the z axis
            )
            self.transforms.append(glm.translate(random_position))

            # TODO[1.1]: Use random.randint / random.random to assign random RGB colors (alpha = 1.0)
            self.colors.append(glm.vec4(random.random(), random.random(), random.random(), 1.0))

        # [1.2]: Choose between instanced or non-instanced rendering
        if use_instancing:
            # one base cube, wrapped in InstancedMeshObject
            base_cube = Cube(color=glm.vec4(1.0))
            cube_mat = Material()

            # Create a base Cube mesh and wrap it in InstancedMeshObject
            self.instance_cube = InstancedMeshObject(base_cube, cube_mat,
                                                     transforms=self.transforms,
                                                     colors=self.colors)
            # Add it to renderer
            renderer.addObject(self.instance_cube)
        else:
            # Create and add n individual MeshObject cubes (inefficient)
            cube_mat = Material()
            for i in range(n):
                cube = MeshObject(Cube(color=self.colors[i]), cube_mat)
                cube.transform = self.transforms[i]
                renderer.addObject(cube)


    def animate(self):
        # Update animations only if instancing is enabled
        if not self.use_instancing:
            return

        self.frames += 1

         # TODO[2.0]: Every ~100 frames, randomize colors again and update them on GPU
         # Hint: use self.frames % 100 == 0 to check if it's time to update
        if self.frames % 100 == 0:
            for i in range(self.n):
                self.colors[i] = glm.vec4(random.random(), random.random(), random.random(), 1.0) # adjust this to randomize the colors
            self.instance_cube.update_colors(self.colors)

        # TODO[2.1]: Slowly rotate all cubes around Y-axis
        for i in range(self.n):
            self.transforms[i] = self.transforms[i] * glm.rotate(
                glm.radians(0.3), glm.vec3(0, 1, 0) # adjust this to rotate the cubes around the Y-axis
            )
        self.instance_cube.update_transforms(self.transforms)


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
    glrenderer.addLight(PointLight(glm.vec4(10.0, 10.0, 0.0, 1.0),
                                   glm.vec4(0.5, 0.5, 0.5, 1.0)))
    glrenderer.addLight(PointLight(glm.vec4(0.0, 10.0, 10.0, 1.0),
                                   glm.vec4(0.5, 0.5, 0.5, 1.0)))

    # Floor
    floor_shape = Quad(width=100, height=100)
    floor_mat = Material(fragment_shader="grid.frag")
    floor_obj = MeshObject(floor_shape, floor_mat)
    floor_obj.transform = glm.rotate(glm.radians(-90), glm.vec3(1, 0, 0))
    glrenderer.addObject(floor_obj)

    # ----------------------------
    # Task: Minecraft-style scene
    # ----------------------------
    # TODO[3.0]: Create your MinecraftScene instance
    minecraft = MinecraftScene(glrenderer, n=1000, use_instancing=True) # adjust n and toggle use_instancing to compare performance and other differences.

    # Render loop
    while not glfw.window_should_close(glwindow.window):
        # Call minecraft.animate() inside the loop to apply color changes and rotations
        minecraft.animate()
        glrenderer.render()

    glrenderer.delete()
    glwindow.delete()
    return 0


if __name__ == "__main__":
    main()
