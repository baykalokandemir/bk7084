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
from framework.utils.mesh_generator import MeshGenerator
from framework.utils.mesh_batcher import MeshBatcher
from framework.utils.car_agent import CarAgent
from framework.shapes.cube import Cube # [NEW]
import random
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

    # [NEW] Agent State
    agents = []
    target_agent_count = [1] # List for ImGui (mutable)

    def regenerate():
        nonlocal current_objects, city_mesh_obj, building_mesh_obj, debug_mesh_obj, agents, city_gen
        
        # Clear old objects
        for obj in current_objects:
            if obj in glrenderer.objects:
                glrenderer.objects.remove(obj)
        current_objects = []
        city_mesh_obj = None
        building_mesh_obj = None
        debug_mesh_obj = None

        # Clear Agents
        for agent in agents:
            if agent.mesh_object in glrenderer.objects:
                glrenderer.objects.remove(agent.mesh_object)
        agents = []
        
        # Reset Generators (Clean State)
        city_gen = CityGenerator() # [NEW] Fresh instance to wipe graph
        
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
        
        # 5. [NEW] Visualize Auditor Failures (Red Cubes)
        if hasattr(city_gen, 'dead_end_lanes') and city_gen.dead_end_lanes:
            batcher_fails = MeshBatcher()
            
            # Create a localized Cube shape once
            fail_cube = Cube(color=glm.vec4(1.0, 1.0, 0.0, 0.4), side_length=3.0)
            fail_cube.createGeometry()
            
            # We must manually transform and add to batcher?
            # Batcher expects 'shapes'.
            # A Shape stores vertices in local space usually, but Batcher merges them.
            # If we want 50 cubes at different positions, we need 50 Shape objects with baked positions,
            # OR we reuse the same shape but modify vertices? The Batcher reads vertices.
            
            # Easiest: Create a new Cube shape for each failure, or modify vertices.
            # Let's just create new Cube objects. It's initialization time, so fine.
            
            for lane in city_gen.dead_end_lanes:
                 if lane.waypoints:
                     p = lane.waypoints[-1]
                     # Make a cube at p
                     c = Cube(color=glm.vec4(1.0, 1.0, 0.0, 0.8), side_length=3.0)
                     c.createGeometry()
                     
                     # Translate vertices manually to p
                     offset = glm.vec3(p.x, 1.0, p.z) # Lift slightly
                     
                     # Dirty hack: Modify c.vertices in place?
                     # c.vertices is numpy array [ [x,y,z,w], ... ]
                     # We can just add offset.
                     # But numpy addition needs broadcasing.
                     
                     # shape.translate? Not implemented?
                     # Let's do manual loop or numpy add.
                     # c.vertices[:, 0] += offset.x
                     # c.vertices[:, 1] += offset.y
                     # c.vertices[:, 2] += offset.z
                     
                     c.vertices[:, 0] += offset.x
                     c.vertices[:, 1] += offset.y
                     c.vertices[:, 2] += offset.z
                     
                     batcher_fails.add_shape(c)
            
            fail_mesh = batcher_fails.build(Material())
            # Unlit Red
            fail_mesh.material.uniforms = {"ambientStrength": 1.0}
            
            glrenderer.addObject(fail_mesh)
            current_objects.append(fail_mesh)
        
        print(f"Done. Nodes: {len(city_gen.graph.nodes)}, Edges: {len(city_gen.graph.edges)}")
            
    # Initial Gen
    regenerate()

    # Main Loop
    while not glfw.window_should_close(window.window):
        impl.process_inputs()
        camera.update(0.016)
        
        # --- Traffic Simulation ---
        # 1. Spawn / Despawn
        while len(agents) > target_agent_count[0]:
            removed = agents.pop()
            if removed.mesh_object in glrenderer.objects:
                glrenderer.objects.remove(removed.mesh_object)
        
        if len(agents) < target_agent_count[0]:
            if city_gen.graph.edges:
                edge = random.choice(city_gen.graph.edges)
                if hasattr(edge, 'lanes') and edge.lanes:
                    lane = random.choice(edge.lanes)
                    ag = CarAgent(lane)
                    
                    # Random color tweak?
                    # ag.mesh_object.material.uniforms['color'] = ... (Need shader support)
                    
                    agents.append(ag)
                    glrenderer.addObject(ag.mesh_object)
        
        # 2. Update Agents
        for agent in agents:
            agent.update(0.016)
            
        # 3. Cleanup Dead Agents
        # Iterate copy or use list comprehension to filter
        alive_agents = []
        for agent in agents:
            if agent.alive:
                alive_agents.append(agent)
            else:
                # Remove from renderer
                if agent.mesh_object in glrenderer.objects:
                    glrenderer.objects.remove(agent.mesh_object)
        agents = alive_agents
        
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
        
        # [NEW] Debug Render
        # Ideally render debug AFTER main render to draw on top, but depth test handles it.
        # CarAgent uses immediate draw call on a mesh object.
        for agent in agents:
            agent.render_debug(glrenderer, camera)
            
        if imgui.button("Regenerate"):
            regenerate()
            
        _, target_agent_count[0] = imgui.slider_int("Car Count", target_agent_count[0], 0, 50)
        imgui.separator()
            
        _, show_buildings[0] = imgui.checkbox("Show Buildings", show_buildings[0])
            
        imgui.text(f"Nodes: {len(city_gen.graph.nodes)}")
        imgui.text(f"Edges: {len(city_gen.graph.edges)}")
        imgui.text("Green = Forward Lane")
        imgui.text("Red = Backward Lane")
            
        imgui.end()
        imgui.render()
        impl.render(imgui.get_draw_data())
        
        glfw.swap_buffers(window.window)fdsagasdgdsaf
        glfw.poll_events()
        
    window.delete()
    glfw.terminate()

if __name__ == "__main__":
    main()