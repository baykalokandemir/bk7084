import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.camera import *
from framework.renderer import *
from framework.light import *
from framework.ui_manager import UIManager
from framework.shapes import UVSphere, Cube, Cylinder, Cone
from framework.objects import MeshObject
from framework.utils.hologram_wrapper import HologramWrapper
from framework.utils.l_system import HologramLSystem
from framework.utils.hologram_agent import HologramAgent
from framework.materials import Material
from pyglm import glm
import OpenGL.GL as gl
import glfw
import imgui
import random
from imgui.integrations.glfw import GlfwRenderer

# Configuration Class
class Config:
    # L-System Parameters
    L_ITERATIONS = 2
    L_SIZE_LIMIT = 12
    L_LENGTH = 2.5
    L_ANGLE_MIN = 30.0
    L_ANGLE_MAX = 120.0
    
    # Hologram Settings
    GRID_SPACING = 0.075
    POINT_SIZE = 10.0
    POINT_SHAPE = 0 # 0: Circle, 1: Square
    POINT_SHAPES = ["Circle", "Square"]
    POINT_CLOUD_COLOR = [0.0, 0.9, 1.0] # Cyan
    ENABLE_GLOW = True
    USE_POINT_CLOUD = True
    
    # Post Process (Keep as they are global renderer settings)
    USE_ABERRATION = False
    ABERRATION_STRENGTH = 0.005
    USE_BLUR = False
    BLUR_STRENGTH = 0.002
    
    # Legacy slice settings (Minimal defaults just in case shader needs them, but we won't expose in UI)
    SLICE_SPACING = 0.1
    SLICE_THICKNESS = 0.005
    SLICE_NORMAL = [1.0, 0.6, 0.0]
    SLICE_WARP = 0.03
    SLICE_ANIMATE = True
    SLICE_SPEED = 0.1
    SLICE_COLOR = [1.0, 0.0, 0.2]

class SceneManager:
    def __init__(self):
        self.slice_mat = Material(vertex_shader="slice_shader.vert", fragment_shader="slice_shader.frag")
        self.slice_offset = 0.0
        self.objects = []
        self.agents = [] 

    def generate_scene(self, config):
        self.agents = [] # Clear agents
        
        # Pool
        pool = [
            Cube(side_length=1.5),
            UVSphere(radius=0.7),
            Cylinder(radius=0.7, height=1.5),
            Cone(radius=0.7, height=1.5)
        ]
        
        root_transform = glm.translate(glm.vec3(0, 0.0, 0))
        
        objects = HologramLSystem.create_group(
            root_transform=root_transform,
            source_shapes_pool=pool,
            axiom="F",
            rules={"F": "F[+F][-F][&F][^F]"},
            iterations=config.L_ITERATIONS,
            size_limit=config.L_SIZE_LIMIT, 
            grid_spacing=config.GRID_SPACING,
            color=glm.vec3(*config.POINT_CLOUD_COLOR),
            use_point_cloud=config.USE_POINT_CLOUD,
            length=config.L_LENGTH,
            angle_range=(config.L_ANGLE_MIN, config.L_ANGLE_MAX)
        )
        
        for obj in objects:
            speed = random.uniform(0.5, 2.0)
            agent = HologramAgent(obj, rotation_speed=speed)
            self.agents.append(agent)
            
        self.objects = objects
        self.update_uniforms(config, 0.0)
        return self.objects

    def update_uniforms(self, config, dt):
        if not hasattr(self, 'accum_time'):
            self.accum_time = 0.0
        self.accum_time += dt

        for agent in self.agents:
            agent.update(dt)

        if config.SLICE_ANIMATE:
            self.slice_offset += config.SLICE_SPEED * dt
            
        for obj in self.objects:
            if hasattr(obj.material, 'vertex_shader') and obj.material.vertex_shader == "mikoshi_shader.vert":
                obj.material.uniforms["enable_glow"] = config.ENABLE_GLOW
                obj.material.uniforms["base_color"] = glm.vec3(*config.POINT_CLOUD_COLOR)
                obj.material.uniforms["point_size"] = config.POINT_SIZE
                obj.material.uniforms["shape_type"] = config.POINT_SHAPE
                obj.material.uniforms["time"] = self.accum_time
            elif obj.material == self.slice_mat:
                # Keep slice uniforms just in case logic falls back
                obj.material.uniforms["slice_spacing"] = config.SLICE_SPACING
                obj.material.uniforms["slice_thickness"] = config.SLICE_THICKNESS
                obj.material.uniforms["slice_normal"] = glm.vec3(*config.SLICE_NORMAL)
                obj.material.uniforms["warp_factor"] = config.SLICE_WARP
                obj.material.uniforms["slice_offset"] = self.slice_offset
                obj.material.uniforms["color"] = glm.vec3(*config.SLICE_COLOR)

def main():
    width, height = 1920, 1080
    glwindow = OpenGLWindow(width, height)
    
    camera = Flycamera(width, height, 70.0, 0.1, 100.0)
    camera.position = glm.vec3(0.0, 0.0, 12.0)  # Moved camera back further
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
    
    print("Starting render loop.")
    
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
        glrenderer.use_post_process = config.USE_ABERRATION or config.USE_BLUR
        glrenderer.aberration_strength = config.ABERRATION_STRENGTH if config.USE_ABERRATION else 0.0
        glrenderer.blur_strength = config.BLUR_STRENGTH if config.USE_BLUR else 0.0
        
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
