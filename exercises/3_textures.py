"""

  /$$$$$$$  /$$   /$$ /$$$$$$$$ /$$$$$$   /$$$$$$  /$$   /$$
 | $$__  $$| $$  /$$/|_____ $$//$$$_  $$ /$$__  $$| $$  | $$
 | $$  \\ $$| $$ /$$/      /$$/| $$$$\\ $$| $$  \\ $$| $$  | $$
 | $$$$$$$ | $$$$$/      /$$/ | $$ $$ $$|  $$$$$$/| $$$$$$$$
 | $$__  $$| $$  $$     /$$/  | $$\\ $$$$ >$$__  $$|_____  $$
 | $$  \\ $$| $$\\  $$   /$$/   | $$ \\ $$$| $$  \\ $$      | $$
 | $$$$$$$/| $$ \\  $$ /$$/    |  $$$$$$/|  $$$$$$/      | $$
 |_______/ |__/  \\__/|__/      \\______/  \\______/       |__/

This assignment demonstrates how to give basic textures to shapes:
Swap textures by editing the file paths in the script: stone_texture_path & brick_texture_path

Change texture density (bigger value → smaller, denser tiles)
- Cube: set texture_scale_cube
- Roof: set texture_scale_roof

"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.camera import Flycamera
from framework.window import *
from framework.renderer import *
from framework.light import *
from framework.shapes import Cube, Cone, Quad
from framework.objects import MeshObject
from framework.materials import Texture, Material
from pyglm import glm
import numpy as np

import os
BASE_DIR = os.path.dirname(os.path.abspath(__file__))


# [1.0]: Define the texture paths relative to this file.
# We can use the variable "stone_texture_path" later to refer to the right texture.
# For instance, if this file is located at      : "exercises/3_textures.py",
# then we expect our texture to be located at   : "exercises/assets/stone_bricks_col.jpg"
stone_texture_path = os.path.join(BASE_DIR, "assets", "stone_bricks_col.jpg")
brick_texture_path = os.path.join(BASE_DIR, "assets", "brickwall.png")


def _get_vp_from_camera(cam):
    try:
        return cam.projection * cam.view
    except Exception:
        try:
            return cam.getProjection() * cam.getView()
        except Exception:
            return glm.mat4(1.0)

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
    glrenderer.addLight(PointLight(glm.vec4(12.0, 10.0, 0.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))
    glrenderer.addLight(PointLight(glm.vec4(-8.0, 10.0, 0.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))

    # Floor
    floor_shape = Quad(color=glm.vec4(1.0), width=100.0, height=100.0)
    floor_texture = Texture(file_path=stone_texture_path)
    floor_mat   = Material(color_texture=floor_texture)
    floor_mat.texture_scale=glm.vec2(50)
    floor_obj   = MeshObject(floor_shape, floor_mat)
    floor_obj.transform = glm.rotate(glm.radians(-90), glm.vec3(1, 0, 0))
    glrenderer.addObject(floor_obj)

    # Create house body (cube)
    #TODO [1.1]: change the stone texture of the cube to the brick texture.
    cube_shape = Cube(color=glm.vec4(1.0))
    cube_texture = Texture(file_path=brick_texture_path)
    cube_mat   = Material(color_texture=cube_texture)
    cube_obj   = MeshObject(cube_shape, cube_mat)
    cube_obj.transform = glm.translate(glm.vec3(0.0, 0.5, -2.0)) * glm.scale(glm.vec3(1.0))
    glrenderer.addObject(cube_obj)

    #[2.0]: Create a roof, use a cone shape for the roof:
    # We set the shape's vertex color to red. The shader will multiply this with the texture.
    roof_shape = Cone(radius=glm.sqrt(0.5), segments=4, split_faces=False, color=glm.vec4(1.0, 0.2, 0.2, 1.0))

    #TODO [2.1]: Create a texture for the roof
    roof_texture = Texture(file_path=os.path.join(BASE_DIR, "assets", "brickwall2.jpg"))

    #TODO [2.2]: Create a material for the roof
    roof_mat = Material(color_texture=roof_texture)
    roof_mat.texture_scale = glm.vec2(2.0, 2.0)  # Adjust texture scale for the roof

    #TODO [2.3]: Create a transform for the roof
    # The transformation order is important: Scale -> Rotate -> Translate.
    # To get predictable results, transformations should be ordered: Translate * Rotate * Scale.
    # This scales the object in place, then rotates it in place, then moves it to the final destination.
    roof_transform = glm.translate(glm.vec3(0.0, 1.5, -2.0)) * glm.rotate(glm.radians(45), glm.vec3(0, 1, 0)) * glm.scale(glm.vec3(1.25, 1.25, 1.25))

    #TODO [2.4]: Create a MeshObject with the roof shape, material, and transform.
    roof_obj = MeshObject(roof_shape, roof_mat, transform=roof_transform)

    #TODO [2.5]: Add the roof to the renderer (uncomment this line)
    glrenderer.addObject(roof_obj)


    #TODO [3.0]: Look in the assets folder, and pick another texture you like.
    # For instance, set the floor texture to the "road_stone_tile.jpg" texture.
    # - Alternatively, add a texture of your choosing. It can be any image file.
    # It could be that your texture appears flipped, or squashed!
    # - Use ``material.texture_scale = glm.vec2(x, y)`` to solve this, with a negative x or y to flip around that axis.
    # To change the texture, we create a new Texture object and assign it to the material.
    obamium_texture = Texture(file_path=os.path.join(BASE_DIR, "assets", "obamium.jpg"))
    floor_mat.color_texture = obamium_texture
    floor_mat.texture_scale = glm.vec2(5.0, -5.0)

    #TODO [3.1]: Play around with the material properties of some objects. For instance:
    floor_mat.ambient_strength = 0.3
    floor_mat.diffuse_strength = 0.7
    floor_mat.specular_strength = 1
    floor_mat.shininess = 128.0

    #TODO [3.2]: Play around with the color of objects and different textures.
    # - How does the color affect the texture?
    # Try to make the roof red, but still have a texture.
    # As seen above, setting the shape's vertex color achieves the tinting effect.

    #[4.0]: Create a texture via code
    gradient_cube_shape = Cube()
    #[4.1]: Define a resolution. This is defined by a width and a height.
    # Commonly in graphics, images are square, and the size of each dimension is a power of two.
    gradient_texture_resolution = glm.ivec2(128, 128)
    gradient_cube_texture = Texture(resolution = gradient_texture_resolution)
    for px in range(gradient_texture_resolution.x):
        for py in range(gradient_texture_resolution.y):
            # TODO [4.1] set pixel values based on the pixel coordinates.
            # For instance, create a gradient from 0 to 1 in the red channel for the x dimension,
            #   and 0 to 1 in the green channel for the y dimension.
            # Tip: Remember that colors are in the range 0 to 1.
            r = px / (gradient_texture_resolution.x - 1)
            g = py / (gradient_texture_resolution.y - 1)
            b = py / (gradient_texture_resolution.x - 1)
            pixel_color = glm.vec4(r, g, b, 1.0)
            gradient_cube_texture.set_pixel(px, py, pixel_color)

    gradient_cube_mat   = Material(color_texture=gradient_cube_texture)
    gradient_cube_obj   = MeshObject(gradient_cube_shape, gradient_cube_mat)
    gradient_cube_obj.transform = glm.translate(glm.vec3(2.0, 0.5, -2.0)) * glm.scale(glm.vec3(1.0))
    glrenderer.addObject(gradient_cube_obj)

    # RENDER LOOP: called every frame, here you can animate your objects
    while not glfw.window_should_close(glwindow.window):
        # Draw framework shapes
        glrenderer.render()

    # end of render loop, deletes all necessary instances and finishes
    glrenderer.delete()
    # deletes the window and frees the memory
    glwindow.delete()
    return 0

if __name__ == "__main__":
    main()
