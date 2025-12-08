import os
import sys

# Add framework to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from framework.window import OpenGLWindow
from framework.renderer import GLRenderer
from framework.light import PointLight
from framework.shapes import Car, Cube
from framework.objects import InstancedMeshObject, MeshObject
from framework.materials import Material
from framework.utils.city_generator import CityGenerator
from framework.camera import Flycamera
import imgui
from imgui.integrations.glfw import GlfwRenderer
import glfw
import glm
import math
import random
import numpy as np

def main():
    window = OpenGLWindow(1280, 720, "City Generation Test (BSP)")
    camera = Flycamera(window.width, window.height, 70, 0.1, 1000.0)
    camera.position = glm.vec3(0, 100, 100) # Higher up
    camera.euler_angles.x = -60 # pitch down more
    camera.euler_angles.y = -90 # yaw
    glrenderer = GLRenderer(window, camera)
    
    # Lighting
    glrenderer.addLight(PointLight(glm.vec4(100.0, 100.0, 100.0, 1.0), glm.vec4(0.8, 0.8, 0.8, 1.0)))
    glrenderer.addLight(PointLight(glm.vec4(-100.0, 100.0, 100.0, 1.0), glm.vec4(0.5, 0.5, 0.5, 1.0)))
    
    # Init ImGui with attach_callbacks=False to avoid stealing inputs
    imgui.create_context()
    impl = GlfwRenderer(window.window, attach_callbacks=False)
    
    # Manual Callback Chaining
    def key_callback(win, key, scancode, action, mods):
        impl.keyboard_callback(win, key, scancode, action, mods)
        window.key_callback(win, key, scancode, action, mods)
    glfw.set_key_callback(window.window, key_callback)

    def mouse_button_callback(win, button, action, mods):
        # impl.mouse_button_callback(win, button, action, mods) # Not exposed?
        # Manual update for ImGui
        if 0 <= button < 5:
            imgui.get_io().mouse_down[button] = (action == glfw.PRESS)
        window.mouse_button_callback(win, button, action, mods)
    glfw.set_mouse_button_callback(window.window, mouse_button_callback)

    def scroll_callback(win, x_offset, y_offset):
        impl.scroll_callback(win, x_offset, y_offset)
        window.scroll_callback(win, x_offset, y_offset)
    glfw.set_scroll_callback(window.window, scroll_callback)

    def char_callback(win, char):
        impl.char_callback(win, char)
    glfw.set_char_callback(window.window, char_callback)
    
    def resize_callback(win, width, height):
        impl.resize_callback(win, width, height)
        window.window_size_callback(win, width, height)
    glfw.set_window_size_callback(window.window, resize_callback)
    
    # Generate City
    road_len = 8.0 # Base length for scaling
    road_width = 2.0
    # Pass flat=False for real heights
    generator = CityGenerator(width=400.0, depth=400.0, min_block_size=20.0, road_width=road_width, flat=False)
    generator.generate()
    
    print(f"Generated {len(generator.road_cubes)} road segments.")
    print(f"Generated {len(generator.building_cubes)} buildings.")
    
    # Create Instanced Road (Cubes)
    road_shape = Cube()
    road_mat = Material()
    
    road_transforms = generator.road_cubes
    road_colors = [glm.vec4(0.2, 0.2, 0.2, 1.0)] * len(road_transforms) # Dark gray roads
    
    if road_transforms:
        road_inst = InstancedMeshObject(road_shape, road_mat, transforms=road_transforms, colors=road_colors)
        glrenderer.addObject(road_inst)
        
    # Create Buildings (Cubes)
    building_mat = Material()
    
    building_transforms = generator.building_cubes
    building_colors = generator.building_colors
    
    if building_transforms:
        building_inst = InstancedMeshObject(Cube(), building_mat, transforms=building_transforms, colors=building_colors)
        glrenderer.addObject(building_inst)
    
    # Add some cars
    car_shape = Car()
    car_mat = Material()
    car_transforms = []
    car_colors = []
    
    # Place cars on random roads
    for i in range(100):
        if not road_transforms: break
        idx = random.randrange(len(road_transforms))
        T = road_transforms[idx]
        
        # T is the transform of the road cube.
        # Road cube is scaled.
        # We want to place the car on top of the road.
        # Road height (Y) is 0.1. Top is at y=0.05 (if centered) or y=0.1 (if bottom at 0).
        # Our Cube shape is centered at origin with side length 1.
        # So T scales it by (w, 0.1, l).
        # The top surface is at T * (0, 0.5, 0).
        
        # Extract position from T
        pos = glm.vec3(T[3])
        
        # Add offset to put car on top
        # Car origin is usually at its bottom center.
        # Road top is at pos.y + 0.05 (half of 0.1).
        car_pos = glm.vec3(pos.x, pos.y + 0.05, pos.z)
        
        # Randomize position along the road?
        # We don't know the road orientation easily from T without decomposing.
        # But we know roads are either X or Z aligned.
        # Scale tells us dimensions.
        # sx = length(T[0]), sz = length(T[2])
        sx = glm.length(glm.vec3(T[0]))
        sz = glm.length(glm.vec3(T[2]))
        
        # If sx > sz, road is along X.
        # If sz > sx, road is along Z.
        
        offset = 0.0
        if sx > sz:
            # Along X
            offset = random.uniform(-sx/2 * 0.8, sx/2 * 0.8)
            car_pos.x += offset
            # Rotate car to face X (or -X)
            angle = 90 if random.random() < 0.5 else -90
        else:
            # Along Z
            offset = random.uniform(-sz/2 * 0.8, sz/2 * 0.8)
            car_pos.z += offset
            # Rotate car to face Z (or -Z)
            angle = 0 if random.random() < 0.5 else 180
            
        # Create car transform
        car_T = glm.translate(car_pos) * glm.rotate(math.radians(angle), glm.vec3(0, 1, 0))
        # Scale car if needed? Car shape might be big.
        # Let's assume Car shape is reasonable size.
        
        car_transforms.append(car_T)
        car_colors.append(glm.vec4(random.random(), random.random(), random.random(), 1.0))
        
    if car_transforms:
        car_inst = InstancedMeshObject(car_shape, car_mat, transforms=car_transforms, colors=car_colors)
        glrenderer.addObject(car_inst)

    # Main Loop
    while not glfw.window_should_close(window.window):
        impl.process_inputs()
        # window.processInput() # OpenGLWindow doesn't have this? It has callbacks.
        camera.update(0.016) # Add dt
        
        glrenderer.render() # render takes no args? No, it takes camera? 
        # In renderer.py: def render (self): ... o.draw(self.glwindow.camera, ...)
        # So glrenderer.render() is correct.
        
        # GUI
        imgui.new_frame()
        imgui.begin("City Controls")
        if imgui.button("Regenerate"):
            generator.generate()
            
            # Update Road Instance
            road_transforms = generator.road_cubes
            road_colors = [glm.vec4(0.2, 0.2, 0.2, 1.0)] * len(road_transforms)
            
            if 'road_inst' in locals():
                if road_inst in glrenderer.objects:
                    glrenderer.objects.remove(road_inst)
            
            if road_transforms:
                road_inst = InstancedMeshObject(road_shape, road_mat, transforms=road_transforms, colors=road_colors)
                glrenderer.addObject(road_inst)
                
            # Update Buildings
            building_transforms = generator.building_cubes
            building_colors = generator.building_colors
            
            if 'building_inst' in locals():
                if building_inst in glrenderer.objects:
                    glrenderer.objects.remove(building_inst)
            
            if building_transforms:
                building_inst = InstancedMeshObject(Cube(), building_mat, transforms=building_transforms, colors=building_colors)
                glrenderer.addObject(building_inst)
                
        imgui.end()
        imgui.render()
        impl.render(imgui.get_draw_data())
        
        glfw.swap_buffers(window.window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
