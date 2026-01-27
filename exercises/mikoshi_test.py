import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.camera import *
from framework.renderer import *
from framework.light import *
from framework.utils.ui_manager import UIManager
from framework.utils.holograms_3d import Holograms3D
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
    
    # Post Process
    USE_ABERRATION = False
    ABERRATION_STRENGTH = 0.005
    USE_BLUR = False
    BLUR_STRENGTH = 0.002
    
    # Legacy slice settings
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
        self.cluster = Holograms3D()

    def generate_scene(self, config):
        self.cluster.regenerate(config)
        self.objects = self.cluster.objects
        self.update_uniforms(config, 0.0)
        return self.objects

    def update_uniforms(self, config, dt):
        if not hasattr(self, 'accum_time'):
            self.accum_time = 0.0
        self.accum_time += dt

        # Update Cluster Logic (Animation)
        self.cluster.update(dt)
        self.cluster.update_uniforms(config, self.accum_time)

        if config.SLICE_ANIMATE:
            self.slice_offset += config.SLICE_SPEED * dt
            
        # Standard Slice update (Hologram uniforms handled by cluster)
        for obj in self.objects:
             if obj.material == self.slice_mat:
                obj.material.uniforms["slice_spacing"] = config.SLICE_SPACING
                obj.material.uniforms["slice_thickness"] = config.SLICE_THICKNESS
                obj.material.uniforms["slice_normal"] = glm.vec3(*config.SLICE_NORMAL)
                obj.material.uniforms["warp_factor"] = config.SLICE_WARP
                obj.material.uniforms["slice_offset"] = self.slice_offset
                obj.material.uniforms["color"] = glm.vec3(*config.SLICE_COLOR)

def draw_ui(config, scene_manager, renderer):
    """Scene-specific UI layout."""
    imgui.begin("Hologram Controls")
    
    # --- L-System Settings ---
    if imgui.collapsing_header("L-System Rules", visible=True)[0]:
        changed, config.L_ITERATIONS = imgui.slider_int("Iterations", config.L_ITERATIONS, 1, 5)
        changed, config.L_SIZE_LIMIT = imgui.slider_int("Max Objects", config.L_SIZE_LIMIT, 1, 50)
        changed, config.L_LENGTH = imgui.slider_float("Step Length", config.L_LENGTH, 0.5, 5.0)
        
        imgui.text("Angle Variance (Min/Max Deg)")
        changed, new_min = imgui.slider_float("Min Angle", config.L_ANGLE_MIN, 0.0, 180.0)
        if changed: config.L_ANGLE_MIN = new_min
        
        changed, new_max = imgui.slider_float("Max Angle", config.L_ANGLE_MAX, 0.0, 180.0)
        if changed: config.L_ANGLE_MAX = new_max
        
        imgui.separator()
        if imgui.button("Regenerate Structure"):
            new_objects = scene_manager.generate_scene(config)
            renderer.objects = []
            for obj in new_objects:
                renderer.addObject(obj)

    # --- Visual Settings ---
    if imgui.collapsing_header("Hologram Visuals", visible=True)[0]:
        _, config.GRID_SPACING = imgui.slider_float("Grid Spacing", config.GRID_SPACING, 0.02, 0.5)
        _, config.POINT_SIZE = imgui.slider_float("Point Size", config.POINT_SIZE, 1.0, 50.0) 
        clicked, current = imgui.combo("Shape", config.POINT_SHAPE, config.POINT_SHAPES)
        if clicked: config.POINT_SHAPE = current
        changed, config.POINT_CLOUD_COLOR = imgui.color_edit3("Color", *config.POINT_CLOUD_COLOR)
        _, config.ENABLE_GLOW = imgui.checkbox("Enable Glow", config.ENABLE_GLOW)
        
        if imgui.button("Apply Grid Changes"):
            new_objects = scene_manager.generate_scene(config)
            renderer.objects = []
            for obj in new_objects:
                renderer.addObject(obj)
                
    # --- Post Process ---
    if imgui.collapsing_header("Post Processing", visible=True)[0]:
        _, config.USE_ABERRATION = imgui.checkbox("Chromatic Aberration", config.USE_ABERRATION)
        if config.USE_ABERRATION:
            _, config.ABERRATION_STRENGTH = imgui.slider_float("Strength##Aber", config.ABERRATION_STRENGTH, 0.0, 0.05)
        _, config.USE_BLUR = imgui.checkbox("Blur", config.USE_BLUR)
        if config.USE_BLUR:
            _, config.BLUR_STRENGTH = imgui.slider_float("Strength##Blur", config.BLUR_STRENGTH, 0.0, 0.01)

    imgui.end()

def main():
    width, height = 1920, 1080
    glwindow = OpenGLWindow(width, height)
    
    camera = Flycamera(width, height, 70.0, 0.1, 100.0)
    camera.position = glm.vec3(0.0, 0.0, 12.0)
    camera.front = glm.normalize(glm.vec3(0.0, 0.0, 0.0) - camera.position)
    camera.updateView()
    
    glrenderer = GLRenderer(glwindow, camera)
    glrenderer.clear_color = [0.0, 0.0, 0.0, 1.0]
    glrenderer.init_post_process(width, height)
    
    # UI Manager (Handles ImGui Init & Input Chaining)
    ui_manager = UIManager(glwindow.window)
    ui_manager.setup_input_chaining(glwindow)

    # Framebuffer Resize Callback
    def framebuffer_size_callback(window, width, height):
        gl.glViewport(0, 0, width, height)
        glrenderer.resize_post_process(width, height)
        camera.window_size_callback(width, height)
        
    glfw.set_framebuffer_size_callback(glwindow.window, framebuffer_size_callback)
    
    # Managers
    config = Config()
    scene_manager = SceneManager()
    
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

        # Render UI (Processing Inputs handled internally)
        ui_manager.render(draw_ui, config, scene_manager, glrenderer)
        
        glfw.swap_buffers(glwindow.window)
        glfw.poll_events()
        
    ui_manager.shutdown()
    glrenderer.delete()
    glwindow.delete()

if __name__ == "__main__":
    main()
