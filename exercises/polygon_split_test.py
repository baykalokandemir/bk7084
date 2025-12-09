import os
import sys

# Add framework to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from framework.window import OpenGLWindow
from framework.renderer import GLRenderer
from framework.light import PointLight
from framework.objects import MeshObject
from framework.materials import Material
from framework.utils.polygon import Polygon
from framework.camera import Flycamera
import glfw
import glm
import math

def main():
    window = OpenGLWindow(1280, 720, "Polygon Split Test")
    camera = Flycamera(window.width, window.height, 70, 0.1, 1000.0)
    camera.position = glm.vec3(0, 10, 20)
    camera.euler_angles.x = -30
    glrenderer = GLRenderer(window, camera)
    
    # Lighting
    glrenderer.addLight(PointLight(glm.vec4(10.0, 10.0, 10.0, 1.0), glm.vec4(1.0, 1.0, 1.0, 1.0)))
    
    # 1. Square to Split
    # Center at 0,0, size 4x4
    poly = Polygon([
        glm.vec2(-2, -2),
        glm.vec2(2, -2),
        glm.vec2(2, 2),
        glm.vec2(-2, 2)
    ])
    
    # Split Line: Diagonal y = x (approx)
    # Point (0,0), Dir (1, 1) normalized
    split_point = glm.vec2(0, 0)
    split_dir = glm.normalize(glm.vec2(1, 1))
    
    poly1, poly2 = poly.split(split_point, split_dir)
    
    if poly1 and poly2:
        print(f"Split successful!")
        print(f"Poly1 verts: {len(poly1.vertices)}")
        print(f"Poly2 verts: {len(poly2.vertices)}")
        
        # Extrude and Render Poly1 (Red)
        shape1 = poly1.extrude(height=2.0)
        shape1.createBuffers()
        mat1 = Material()
        mat1.uniforms["color"] = glm.vec3(1.0, 0.2, 0.2) # Red
        obj1 = MeshObject(shape1, mat1, transform=glm.translate(glm.vec3(-2, 0, 0))) # Move left slightly
        glrenderer.addObject(obj1)
        
        # Extrude and Render Poly2 (Blue)
        shape2 = poly2.extrude(height=2.0)
        shape2.createBuffers()
        mat2 = Material()
        mat2.uniforms["color"] = glm.vec3(0.2, 0.2, 1.0) # Blue
        obj2 = MeshObject(shape2, mat2, transform=glm.translate(glm.vec3(2, 0, 0))) # Move right slightly
        glrenderer.addObject(obj2)
        
    else:
        print("Split failed (no intersection or all on one side)")
        # Render original
        shape = poly.extrude(height=2.0)
        shape.createBuffers()
        mat = Material()
        obj = MeshObject(shape, mat)
        glrenderer.addObject(obj)
    
    # Main Loop
    while not glfw.window_should_close(window.window):
        camera.update(0.016)
        glrenderer.render()
        glfw.swap_buffers(window.window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
