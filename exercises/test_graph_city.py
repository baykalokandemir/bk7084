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
from framework.utils.car_agent import CarAgent
from framework.shapes.cube import Cube
import random
from framework.camera import Flycamera
from framework.light import PointLight
import OpenGL.GL as gl

import glfw
import glm
import imgui
from framework.utils.ui_manager import UIManager
from framework.utils.holograms_3d import Holograms3D, HologramConfig

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

    # ImGui Setup & UIManager
    ui_manager = UIManager(window.window)
    ui_manager.setup_input_chaining(window)

    # City Generation State
    city_gen = CityGenerator()
    mesh_gen = MeshGenerator()
    
    # Toggle State
    show_buildings = [False] 
    crash_debug = [False] # Changed to list for mutability in nested func
    print_stuck_debug = [False]
    print_despawn_debug = [False]

    # Store explicit references
    current_objects = []
    city_mesh_obj = None
    building_mesh_obj = None
    debug_mesh_obj = None
    signal_mesh_obj = None 
    crash_shape = None 

    # [NEW] Hologram State
    holograms = [] # List of Holograms3D instances
    hologram_configs = [] # List of HologramConfig instances
    target_hologram_count = [5] # UI Slider State
    
    # [NEW] Agent State
    agents = []
    target_agent_count = [1] 
    num_cars_to_brake = [5] 
    reckless_chance = [0.2] 
    crash_events = [] 
    total_crashes = [0] 

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
            total_crashes[0] += 1
            if (crash_debug[0]):
                print(f"DEBUG: [Car {a1.id}] crashed into [Car {a2.id}] at {midpoint}.")

    def regenerate_holograms():
        """Generates random holograms."""
        nonlocal holograms, hologram_configs
        
        # Clear existing
        for holo in holograms:
            for obj in holo.objects:
                if obj in glrenderer.objects:
                    glrenderer.objects.remove(obj)
        holograms = []
        hologram_configs = []
        
        print(f"Generating {target_hologram_count[0]} holograms...")
        
        for i in range(target_hologram_count[0]):
             # Random Pos with Spacing Check
             pos = glm.vec3(0, 40.0, 0)
             valid = False
             for attempt in range(10):
                 rx = random.uniform(-180, 180)
                 rz = random.uniform(-180, 180)
                 candidate = glm.vec3(rx, 40.0, rz)
                 
                 # Check distance to existing
                 too_close = False
                 for h in holograms:
                     if glm.distance(candidate, h.root_position) < 80.0:
                         too_close = True
                         break
                 
                 if not too_close:
                     pos = candidate
                     valid = True
                     break
            
             if not valid:
                 # Fallback to random if crowded
                 pos = glm.vec3(random.uniform(-180, 180), 40.0, random.uniform(-180, 180))
             
             # Create Config
             cfg = HologramConfig()
             cfg.L_ITERATIONS = 2
             cfg.L_SIZE_LIMIT = random.randint(3, 15) # Random size complexity
             
             # Random Color
             # Neon Palette (0-255)
             palette = [
                 (0, 240, 255),  # Cyan
                 (116, 238, 21),  # Lime
                 (255, 231, 0),   # Yellow
                 (240, 0, 255),   # Magenta
                 (245, 39, 137)   # Pink
             ]
             choice = random.choice(palette)
             # Normalize (0-1) and Boost (x3.0) for glow
             rgb = [(c / 255.0) * 3.0 for c in choice]
             cfg.POINT_CLOUD_COLOR = list(rgb)
             
             # Random Render Mode
             if random.random() < 0.5:
                 cfg.USE_POINT_CLOUD = True
             else:
                 cfg.USE_POINT_CLOUD = False
                 # Random Slice Params
                 cfg.SLICE_NORMAL = [random.random(), random.random(), random.random()]
                 cfg.SLICE_SPEED = random.uniform(0.05, 0.2)
             
             # Create Logic
             holo = Holograms3D(root_position=pos, scale=5.0)
             holo.regenerate(cfg)
             
             # Register Objects
             for obj in holo.objects:
                 glrenderer.addObject(obj)
                 
             holograms.append(holo)
             hologram_configs.append(cfg)

    def regenerate():
        nonlocal current_objects, city_mesh_obj, building_mesh_obj, debug_mesh_obj, signal_mesh_obj, agents, city_gen, crash_shape, holograms, hologram_configs
        
        # Clear old objects
        for obj in current_objects:
            if obj in glrenderer.objects:
                glrenderer.objects.remove(obj)
        current_objects = []
        city_mesh_obj = None
        building_mesh_obj = None
        debug_mesh_obj = None
        signal_mesh_obj = None
        crash_events[:] = [] # Clear list in place
        total_crashes[0] = 0
        
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
        adv_gen = AdvancedCityGenerator(width=400, depth=400)
        adv_gen.generate()
        
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

        print("Batching Buildings (BSP)...")
        batcher_bldg = MeshBatcher()
        for shape in adv_gen.buildings: batcher_bldg.add_shape(shape)
            
        building_mesh_obj = batcher_bldg.build(Material())
        if building_mesh_obj:
            current_objects.append(building_mesh_obj)
            if show_buildings[0]:
                glrenderer.addObject(building_mesh_obj)
            
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
        
        print(f"Done. Nodes: {len(city_gen.graph.nodes)}, Edges: {len(city_gen.graph.edges)}")

    def draw_ui():
        """Captured UI logic"""
        imgui.begin("City Controls")
        
        if imgui.button("Regenerate"):
            regenerate()
            
        imgui.text(f"Total Crashes: {total_crashes[0]}")
            
        _, num_cars_to_brake[0] = imgui.input_int("Num to Brake", num_cars_to_brake[0])
        if imgui.button("Brake Random Cars"):
            count = min(num_cars_to_brake[0], len(agents))
            if count > 0:
                candidates = [a for a in agents if not a.manual_brake and not a.is_reckless]
                targets = candidates if len(candidates) < count else random.sample(candidates, count)
                for t in targets: t.manual_brake = True
                print(f"[USER] Manually braked {len(targets)} cars.")
        
        if imgui.button("Release All"):
            for a in agents: a.manual_brake = False
            print("[USER] Released all manual brakes.")
            
        _, reckless_chance[0] = imgui.slider_float("Reckless %", reckless_chance[0], 0.0, 1.0)
        
        if imgui.button("Clear Wrecks"):
             to_remove = [obj for obj in current_objects if obj.mesh == crash_shape]
             for obj in to_remove:
                 if obj in glrenderer.objects: glrenderer.objects.remove(obj)
                 current_objects.remove(obj)
             print(f"[USER] Cleared {len(to_remove)} wrecks.")

        _, target_agent_count[0] = imgui.slider_int("Car Count", target_agent_count[0], 0, 50)
        
        imgui.separator()
        imgui.text("Holograms")
        changed, target_hologram_count[0] = imgui.slider_int("Num Holograms", target_hologram_count[0], 0, 20)
        if changed or imgui.button("Regenerate Holograms"):
            regenerate_holograms()
            
        imgui.separator()
            
        _, show_buildings[0] = imgui.checkbox("Show Buildings", show_buildings[0])
        _, crash_debug[0] = imgui.checkbox("Crash Debug", crash_debug[0])
        _, print_stuck_debug[0] = imgui.checkbox("Print Stuck Debug", print_stuck_debug[0])
        _, print_despawn_debug[0] = imgui.checkbox("Print Despawn Debug", print_despawn_debug[0])
            
        imgui.text(f"Nodes: {len(city_gen.graph.nodes)}")
        imgui.text(f"Edges: {len(city_gen.graph.edges)}")
        imgui.text("Green = Forward Lane")
        imgui.text("Red = Backward Lane")
        imgui.end()

    # Initial Gen
    regenerate()
    regenerate_holograms() # [NEW]

    # Main Loop
    while not glfw.window_should_close(window.window):
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
                    is_reckless = (random.random() < reckless_chance[0])
                    ag = CarAgent(lane, is_reckless=is_reckless)
                    agents.append(ag)
                    glrenderer.addObject(ag.mesh_object)
        
        # 2. Update Simulation
        for node in city_gen.graph.nodes:
            node.update(0.016)
        for agent in agents:
            agent.update(0.016, print_stuck_debug[0], print_despawn_debug[0])
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
            
        # Update Holograms
        for i, holo in enumerate(holograms):
            holo.update(0.016)
            holo.update_uniforms(hologram_configs[i], glfw.get_time())
            
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
        alive_agents = []
        for agent in agents:
            if agent.alive:
                alive_agents.append(agent)
            else:
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
        ui_manager.render(draw_ui)
        
        glfw.swap_buffers(window.window)
        glfw.poll_events()
        
    ui_manager.shutdown()
    window.delete()
    glfw.terminate()

if __name__ == "__main__":
    main()