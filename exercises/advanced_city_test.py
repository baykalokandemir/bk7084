import os
import sys

# Add framework to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from framework.window import OpenGLWindow
from framework.renderer import GLRenderer
from framework.light import PointLight
from framework.objects import MeshObject
from framework.materials import Material
from framework.utils.advanced_city_generator import AdvancedCityGenerator
from framework.utils.mesh_batcher import MeshBatcher
from framework.utils.street_light import StreetLight
from framework.camera import Flycamera
import glfw
import glm
import imgui
from imgui.integrations.glfw import GlfwRenderer
import numpy as np

def main():
    window = OpenGLWindow(1280, 720, "Advanced City Generation (Organic & Batched)")
    camera = Flycamera(window.width, window.height, 70, 0.1, 1000.0)
    camera.position = glm.vec3(0, 100, 100)
    camera.euler_angles.x = -60
    glrenderer = GLRenderer(window, camera)
    
    # Lighting
    glrenderer.addLight(PointLight(glm.vec4(100.0, 100.0, 100.0, 1.0), glm.vec4(0.8, 0.8, 0.8, 1.0)))
    
    # Init ImGui
    imgui.create_context()
    impl = GlfwRenderer(window.window, attach_callbacks=False)
    
    # Callbacks (Simplified)
    def key_callback(win, key, scancode, action, mods):
        impl.keyboard_callback(win, key, scancode, action, mods)
        window.key_callback(win, key, scancode, action, mods)
    glfw.set_key_callback(window.window, key_callback)

    def mouse_button_callback(win, button, action, mods):
        if 0 <= button < 5:
            imgui.get_io().mouse_down[button] = (action == glfw.PRESS)
        window.mouse_button_callback(win, button, action, mods)
    glfw.set_mouse_button_callback(window.window, mouse_button_callback)
    
    # Generate City
    generator = AdvancedCityGenerator(width=400.0, depth=400.0, min_block_area=4000.0, min_lot_area=1000.0, ortho_chance=0.9)
    generator.generate()
    
    print(f"Generated {len(generator.blocks)} blocks.")
    print(f"Generated {len(generator.lots)} lots.")
    
    # Create Objects using Batching
    city_object = None
    all_bulb_positions = []
    
    def create_city_objects():
        nonlocal city_object
        
        batcher = MeshBatcher()
        
        # Batch Buildings
        for shape in generator.buildings:
            # Random color per building
            import random
            col = glm.vec4(random.random(), random.random(), random.random(), 1.0)
            batcher.add_shape(shape, color=col)
            
        # Batch Parks (Green)
        for shape in generator.parks:
            col = glm.vec4(0.2, 0.8, 0.2, 1.0)
            batcher.add_shape(shape, color=col)
            
        # Batch Roads (Asphalt + Stripes)
        # They have their own colors in the shape, so pass color=None to use vertex colors
        for shape in generator.roads:
            batcher.add_shape(shape)
            
            
        # Batch Sidewalks (Gray)
        for shape in generator.sidewalks:
            batcher.add_shape(shape)
            

        # Batch Street Lights & Add Lights
        sl_gen = StreetLight()
        sl_shape = sl_gen.generate_mesh()
        
        
        # Batch Street Lights & Collect Bulb Positions
        sl_gen = StreetLight()
        sl_shape = sl_gen.generate_mesh()
        
        # Store all bulb positions for dynamic culling
        nonlocal all_bulb_positions
        all_bulb_positions = []
        
        count_valid = 0
        for pose in generator.street_light_poses:
            # Robust Check for NaNs or Infinity in the matrix
            # pose is a glm.mat4, which behaves like a list of 4 columns (vec4s) or list of list.
            # We convert to numpy buffer to check easily or just iterate.
            is_valid = True
            for col in range(4):
                for row in range(4):
                    val = pose[col][row]
                    import math
                    if math.isnan(val) or math.isinf(val):
                        is_valid = False
                        break
                if not is_valid: break
            
            if not is_valid:
                continue
                 
            batcher.add_shape(sl_shape, transform=pose)
            
            # Calculate world position of bulb
            bulb_local = glm.vec4(sl_gen.bulb_offset, 1.0)
            bulb_world = pose * bulb_local
            all_bulb_positions.append(bulb_world)
            count_valid += 1
            
        print(f"Generated {count_valid} valid street lights (filtered from {len(generator.street_light_poses)})")
            
        mat = Material()
            
        mat = Material()
        # Reduce specular strength to avoid "shiny lines" on ground
        mat.specular_strength = 0.1
            
        mat = Material()
        # Use vertex colors
        # Ensure shader uses vertex colors. Default shader usually does if available.
        
        city_object = batcher.build(mat)
        if city_object:
            glrenderer.addObject(city_object)
            
    create_city_objects()
    
    # Main Loop
    while not glfw.window_should_close(window.window):
        impl.process_inputs()
        camera.update(0.016)
        
        # Dynamic Lighting Culling
        # 1. Always keep the main sun/ambient light (index 0)
        main_light = glrenderer.lights[0] if len(glrenderer.lights) > 0 else None
        
        # 2. Find closest street lights
        active_lights = [main_light] if main_light else []
        
        if len(all_bulb_positions) > 0:
            cam_pos = camera.position
            
            # Helper to get distance squared
            def dist_sq(pos_vec4):
                # pos_vec4 is glm.vec4
                # cam_pos is glm.vec3
                p = glm.vec3(pos_vec4)
                d = p - cam_pos
                return glm.dot(d, d)
                
            # Sort all lights by distance
            # Optimization: If we have thousands, this might differ.
            # But for ~hundreds it's fine.
            sorted_bulbs = sorted(all_bulb_positions, key=dist_sq)
            
            # Pick closest 8 (leaving room for sun + maybe one more)
            closest_bulbs = sorted_bulbs[:8]
            
            light_col = glm.vec4(1.0, 0.9, 0.7, 1.0)
            for bulb_pos in closest_bulbs:
                active_lights.append(PointLight(bulb_pos, light_col))
                
        # 3. Update renderer
        glrenderer.lights = active_lights
        
        glrenderer.render()
        
        # GUI
        imgui.new_frame()
        imgui.begin("Controls")
        if imgui.button("Regenerate"):
            # Clear old objects
            if city_object and city_object in glrenderer.objects:
                glrenderer.objects.remove(city_object)
            
            generator.generate()
            create_city_objects()
            print(f"Regenerated: {len(generator.blocks)} blocks, {len(generator.lots)} lots.")
            
        imgui.end()
        imgui.render()
        impl.render(imgui.get_draw_data())
        
        glfw.swap_buffers(window.window)
        glfw.poll_events()

    glfw.terminate()

if __name__ == "__main__":
    main()
