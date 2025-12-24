
import sys, os
import glfw
import OpenGL.GL as gl
import time
from pyglm import glm

# Ensure we can import framework
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.window import *
from framework.renderer import *
from framework.camera import Flycamera
from framework.objects import MeshObject
from framework.materials import Material, Texture
from framework.shapes import Quad

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def main():
    print("Starting Hologram Single File Test...")
    
    # 1. Create Window
    width, height = 800, 600
    try:
        win = OpenGLWindow(width, height, "Hologram Single")
    except Exception as e:
        print(f"Failed to create window: {e}")
        return

    # 2. Setup Camera
    cam = Flycamera(width, height, 70.0, 0.1, 100.0)
    cam.position = glm.vec3(0, 1, 3)
    cam.lookAt = lambda *args: None # provisional fix if called internally, though I removed strict usage
    cam.updateView()

    # 3. Setup Renderer
    ren = GLRenderer(win, cam)

    # 4. Load Texture
    tex_path = os.path.join(BASE_DIR, "assets", "hologram.jpg")
    if not os.path.exists(tex_path):
        print(f"Warning: Texture not found at {tex_path}")
        tex = None
    else:
        try:
            tex = Texture(file_path=tex_path)
        except Exception as e:
            print(f"Failed to load texture: {e}")
            tex = None

    # 5. Create Material using the hologram shader
    # We rely on the Material class to load the shader files we created in framework/shaders
    try:
        mat = Material(fragment_shader="hologram.frag", color_texture=tex)
        mat.texture_scale = glm.vec2(1, 1)
        # Custom uniforms for the hologram shader
        mat.uniforms["hologram_color"] = glm.vec3(0.0, 1.0, 1.0) # Cyan
        mat.uniforms["time"] = 0.0
    except Exception as e:
        print(f"Failed to create material/shader: {e}")
        return

    # 6. Create Object (Vertical Quad)
    # 2 units wide, 3 units tall
    obj = MeshObject(
        Quad(width=2, height=3), 
        mat, 
        transform=glm.translate(glm.vec3(0, 1.5, 0)), 
        enable_blending=True, 
        blend_func=(gl.GL_SRC_ALPHA, gl.GL_ONE) # Additive blending
    )
    ren.addObject(obj)

    # 7. Add a floor for context
    floor_mat = Material() # Standard shader
    floor_obj = MeshObject(
        Quad(width=10, height=10, color=glm.vec4(0.1, 0.1, 0.1, 1.0)), 
        floor_mat, 
        transform=glm.rotate(glm.radians(-90), glm.vec3(1, 0, 0))
    )
    ren.addObject(floor_obj)

    # 8. Render Loop with explicit Swap and Poll
    print("Entering render loop...")
    start_time = time.time()
    last_frame = time.time()
    
    while not glfw.window_should_close(win.window):
        current_frame = time.time()
        dt = current_frame - last_frame
        last_frame = current_frame

        # Update uniforms
        mat.uniforms["time"] = current_frame - start_time
        
        # Update Camera
        cam.update(dt)

        # Render
        ren.render()
        
        # ESSENTIAL: Swap buffers and poll events
        glfw.swap_buffers(win.window)
        glfw.poll_events()

    print("Closing...")
    ren.delete()
    win.delete()

if __name__ == "__main__":
    main()
