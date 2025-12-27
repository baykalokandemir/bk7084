import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.camera import *
from framework.renderer import *
from framework.light import *
from framework.scene_manager import SceneManager
from framework.ui_manager import UIManager
from pyglm import glm
import OpenGL.GL as gl
import glfw
import imgui
from imgui.integrations.glfw import GlfwRenderer

# Configuration Class
class Config:
    POINT_COUNT = 500
    POINT_SIZE = 10.0
    POINT_SHAPE = 0 # 0: Circle, 1: Square
    POINT_SHAPES = ["Circle", "Square"]
    ANIM_RESIZE_X = False
    ANIM_RESIZE_X = False
    ANIM_RESIZE_Y = False
    USE_ABERRATION = False
    ABERRATION_STRENGTH = 0.005
    ROTATE = False
    SAMPLING_MODE = 1 # 0: random, 1: poisson, 2: regular
    SAMPLING_MODES = ['random', 'poisson', 'regular']
    
    SLICE_SPACING = 0.1
    SLICE_THICKNESS = 0.005
    SLICE_NORMAL = [1.0, 0.6, 0.0] # List for ImGui
    SLICE_WARP = 0.03
    SLICE_ANIMATE = True
    SLICE_SPEED = 0.1
    
    ENABLE_GLOW = True
    
    # Colors (RGB)
    POINT_CLOUD_COLOR = [0.0, 0.9, 1.0] # Cyan
    SLICE_COLOR = [1.0, 0.0, 0.2] # Red
    
    # Hues (0.0 - 1.0)
    POINT_CLOUD_HUE = 0.5
    SLICE_HUE = 0.97
    
    GLTF_PATH = None
    GLTF_SCALE = 0.1
    USE_POINT_CLOUD = True

def main():
    width, height = 1920, 1080
    glwindow = OpenGLWindow(width, height)
    
    camera = Flycamera(width, height, 70.0, 0.1, 100.0)
    camera.position = glm.vec3(0.0, 0.0, 5.0)
    camera.front = glm.normalize(glm.vec3(0.0, 0.0, 0.0) - camera.position)
    camera.updateView()
    
    glrenderer = GLRenderer(glwindow, camera)
    glrenderer.clear_color = [0.05, 0.05, 0.1, 1.0] # Dark blue background
    glrenderer.init_post_process(width, height)
    
    # ImGui Initialization
    imgui.create_context()
    impl = GlfwRenderer(glwindow.window, attach_callbacks=False)

    # Framebuffer Resize Callback
    def framebuffer_size_callback(window, width, height):
        gl.glViewport(0, 0, width, height)
        glrenderer.resize_post_process(width, height)
        camera.window_size_callback(width, height)
        
    glfw.set_framebuffer_size_callback(glwindow.window, framebuffer_size_callback)
    
    # Overwrite callbacks with our wrappers that call ImGui's handler AND our handler
    def key_callback_wrapper(window, key, scancode, action, mods):
        impl.keyboard_callback(window, key, scancode, action, mods)
        if not imgui.get_io().want_capture_keyboard:
            glwindow.key_callback(window, key, scancode, action, mods)

    def mouse_button_callback_wrapper(window, button, action, mods):
        impl.mouse_callback(window, button, action, mods)
        if not imgui.get_io().want_capture_mouse:
            glwindow.mouse_button_callback(window, button, action, mods)

    def scroll_callback_wrapper(window, x_offset, y_offset):
        impl.scroll_callback(window, x_offset, y_offset)
        if not imgui.get_io().want_capture_mouse:
            glwindow.scroll_callback(window, x_offset, y_offset)

    def char_callback_wrapper(window, char):
        impl.char_callback(window, char)
            
    # Set our wrappers
    glfw.set_key_callback(glwindow.window, key_callback_wrapper)
    glfw.set_mouse_button_callback(glwindow.window, mouse_button_callback_wrapper)
    glfw.set_scroll_callback(glwindow.window, scroll_callback_wrapper)
    glfw.set_char_callback(glwindow.window, char_callback_wrapper)
    
    # Managers
    config = Config()
    scene_manager = SceneManager()
    ui_manager = UIManager()
    
    # Initial Scene Generation
    initial_objects = scene_manager.generate_scene(config)
    for obj in initial_objects:
        glrenderer.addObject(obj)
    
    print(f"Starting render loop. Points: {config.POINT_COUNT}")
    
    last_time = glfw.get_time()
    
    while not glfw.window_should_close(glwindow.window):
        current_time = glfw.get_time()
        dt = current_time - last_time
        last_time = current_time
        
        # ImGui Input Processing
        impl.process_inputs()
        
        # Render UI
        ui_manager.render(config, scene_manager, glrenderer)
        
        # Update Scene Uniforms
        scene_manager.update_uniforms(config, dt)
        
        # Update Post-Process Uniforms
        glrenderer.use_post_process = config.USE_ABERRATION
        glrenderer.aberration_strength = config.ABERRATION_STRENGTH
        
        # Update camera
        camera.update(dt)
        
        # Render Scene
        glrenderer.render()
        
        # Draw UI Data
        impl.render(imgui.get_draw_data())
        
        glfw.swap_buffers(glwindow.window)
        glfw.poll_events()
        
    impl.shutdown()
    glrenderer.delete()
    glwindow.delete()

if __name__ == "__main__":
    main()
