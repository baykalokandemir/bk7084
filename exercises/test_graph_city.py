import os
import sys

# Add framework to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from framework.window import OpenGLWindow
from framework.renderer import GLRenderer
from framework.objects import MeshObject
from framework.materials import Material
from framework.utils.city_generator import CityGenerator
from framework.utils.mesh_generator import MeshGenerator
from framework.utils.mesh_batcher import MeshBatcher
from framework.camera import Flycamera
from framework.light import PointLight
import OpenGL.GL as gl

import glfw
import glm
import imgui
from imgui.integrations.glfw import GlfwRenderer

def main():
    # Robust Window Init
    try:
        window = OpenGLWindow(1280, 720, "Graph City Test")
    except Exception as e:
        print(f"Failed to create window: {e}")
        return

    # Camera setup
    camera = Flycamera(window.width, window.height, 70, 0.1, 1000.0)
    camera.position = glm.vec3(0, 100, 100)
    camera.euler_angles.x = -60
    
    glrenderer = GLRenderer(window, camera)
    
    # Light
    glrenderer.addLight(PointLight(glm.vec4(100.0, 200.0, 100.0, 1.0), glm.vec4(0.8, 0.8, 0.8, 1.0)))

    # ImGui Setup
    imgui.create_context()
    impl = GlfwRenderer(window.window, attach_callbacks=False)

    # Callbacks
    def key_callback(win, key, scancode, action, mods):
        impl.keyboard_callback(win, key, scancode, action, mods)
        window.key_callback(win, key, scancode, action, mods)
    glfw.set_key_callback(window.window, key_callback)

    def mouse_button_callback(win, button, action, mods):
        if 0 <= button < 5:
            imgui.get_io().mouse_down[button] = (action == glfw.PRESS)
        window.mouse_button_callback(win, button, action, mods)
    glfw.set_mouse_button_callback(window.window, mouse_button_callback)

    # City Generation State
    city_gen = CityGenerator()
    mesh_gen = MeshGenerator()
    
    # Store objects to remove them later
    current_objects = []

    def regenerate():
        nonlocal current_objects
        
        # Clear old objects
        for obj in current_objects:
            if obj in glrenderer.objects:
                glrenderer.objects.remove(obj)
        current_objects = []
        
        # 1. Generate Grid (Deterministic)
        print("Generating Grid...")
        city_gen.generate_grid(rows=10, cols=10, spacing=40.0) 
        print(f"Nodes: {len(city_gen.graph.nodes)}, Edges: {len(city_gen.graph.edges)}")
        
        # 2. Naturalization (The Fix for Monotony)
        print("Naturalizing City...")
        city_gen.apply_irregularity(distortion=15.0, cull_chance=0.2)
        print(f"Nodes (Post-Cull): {len(city_gen.graph.nodes)}, Edges (Post-Cull): {len(city_gen.graph.edges)}")
        
        # 3. Generate Geometry
        print("Generating Mesh...")
        meshes = mesh_gen.generate(city_gen.graph)
        
        # 4. Batching (The Fix for Freezing)
        print("Batching...")
        batcher = MeshBatcher()
        for shape in meshes:
            batcher.add_shape(shape)
            
        # Build one unified mesh
        city_mesh = batcher.build(Material())
        
        if city_mesh:
            glrenderer.addObject(city_mesh)
            current_objects.append(city_mesh)
        
        print("Done.")
            
    # Initial Gen
    regenerate()

    # Main Loop
    while not glfw.window_should_close(window.window):
        impl.process_inputs()
        camera.update(0.016)
        
        glrenderer.render()
        
        # GUI
        imgui.new_frame()
        imgui.begin("City Controls")
        
        if imgui.button("Regenerate"):
            regenerate()
            
        imgui.text(f"Nodes: {len(city_gen.graph.nodes)}")
        imgui.text(f"Edges: {len(city_gen.graph.edges)}")
            
        imgui.end()
        imgui.render()
        impl.render(imgui.get_draw_data())
        
        glfw.swap_buffers(window.window)
        glfw.poll_events()
        
    window.delete()
    glfw.terminate()

if __name__ == "__main__":
    main()