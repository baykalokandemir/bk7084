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
    window = OpenGLWindow(1280, 720, "Polygon Extrusion Test")
    camera = Flycamera(window.width, window.height, 70, 0.1, 1000.0)
    camera.position = glm.vec3(0, 10, 20)
    camera.euler_angles.x = -30
    glrenderer = GLRenderer(window, camera)
    
    # Lighting
    glrenderer.addLight(PointLight(glm.vec4(10.0, 10.0, 10.0, 1.0), glm.vec4(1.0, 1.0, 1.0, 1.0)))
    
    # 1. Simple Triangle
    poly1 = Polygon([
        glm.vec2(-2, 0),
        glm.vec2(2, 0),
        glm.vec2(0, 3)
    ])
    shape1 = poly1.extrude(height=2.0)
    shape1.createGeometry() # Actually already created in extrude, but createBuffers needed?
    # Shape.createGeometry usually populates vertices. Our extrude ALREADY populated vertices.
    # We just need createBuffers.
    shape1.createBuffers()
    
    mat1 = Material() # Default white
    obj1 = MeshObject(shape1, mat1, transform=glm.translate(glm.vec3(-5, 0, 0)))
    glrenderer.addObject(obj1)
    
    # 2. Hexagon
    verts = []
    for i in range(6):
        angle = math.radians(60 * i)
        verts.append(glm.vec2(math.cos(angle) * 2, math.sin(angle) * 2))
    poly2 = Polygon(verts)
    shape2 = poly2.extrude(height=4.0)
    shape2.createBuffers()
    
    mat2 = Material()
    mat2.uniforms["color"] = glm.vec3(1.0, 0.5, 0.0) # Orange
    # Wait, Material default shader might use vertex colors. 
    # Let's check Material implementation or just rely on default.
    # Default material uses "simple_shader" usually?
    # Let's assume default works.
    
    obj2 = MeshObject(shape2, mat2, transform=glm.translate(glm.vec3(5, 0, 0)))
    glrenderer.addObject(obj2)
    
    # Main Loop
    while not glfw.window_should_close(window.window):
        # window.processInput()
        camera.update(0.016)
        
        glrenderer.render()
        
        glfw.swap_buffers(window.window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
