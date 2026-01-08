import os
import sys

# Add framework to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from framework.window import OpenGLWindow
from framework.renderer import GLRenderer
from framework.objects import MeshObject
from framework.materials import Material
from framework.utils.city_generator import CityGenerator
from framework.utils.advanced_city_generator import AdvancedCityGenerator
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
        window = OpenGLWindow(1280, 720, "Graph City Test - Hybrid Mode")
    except Exception as e:
        print(f"Failed to create window: {e}")
        return

    # Camera setup
    camera = Flycamera(window.width, window.height, 70, 0.1, 1000.0)
    camera.position = glm.vec3(0, 150, 150)
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
    
    # Toggle State
    show_buildings = [False] 
    
    # Store explicit references
    current_objects = []
    city_mesh_obj = None
    building_mesh_obj = None
    debug_mesh_obj = None

    def regenerate():
        nonlocal current_objects, city_mesh_obj, building_mesh_obj, debug_mesh_obj
        
        # Clear old objects
        for obj in current_objects:
            if obj in glrenderer.objects:
                glrenderer.objects.remove(obj)
        current_objects = []
        city_mesh_obj = None
        building_mesh_obj = None
        debug_mesh_obj = None
        
        # 1. Generate BSP Layout (Visuals + Layout)
        print("Generating BSP Layout...")
        adv_gen = AdvancedCityGenerator(width=400, depth=400)
        adv_gen.generate()
        
        # 2. Build Traffic Graph (Logic Only)
        print("Building Traffic Graph...")
        city_gen.build_graph_from_layout(adv_gen)
        
        # 3. Batch Visuals (ALL from BSP)
        print("Batching Visuals (BSP)...")
        
        # Batch 1: Infrastructure (Roads, Sidewalks, Parks)
        batcher_infra = MeshBatcher()
        for shape in adv_gen.roads:
            batcher_infra.add_shape(shape)
        for shape in adv_gen.sidewalks:
            batcher_infra.add_shape(shape)
        # Don't forget the parks if you want them!
        for shape in getattr(adv_gen, 'parks', []):
             # Make parks green
             import random # simplified color for now
             batcher_infra.add_shape(shape) 
            
        city_mesh_obj = batcher_infra.build(Material())
        if city_mesh_obj:
            glrenderer.addObject(city_mesh_obj)
            current_objects.append(city_mesh_obj)

        # Batch 2: Buildings (FROM BSP)
        print("Batching Buildings (BSP)...")
        batcher_bldg = MeshBatcher()
        
        # Use adv_gen.buildings instead of city_gen.buildings
        for shape in adv_gen.buildings:
             # BSP buildings usually have colors baked in or need random assignment
             # If shape.colors is empty, the batcher might complain or render black.
             # AdvancedCityGenerator usually handles this.
            batcher_bldg.add_shape(shape)
            
        building_mesh_obj = batcher_bldg.build(Material())
        if building_mesh_obj:
            current_objects.append(building_mesh_obj)
            if show_buildings[0]:
                glrenderer.addObject(building_mesh_obj)
            
        # 4. Generate Debug Traffic Lines (Graph)
        print("Generating Traffic Debug...")
        # Use the tuned values we discussed (width * 0.15)
        debug_shape = mesh_gen.generate_traffic_debug(city_gen.graph)
        
        if len(debug_shape.vertices) > 0:
            # High visibility material (Unlit / High Ambient)
            debug_mat = Material()
            debug_mat.ambient_strength = 1.0 # Max brightness regardless of light angle
            debug_mat.diffuse_strength = 0.0 # Ignore directional shading
            debug_mat.specular_strength = 0.0
            
            debug_mesh_obj = MeshObject(debug_shape, debug_mat)
            debug_mesh_obj.draw_mode = gl.GL_LINES 
            glrenderer.addObject(debug_mesh_obj)
            current_objects.append(debug_mesh_obj)
        
        print(f"Done. Nodes: {len(city_gen.graph.nodes)}, Edges: {len(city_gen.graph.edges)}")
            
    # Initial Gen
    regenerate()

    # Main Loop
    while not glfw.window_should_close(window.window):
        impl.process_inputs()
        camera.update(0.016)
        
        # Handle Toggle Logic (State Sync)
        if building_mesh_obj:
            is_in_renderer = building_mesh_obj in glrenderer.objects
            if show_buildings[0] and not is_in_renderer:
                glrenderer.addObject(building_mesh_obj)
            elif not show_buildings[0] and is_in_renderer:
                glrenderer.objects.remove(building_mesh_obj)
        
        glrenderer.render()
        
        # GUI
        imgui.new_frame()
        imgui.begin("City Controls")
        
        if imgui.button("Regenerate"):
            regenerate()
            
        _, show_buildings[0] = imgui.checkbox("Show Buildings", show_buildings[0])
            
        imgui.text(f"Nodes: {len(city_gen.graph.nodes)}")
        imgui.text(f"Edges: {len(city_gen.graph.edges)}")
        imgui.text("Green = Forward Lane")
        imgui.text("Red = Backward Lane")
            
        imgui.end()
        imgui.render()
        impl.render(imgui.get_draw_data())
        
        glfw.swap_buffers(window.window)
        glfw.poll_events()
        
    window.delete()
    glfw.terminate()

if __name__ == "__main__":
    main()