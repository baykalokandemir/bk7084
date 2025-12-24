
import os
import sys

# Add framework to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from framework.window import OpenGLWindow
from framework.renderer import GLRenderer
from framework.light import PointLight
from framework.objects import MeshObject
from framework.materials import Material
from framework.camera import Flycamera
from framework.utils.street_light import StreetLight
from framework.utils.mesh_batcher import MeshBatcher
from framework.shapes import Cube 
import glfw
import glm
import numpy as np
from framework.shapes.shape import Shape


def main():
    window = OpenGLWindow(1280, 720, "Street Light Test")
    camera = Flycamera(window.width, window.height, 70, 0.1, 1000.0)
    camera.position = glm.vec3(5, 5, 10)
    camera.euler_angles.x = -20
    camera.euler_angles.y = 180 + 20 # Look at origin
    
    # IMPORTANT: Link camera to window for input callbacks
    window.camera = camera
    
    glrenderer = GLRenderer(window, camera)
    
    # 1. Dark Gray Ground Plane
    ground_mat = Material()
    # Simple quad shape
    ground_shape = Shape()
    w = 20.0
    verts = [
        glm.vec4(-w, 0, -w, 1.0),
        glm.vec4(w, 0, -w, 1.0),
        glm.vec4(w, 0, w, 1.0),
        glm.vec4(-w, 0, w, 1.0)
    ]
    norms = [glm.vec3(0, 1, 0)] * 4
    col = glm.vec4(0.2, 0.2, 0.2, 1.0) # Dark Gray
    cols = [col] * 4
    inds = [0, 1, 2, 0, 2, 3]
    
    ground_shape.vertices = np.array([v.to_list() for v in verts], dtype=np.float32)
    ground_shape.normals = np.array([n.to_list() for n in norms], dtype=np.float32) 
    ground_shape.uvs = np.zeros((4, 2), dtype=np.float32)
    ground_shape.colors = np.array([c.to_list() for c in cols], dtype=np.float32)
    ground_shape.indices = np.array(inds, dtype=np.uint32)
    
    ground_shape.createBuffers()
    ground_obj = MeshObject(ground_shape, ground_mat)
    glrenderer.addObject(ground_obj)
    
    # 2. Street Light
    sl = StreetLight()
    sl_shape = sl.generate_mesh()
    sl_shape.createBuffers()
    
    # Place at Origin
    sl_obj = MeshObject(sl_shape, Material())
    glrenderer.addObject(sl_obj)
    
    # 3. Add Light Source from Street Light
    bulb_pos = sl.bulb_offset
    # Offset is local (and obj is at 0,0,0)
    world_pos = glm.vec4(bulb_pos, 1.0) 
    
    light_color = glm.vec4(1.0, 0.9, 0.7, 1.0)
    glrenderer.addLight(PointLight(world_pos, light_color))
    
    # Add ambient/fill light to see the pole itself better if needed
    # glrenderer.addLight(PointLight(glm.vec4(10, 10, 10, 1.0), glm.vec4(0.2, 0.2, 0.2, 1.0)))

    while not glfw.window_should_close(window.window):
        # Window callbacks handle inputs and update camera state (pressed keys)
        # We just need update step
        camera.update(0.016)
        
        glrenderer.render()
        
        glfw.swap_buffers(window.window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
