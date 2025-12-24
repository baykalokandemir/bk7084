
import sys, os
import glfw
import OpenGL.GL as gl
import time
from pyglm import glm
import imgui
from imgui.integrations.glfw import GlfwRenderer

# Ensure we can import framework
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.window import *
from framework.renderer import *
from framework.camera import Flycamera
from framework.objects import MeshObject
from framework.materials import Material, Texture
from framework.shapes import Quad

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# Note: Material class loads from framework/shaders relative to its file, 
# so we pass just the filename assuming it's there.


class HologramConfig:
    color = [0.0, 1.0, 1.0]
    lines_freq = 100.0
    lines_thick = 0.5
    uv_scale = [1.0, 1.0] 
    uv_offset = [0.0, 0.0]
    flip_y = False
    quad_size = [2.0, 3.0] # Width, Height

def main():
    print("Starting Hologram GUI...")
    
    # 1. Create Window
    width, height = 1200, 900
    try:
        win = OpenGLWindow(width, height, "Hologram GUI")
    except Exception as e:
        print(f"Failed to create window: {e}")
        return

    # 2. Setup Camera
    cam = Flycamera(width, height, 70.0, 0.1, 100.0)
    cam.position = glm.vec3(0, 1, 3)
    cam.updateView()

    # 3. Setup Renderer
    ren = GLRenderer(win, cam)
    ren.clear_color = [0.1, 0.1, 0.1, 1.0]

    # 4. ImGui Setup
    imgui.create_context()
    impl = GlfwRenderer(win.window, attach_callbacks=False)

    # Callbacks wrapper (similar to Mikoshi)
    def key_callback_wrapper(window, key, scancode, action, mods):
        impl.keyboard_callback(window, key, scancode, action, mods)
        if not imgui.get_io().want_capture_keyboard:
            win.key_callback(window, key, scancode, action, mods)

    def mouse_button_callback_wrapper(window, button, action, mods):
        impl.mouse_callback(window, button, action, mods)
        if not imgui.get_io().want_capture_mouse:
            win.mouse_button_callback(window, button, action, mods)

    def scroll_callback_wrapper(window, x_offset, y_offset):
        impl.scroll_callback(window, x_offset, y_offset)
        if not imgui.get_io().want_capture_mouse:
            win.scroll_callback(window, x_offset, y_offset)
            
    def char_callback_wrapper(window, char):
        impl.char_callback(window, char)

    glfw.set_key_callback(win.window, key_callback_wrapper)
    glfw.set_mouse_button_callback(win.window, mouse_button_callback_wrapper)
    glfw.set_scroll_callback(win.window, scroll_callback_wrapper)
    glfw.set_char_callback(win.window, char_callback_wrapper)

    # 5. Load Texture
    tex_path = os.path.join(BASE_DIR, "assets", "hologram.jpg")
    if not os.path.exists(tex_path):
        print(f"Warning: Texture not found at {tex_path}")
        tex = None
    else:
        try:
            tex = Texture(file_path=tex_path)
            # Default to flipped if image is upside down typically
            # But we have a toggle now.
        except Exception as e:
            print(f"Failed to load texture: {e}")
            tex = None

    # 6. Create Material & Object
    try:
        mat = Material(fragment_shader="hologram.frag", color_texture=tex)
        mat.texture_scale = glm.vec2(1, 1)
        # Custom uniforms initialization
        mat.uniforms["hologram_color"] = glm.vec3(0.0, 1.0, 1.0)
        mat.uniforms["time"] = 0.0
    except Exception as e:
        print(f"Failed to create material/shader: {e}")
        return

    # Create Quad of size 1x1, scaled later
    obj = MeshObject(
        Quad(width=1.0, height=1.0), 
        mat, 
        transform=glm.translate(glm.vec3(0, 1.5, 0)), 
        enable_blending=True, 
        blend_func=(gl.GL_SRC_ALPHA, gl.GL_ONE)
    )
    ren.addObject(obj)
    
    # Floor
    floor_obj = MeshObject(
        Quad(width=10, height=10, color=glm.vec4(0.1, 0.1, 0.1, 1.0)), 
        Material(), 
        transform=glm.rotate(glm.radians(-90), glm.vec3(1, 0, 0))
    )
    ren.addObject(floor_obj)

    config = HologramConfig()
    
    print("Entering render loop...")
    start_time = time.time()
    last_frame = time.time()
    
    while not glfw.window_should_close(win.window):
        current_frame = time.time()
        dt = current_frame - last_frame
        last_frame = current_frame

        # Update Object Scale based on Config
        obj.transform = glm.translate(glm.vec3(0, 1.5, 0)) * glm.scale(glm.vec3(config.quad_size[0], config.quad_size[1], 1.0))

        # ImGui New Frame
        impl.process_inputs()
        imgui.new_frame()
        
        # UI Window
        imgui.begin("Hologram Controls")
        
        changed, config.color = imgui.color_edit3("Color", *config.color)
        changed, config.lines_freq = imgui.slider_float("Lines Frequency", config.lines_freq, 1.0, 500.0)
        changed, config.lines_thick = imgui.slider_float("Lines Thickness", config.lines_thick, 0.0, 1.0)

        imgui.separator()
        imgui.text("Size")
        changed, config.quad_size = imgui.slider_float2("Face Size (WxH)", *config.quad_size, min_value=0.1, max_value=5.0)

        imgui.separator()
        imgui.text("Transform")
        changed, config.uv_scale = imgui.slider_float2("Zoom (Scale)", *config.uv_scale, min_value=0.1, max_value=5.0)
        # Offset
        changed, config.uv_offset = imgui.slider_float2("Offset", *config.uv_offset, min_value=-1.0, max_value=1.0)
        
        changed, config.flip_y = imgui.checkbox("Flip Y (Fix Upside Down)", config.flip_y)

        if imgui.button("Auto Fit to Face"):
            if tex and tex.resolution:
                tex_w, tex_h = tex.resolution.x, tex.resolution.y
                quad_w, quad_h = config.quad_size[0], config.quad_size[1]
                
                tex_aspect = tex_w / tex_h
                quad_aspect = quad_w / quad_h
                
                # Logic to 'Cover' the quad
                if tex_aspect > quad_aspect:
                    # Texture is wider than quad (relative to aspect)
                    # Show full height (scale_y = 1), scale x to crop width
                    s_x = quad_aspect / tex_aspect
                    s_y = 1.0
                else:
                    # Texture is taller than quad
                    # Show full width (scale_x = 1), scale y to crop height
                    s_x = 1.0
                    s_y = tex_aspect / quad_aspect
                    
                config.uv_scale = [s_x, s_y]
                config.uv_offset = [0.0, 0.0]

        if imgui.button("Reset Transform"):
            config.uv_scale = [1.0, 1.0]
            config.uv_offset = [0.0, 0.0]
            config.flip_y = False

        imgui.end()

        # Update Uniforms
        mat.uniforms["time"] = current_frame - start_time
        mat.uniforms["hologram_color"] = glm.vec3(*config.color)
        mat.uniforms["lines_frequency"] = config.lines_freq
        mat.uniforms["lines_thickness"] = config.lines_thick
        mat.uniforms["uv_scale"] = glm.vec2(*config.uv_scale)
        mat.uniforms["uv_offset"] = glm.vec2(*config.uv_offset)
        mat.uniforms["flip_y"] = config.flip_y
        
        # Update Camera
        cam.update(dt)

        # Render Scene
        ren.render()
        
        # Render UI
        imgui.render()
        impl.render(imgui.get_draw_data())
        
        glfw.swap_buffers(win.window)
        glfw.poll_events()

    impl.shutdown()
    ren.delete()
    win.delete()

if __name__ == "__main__":
    main()
