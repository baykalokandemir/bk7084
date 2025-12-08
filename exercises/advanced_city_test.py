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
from framework.camera import Flycamera
import glfw
import glm
import imgui
from imgui.integrations.glfw import GlfwRenderer

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
    
    def create_city_objects():
        nonlocal city_object
        
        batcher = MeshBatcher()
        
        # Batch Buildings
        for shape in generator.buildings:
            # Random color per building
            import random
            col = glm.vec4(random.random(), random.random(), random.random(), 1.0)
            batcher.add_shape(shape, color=col)
            
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
