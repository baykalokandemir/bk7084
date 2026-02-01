import os
import sys

# Add framework to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from framework.window import OpenGLWindow
from framework.renderer import GLRenderer
from framework.camera import Flycamera
from framework.objects import MeshObject
from framework.materials import Material
from framework.shapes import Cube
from framework.utils.point_cloud_sampler import PointCloudSampler
from framework.utils.ui_manager import UIManager
from pyglm import glm
import OpenGL.GL as gl
import glfw
import imgui

def main():
    # 1. Window & Render Init
    try:
        window = OpenGLWindow(1080, 1080, "Hologram Point Cloud Test")
    except Exception as e:
        print(f"Failed: {e}")
        return

    camera = Flycamera(window.width, window.height, 70, 0.1, 100.0)
    camera.position = glm.vec3(0, 0, 5)
    
    glrenderer = GLRenderer(window, camera)
    glrenderer.init_post_process(window.width, window.height)
    
    # 2. UI Manager
    ui_manager = UIManager(window.window)
    ui_manager.setup_input_chaining(window)

    # 3. State
    # UI Control State
    # Note: Using Lists for ImGui pointer emulation
    ui_state = {
        "grid_spacing": [0.2],
        "point_size": [10.0],
        "point_shape": [0], # 0: Circle, 1: Square
        "rotation_speed": [0.5],
        "anim_x": True,
        "anim_y": True,
        "is_point_mode": True,
        "auto_rotate": True,
        "color": [0.0, 1.0, 1.0],
        "enable_glow": True,
        # Post Process
        "use_aberration": False,
        "aberration_strength": [0.005],
        "use_blur": False,
        "blur_strength": [0.002]
    }
    
    # Scene Objects
    current_mesh_obj = None
    
    def generate_mesh():
        nonlocal current_mesh_obj
        
        # Cleanup old
        if current_mesh_obj in glrenderer.objects:
            glrenderer.objects.remove(current_mesh_obj)
            
        print(f"Generating Point Cloud with spacing {ui_state['grid_spacing'][0]}...")
        
        # 1. Base Shape (Cube)
        base_cube = Cube(side_length=2.0)
        
        # 2. Generate Point Cloud
        # Ensure spacing is safe (not 0)
        spacing = max(0.01, ui_state['grid_spacing'][0])
        pc_shape = PointCloudSampler.generate(base_cube, spacing=spacing)
        pc_shape.createBuffers()
        
        # 3. Material
        mat = Material(vertex_shader="mikoshi_shader.vert", fragment_shader="mikoshi_shader.frag")
        
        # 4. Mesh Object
        current_mesh_obj = MeshObject(pc_shape, mat, draw_mode=gl.GL_POINTS)
        glrenderer.addObject(current_mesh_obj)

    # Initial Gen
    generate_mesh()

    # 4. Render Loop
    def draw_ui():
        imgui.begin("Hologram Controls")
        
        # Geometry Params (Requires Regen)
        if imgui.collapsing_header("Geometry Generation", visible=True)[0]:
            changed, ui_state["grid_spacing"][0] = imgui.slider_float("Grid Spacing", ui_state["grid_spacing"][0], 0.05, 1.0)
            if changed:
                generate_mesh() # Auto-regen on slider release ideally, but immediate is fine for simple test
                
            if imgui.button("Regenerate"):
                generate_mesh()
            
        # Render Uniforms (Realtime)
        if imgui.collapsing_header("Render Uniforms", visible=True)[0]:
            _, ui_state["point_size"][0] = imgui.slider_float("Point Size", ui_state["point_size"][0], 1.0, 50.0)
            _, ui_state["point_shape"][0] = imgui.combo("Point Shape", ui_state["point_shape"][0], ["Circle", "Square"])
            _, ui_state["color"] = imgui.color_edit3("Base Color", *ui_state["color"])
            
            _, ui_state["enable_glow"] = imgui.checkbox("Enable Glow", ui_state["enable_glow"])
            _, ui_state["anim_x"] = imgui.checkbox("Anim X Offset", ui_state["anim_x"])
            _, ui_state["anim_y"] = imgui.checkbox("Anim Y Offset", ui_state["anim_y"])
        
        imgui.separator()
        if imgui.collapsing_header("Transform", visible=True)[0]:
            _, ui_state["auto_rotate"] = imgui.checkbox("Auto Rotate", ui_state["auto_rotate"])
            _, ui_state["rotation_speed"][0] = imgui.slider_float("Rotation Speed", ui_state["rotation_speed"][0], 0.0, 5.0)

        imgui.separator()
        if imgui.collapsing_header("Post Processing", visible=True)[0]:
            _, ui_state["use_aberration"] = imgui.checkbox("Chromatic Aberration", ui_state["use_aberration"])
            if ui_state["use_aberration"]:
                _, ui_state["aberration_strength"][0] = imgui.slider_float("Aberration Strength", ui_state["aberration_strength"][0], 0.0, 0.05)
            
            _, ui_state["use_blur"] = imgui.checkbox("Blur", ui_state["use_blur"])
            if ui_state["use_blur"]:
                _, ui_state["blur_strength"][0] = imgui.slider_float("Blur Strength", ui_state["blur_strength"][0], 0.0, 0.01)

        imgui.text(f"Vertex Count: {len(current_mesh_obj.mesh.vertices) if current_mesh_obj else 0}")
        
        imgui.end()

    last_time = glfw.get_time()
    rotation_angle = 0.0

    while not glfw.window_should_close(window.window):
        current_time = glfw.get_time()
        dt = current_time - last_time
        last_time = current_time
        
        camera.update(dt)
        
        # Update Post Process
        glrenderer.use_post_process = ui_state["use_aberration"] or ui_state["use_blur"]
        glrenderer.aberration_strength = ui_state["aberration_strength"][0] if ui_state["use_aberration"] else 0.0
        glrenderer.blur_strength = ui_state["blur_strength"][0] if ui_state["use_blur"] else 0.0

        # Update Object Logic
        if current_mesh_obj:
            # 1. Rotation
            if ui_state["auto_rotate"]:
                rotation_angle += ui_state["rotation_speed"][0] * dt
                current_mesh_obj.transform = glm.rotate(rotation_angle, glm.vec3(0, 1, 0))
            
            # 2. Update Uniforms
            if current_mesh_obj.material.uniforms is None:
                current_mesh_obj.material.uniforms = {}
                
            u = current_mesh_obj.material.uniforms
            u["point_size"] = ui_state["point_size"][0]
            u["shape_type"] = int(ui_state["point_shape"][0])
            u["enable_glow"] = ui_state["enable_glow"]
            u["base_color"] = glm.vec3(*ui_state["color"])
            u["time"] = current_time
            u["anim_x"] = ui_state["anim_x"]
            u["anim_y"] = ui_state["anim_y"]
        
        glrenderer.render()
        ui_manager.render(draw_ui)
        
        glfw.swap_buffers(window.window)
        glfw.poll_events()
        
    ui_manager.shutdown()
    window.delete()
    glfw.terminate()

if __name__ == "__main__":
    main()
