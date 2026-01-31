# Refactored version - work in progress
import os
import sys

# Add framework to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from framework.window import OpenGLWindow
from framework.renderer import GLRenderer
from framework.objects import MeshObject
from framework.materials import Material, Texture
from framework.utils.city_generator import CityGenerator
from framework.utils.advanced_city_generator import AdvancedCityGenerator
from framework.utils.mesh_generator import MeshGenerator
from framework.utils.mesh_batcher import MeshBatcher
from framework.utils.car_agent import CarAgent
from framework.shapes.cube import Cube 
from framework.objects.skybox import Skybox
from framework.objects.cloud import Cloud

import random
from framework.camera import Flycamera
import OpenGL.GL as gl
from framework.shapes.cars.ambulance import Ambulance
from framework.shapes.cars.bus import Bus
from framework.shapes.cars.cyberpunk_car import CyberpunkCar
from framework.shapes.cars.pickup import Pickup
from framework.shapes.cars.policecar import PoliceCar
from framework.shapes.cars.sedan import Sedan
from framework.shapes.cars.suv import SUV
from framework.shapes.cars.tank import Tank
from framework.shapes.cars.truck import Truck
from framework.shapes.cars.van import Van

import glfw
import glm
import imgui
from framework.utils.ui_manager import UIManager
from exercises.components.simulation_state import SimulationState
from exercises.components.city_ui import CityUI
from exercises.components.city_visuals import CityVisuals

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
    
    
    # [NEW] Visuals Component (manages Skybox, Clouds, Holograms)
    visuals = CityVisuals(glrenderer)
    glrenderer.addObject(visuals.skybox)
    glrenderer.addLight(visuals.skybox.sun_light)
    glrenderer.addLight(visuals.skybox.moon_light)

    # ImGui Setup & UIManager
    ui_manager = UIManager(window.window)
    ui_manager.setup_input_chaining(window)

    # City Generation State
    city_gen = CityGenerator()
    mesh_gen = MeshGenerator()
    
    # [NEW] Simulation State
    config = SimulationState()

    # Store explicit references
    current_objects = []
    city_mesh_obj = None
    building_mesh_objs = [] # List of MeshObjects (one per texture)
    debug_mesh_obj = None
    signal_mesh_obj = None 
    crash_shape = None 

    # [NEW] Agent State
    agents = []
    crash_events = []


    # [NEW] Camera Tracking State
    tracking_state = {
        "is_tracking": False, 
        "target_id": 0,
        "found": False # Feedback for GUI
    }

    # [NEW] UI Component
    ui = CityUI(config)

    def detect_crashes(active_agents):
        """
        Phase 3: Spatial Hash Collision Detection
        Complexity: O(N) instead of O(N^2)
        """
        spatial_grid = {}
        cell_size = 5.0
        
        # 1. Bucket Phase
        for agent in active_agents:
            if not agent.alive: continue
            gx = int(agent.position.x // cell_size)
            gz = int(agent.position.z // cell_size)
            key = (gx, gz)
            if key not in spatial_grid: spatial_grid[key] = []
            spatial_grid[key].append(agent)
            
        # 2. Check Phase
        crashes = []
        for key, cell_agents in spatial_grid.items():
            if len(cell_agents) < 2: continue
            for i in range(len(cell_agents)):
                a1 = cell_agents[i]
                if not a1.alive: continue
                for j in range(i + 1, len(cell_agents)):
                    a2 = cell_agents[j]
                    if not a2.alive: continue
                    dist = glm.distance(a1.position, a2.position)
                    if dist < 2.5: 
                        if a1.current_lane and a2.current_lane and a1.current_lane != a2.current_lane:
                            if hasattr(a1.current_lane, 'parent_edge') and hasattr(a2.current_lane, 'parent_edge'):
                                if a1.current_lane.parent_edge == a2.current_lane.parent_edge:
                                    continue 
                        crashes.append((a1, a2))
        
        # 3. Resolve
        for a1, a2 in crashes:
            if not a1.alive or not a2.alive: continue 
            a1.alive = False
            a2.alive = False
            midpoint = (a1.position + a2.position) * 0.5
            crash_events.append(midpoint)
            config.total_crashes += 1
            config.total_crashes += 1
            if (config.crash_debug):
                print(f"DEBUG: [Car {a1.id}] crashed into [Car {a2.id}] at {midpoint}.")



    def regenerate():
        nonlocal current_objects, city_mesh_obj, building_mesh_objs, debug_mesh_obj, signal_mesh_obj, agents, city_gen, crash_shape
        
        # Clear old objects
        for obj in current_objects:
            if obj in glrenderer.objects:
                glrenderer.objects.remove(obj)
        current_objects = []
        city_mesh_obj = None
        building_mesh_objs = []
        debug_mesh_obj = None
        signal_mesh_obj = None
        signal_mesh_obj = None
        # clouds and holograms managed by visuals component
        crash_events[:] = [] # Clear list in place
        config.total_crashes = 0
        
        # Clear Crash Visuals
        to_remove = [obj for obj in glrenderer.objects if obj.mesh == crash_shape]
        for obj in to_remove:
             glrenderer.objects.remove(obj)

        # Clear Agents
        for agent in agents:
            if agent.mesh_object in glrenderer.objects:
                glrenderer.objects.remove(agent.mesh_object)
        agents = []
        
        # Reset Generators
        city_gen = CityGenerator()
        
        # 1. Generate BSP Layout
        print("Generating BSP Layout...")
        
        # Scan for textures
        texture_dir = os.path.join(os.path.dirname(__file__), "assets", "building_textures")
        found_textures = []
        if os.path.exists(texture_dir):
            for f in os.listdir(texture_dir):
                if f.lower().endswith(('.png', '.jpg', '.jpeg')):
                    found_textures.append(f)
        else:
            print(f"Warning: Texture directory {texture_dir} not found.")

        adv_gen = AdvancedCityGenerator(width=400, depth=400)
        adv_gen.generate(texture_list=found_textures)
        
        # 2. Build Traffic Graph
        print("Building Traffic Graph...")
        city_gen.build_graph_from_layout(adv_gen)
        
        # 3. Batch Visuals (BSP)
        print("Batching Visuals (BSP)...")
        batcher_infra = MeshBatcher()
        for shape in adv_gen.roads: batcher_infra.add_shape(shape)
        for shape in adv_gen.sidewalks: batcher_infra.add_shape(shape)
        for shape in getattr(adv_gen, 'parks', []): batcher_infra.add_shape(shape) 
            
        city_mesh_obj = batcher_infra.build(Material())
        if city_mesh_obj:
            glrenderer.addObject(city_mesh_obj)
            current_objects.append(city_mesh_obj)

        # Batch 2: Buildings (FROM BSP) - Multi-Texture Support
        print("Batching Buildings (BSP)...")
        
        texture_files = found_textures # Use the list we found earlier
        texture_cache = {}
        batchers = {}
        
        # Init Batchers and Load Textures
        for t_name in texture_files:
            batchers[t_name] = MeshBatcher()
            # Load Texture
            path = os.path.join(texture_dir, t_name) # Use texture_dir
            if os.path.exists(path):
                texture_cache[t_name] = Texture(file_path=path)
            else:
                print(f"Warning: Texture {path} not found.")
                
        # Fallback batcher for no texture
        batchers["default"] = MeshBatcher()
        
        # Distribute Shapes
        for shape in adv_gen.buildings:
            t_name = getattr(shape, 'texture_name', 'default')
            if t_name in batchers:
                batchers[t_name].add_shape(shape)
            else:
                batchers["default"].add_shape(shape)
                
        # Build Meshes
        for t_name, batcher in batchers.items():
            if len(batcher.vertices) == 0: continue
            
            mat = Material()
            if t_name in texture_cache:
                mat = Material(color_texture=texture_cache[t_name])
                mat.specular_strength = 0.1 # Bricks aren't very shiny
                mat.texture_scale = glm.vec2(1.0, 1.0) # UVs are already scaled in building.py
            else:
                mat.specular_strength = 0.5
                
            mesh_obj = batcher.build(mat)
            if mesh_obj:
                building_mesh_objs.append(mesh_obj)
                current_objects.append(mesh_obj)
                if config.show_buildings:
                    glrenderer.addObject(mesh_obj)
            
        # 4. Generate Debug Traffic Lines
        print("Generating Traffic Debug...")
        debug_shape = mesh_gen.generate_traffic_debug(city_gen.graph)
        if len(debug_shape.vertices) > 0:
            debug_mat = Material()
            debug_mat.ambient_strength = 1.0 
            debug_mat.diffuse_strength = 0.0
            debug_mat.specular_strength = 0.0
            debug_mesh_obj = MeshObject(debug_shape, debug_mat)
            debug_mesh_obj.draw_mode = gl.GL_LINES 
            glrenderer.addObject(debug_mesh_obj)
            current_objects.append(debug_mesh_obj)
        
        # Optimization: Shared Crash Shape
        crash_shape = Cube(side_length=2.5, color=glm.vec4(1.0, 0.0, 0.0, 1.0))
        crash_shape.createGeometry()
        
        # 5. Visualize Auditor Failures
        if hasattr(city_gen, 'dead_end_lanes') and city_gen.dead_end_lanes:
            batcher_fails = MeshBatcher()
            for lane in city_gen.dead_end_lanes:
                 if lane.waypoints:
                     p = lane.waypoints[-1]
                     c = Cube(color=glm.vec4(1.0, 1.0, 0.0, 0.8), side_length=3.0)
                     c.createGeometry()
                     offset = glm.vec3(p.x, 1.0, p.z)
                     c.vertices[:, 0] += offset.x
                     c.vertices[:, 1] += offset.y
                     c.vertices[:, 2] += offset.z
                     batcher_fails.add_shape(c)
            
            fail_mesh = batcher_fails.build(Material())
            fail_mesh.material.uniforms = {"ambientStrength": 1.0}
            glrenderer.addObject(fail_mesh)
            current_objects.append(fail_mesh)
        
        # 6. [NEW] Generate Random Clouds
        visuals.regenerate_clouds(15)

        print(f"Done. Nodes: {len(city_gen.graph.nodes)}, Edges: {len(city_gen.graph.edges)}")



    # Initial Gen
    regenerate()
    visuals.regenerate_holograms(config.target_hologram_count)

    # Main Loop
    while not glfw.window_should_close(window.window):
        
        # Camera Update Logic
        if not tracking_state["is_tracking"]:
            camera.update(0.016)
        else:
            # Tracking Mode
            target_agent = None
            for a in agents:
                if a.id == tracking_state["target_id"]:
                    target_agent = a
                    break
            
            tracking_state["found"] = (target_agent is not None)
            
            if target_agent:
                # Third Person View: Behind and above
                # orientation is normalized forward vector
                offset_dist = 15.0
                height_offset = 6.0
                
                # Position: Target - (Fwd * Dist) + Up
                desired_pos = target_agent.position - (target_agent.orientation * offset_dist) + glm.vec3(0, height_offset, 0)
                camera.position = desired_pos
                
                # Look At Target (slightly above center to see road)
                look_target = target_agent.position + glm.vec3(0, 2.0, 0)
                camera.front = glm.normalize(look_target - camera.position)
                
                # Update View Matrix directly
                camera.updateView()
                
                # Sync Euler Angles to prevent snapping when tracking ends
                # Pitch (X) - clamp to avoid singularity
                pitch_rad = glm.asin(max(min(camera.front.y, 1.0), -1.0)) 
                camera.euler_angles.x = glm.degrees(pitch_rad)
                
                # Yaw (Y)
                # atan2(z, x) corresponds to the standard mapping used in Flycamera
                camera.euler_angles.y = glm.degrees(glm.atan(camera.front.z, camera.front.x))
        
        # --- Traffic Simulation ---
        # 1. Spawn / Despawn
        while len(agents) > config.target_agent_count:
            removed = agents.pop()
            if removed.mesh_object in glrenderer.objects:
                glrenderer.objects.remove(removed.mesh_object)
        
        if len(agents) < config.target_agent_count:
            if city_gen.graph.edges:
                edge = random.choice(city_gen.graph.edges)
                if hasattr(edge, 'lanes') and edge.lanes:
                    lane = random.choice(edge.lanes)
                    
                    is_reckless = (random.random() < config.reckless_chance)
                    car_types = [
                        Ambulance, Bus, CyberpunkCar, Pickup, PoliceCar, 
                        Sedan, SUV, Tank, Truck, Van
                    ]
                    # Random Car Type
                    
                    CarClass = random.choice(car_types)
                    car_shape = CarClass()
                    car_shape.create_geometry() # BaseVehicle needs this? 
                    # Wait, BaseVehicle.create_geometry is called in its __init__?
                    # Let's check vehicle.py BaseVehicle.__init__ from previous read.
                    # Update: I read vehicle.py earlier. Init calls create_geometry. 
                    # So car_shape = CarClass() is enough.
                    
                    ag = CarAgent(lane, car_shape=car_shape, is_reckless=is_reckless)
                    
                    # Random color tweak logic removed as these cars have fixed mats
                    
                    agents.append(ag)
                    glrenderer.addObject(ag.mesh_object)
        
        # 2. Update Simulation
        for node in city_gen.graph.nodes:
            node.update(0.016)
        for agent in agents:
            agent.update(0.016, config.print_stuck_debug, config.print_despawn_debug)
            agent.render_debug(glrenderer, camera) # Debug Render
            
        # Phase 2: Render Dynamic Signals
        signal_shape = mesh_gen.generate_dynamic_signals(city_gen.graph)
        if signal_mesh_obj:
            if signal_mesh_obj in glrenderer.objects: glrenderer.objects.remove(signal_mesh_obj)
            if signal_mesh_obj in current_objects: current_objects.remove(signal_mesh_obj)
                
        if len(signal_shape.vertices) > 0:
            # Unlit material
            mat = Material()
            mat.uniforms = {"ambientStrength": 1.0, "diffuseStrength": 0.0, "specularStrength": 0.0}
            
            signal_mesh_obj = MeshObject(signal_shape, mat)
            signal_mesh_obj.draw_mode = gl.GL_LINES
            
            glrenderer.addObject(signal_mesh_obj)
            current_objects.append(signal_mesh_obj)
        else:
            signal_mesh_obj = None
            
        # Update Visuals
        visuals.update(0.016, glfw.get_time())
            
        # 3. Detect Crashes
        detect_crashes(agents)
        
        # Phase 4: Render Crashes
        if crash_events:
            for pos in crash_events:
                if crash_shape:
                    mat = Material()
                    mat.uniforms = {"ambientStrength": 1.0, "diffuseStrength": 0.0, "specularStrength": 0.0}
                    crash_obj = MeshObject(crash_shape, mat)
                    crash_obj.transform = glm.translate(pos)
                    glrenderer.addObject(crash_obj)
                    current_objects.append(crash_obj)
            crash_events.clear()
            
        # 4. Cleanup Dead Agents
        
        # [NEW] Skybox managed by visuals.update()

        # Iterate copy or use list comprehension to filter
        alive_agents = []
        for agent in agents:
            if agent.alive:
                alive_agents.append(agent)
            else:
                if agent.mesh_object in glrenderer.objects:
                    glrenderer.objects.remove(agent.mesh_object)
        agents = alive_agents
        
        # Handle Toggle Logic (State Sync)
        for b_obj in building_mesh_objs:
            is_in_renderer = b_obj in glrenderer.objects
            if config.show_buildings and not is_in_renderer:
                glrenderer.addObject(b_obj)
            elif not config.show_buildings and is_in_renderer:
                glrenderer.objects.remove(b_obj)

        # Sync Clouds
        for cloud in visuals.clouds:
             is_in = cloud.inst in glrenderer.objects
             if config.show_clouds and not is_in:
                 glrenderer.addObject(cloud.inst)
             elif not config.show_clouds and is_in:
                 glrenderer.objects.remove(cloud.inst)

        # Sync Holograms
        for holo in visuals.holograms:
            for obj in holo.objects:
                is_in = obj in glrenderer.objects
                if config.show_holograms and not is_in:
                    glrenderer.addObject(obj)
                elif not config.show_holograms and is_in:
                    glrenderer.objects.remove(obj)
        
        glrenderer.render()
        
        # GUI
        ui_manager.render(lambda: ui.draw(
            city_gen, agents, current_objects, glrenderer, crash_shape, 
            visuals.skybox, tracking_state, regenerate, 
            lambda: visuals.regenerate_holograms(config.target_hologram_count)
        ))
        
        # [NEW] Debug Render
        # Ideally render debug AFTER main render to draw on top, but depth test handles it.
        # CarAgent uses immediate draw call on a mesh object.
        for agent in agents:
            agent.render_debug(glrenderer, camera)
            
        glfw.swap_buffers(window.window)
        glfw.poll_events()
        
    ui_manager.shutdown()
    window.delete()
    glfw.terminate()

if __name__ == "__main__":
    main()
