import os
import random
import glm
import OpenGL.GL as gl
from framework.utils.city_generator import CityGenerator
from framework.utils.advanced_city_generator import AdvancedCityGenerator
from framework.utils.mesh_generator import MeshGenerator
from framework.utils.mesh_batcher import MeshBatcher
from framework.utils.car_agent import CarAgent
from framework.utils.crash_cluster import CrashCluster
from framework.shapes.cube import Cube
from framework.objects import MeshObject
from framework.materials import Material, Texture

# Car Imports
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

class CityManager:
    def __init__(self, renderer, texture_dir=None):
        self.renderer = renderer
        
        if texture_dir is None:
            # Auto-detect: ../assets/building_textures relative to this file
            self.texture_dir = os.path.join(os.path.dirname(__file__), "..", "assets", "building_textures")
        else:
            self.texture_dir = texture_dir
            
        self.city_gen = CityGenerator()
        self.mesh_gen = MeshGenerator()
        
        self.agents = []
        self.crash_events = []
        
        # Rendering State
        self.static_objects = []
        self.building_meshes = []
        self.signal_mesh = None
        self.crash_meshes = []
        self.crash_clusters = [] # [NEW] Track persistent crash clusters
        
        # Optimization: Shared Crash Shape
        self.crash_shape = Cube(side_length=2.5, color=glm.vec4(1.0, 0.0, 0.0, 1.0))
        self.crash_shape.createGeometry()
        
        self.found_textures = self._scan_textures()
        
    def _scan_textures(self):
        found = []
        if os.path.exists(self.texture_dir):
            found = [f for f in os.listdir(self.texture_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        return found
        
    @staticmethod
    def get_car_shape_by_name(name):
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
        
        mapping = {
            "Ambulance": Ambulance, "Bus": Bus, "CyberpunkCar": CyberpunkCar,
            "Pickup": Pickup, "PoliceCar": PoliceCar, "Sedan": Sedan,
            "SUV": SUV, "Tank": Tank, "Truck": Truck, "Van": Van
        }
        if name in mapping:
            s = mapping[name]()
            return s
            
        # Fallback to default Car instead of self.crash_shape
        from framework.shapes.cars.car import Car
        return Car()

    def clear_crashes(self):
        # 1. Remove wreck meshes from renderer
        for obj in self.crash_meshes:
            if obj in self.renderer.objects:
                self.renderer.objects.remove(obj)
        self.crash_meshes.clear()
        
        # 2. Clear clusters
        self.crash_clusters.clear()
        
        # 3. Remove crashed agents (Despawn them)
        # We need to filter self.agents to remove those with state="crashed"
        # But wait, self.agents currently holds them.
        self.agents = [a for a in self.agents if a.state != "crashed"]
        
        print(f"[CityManager] Cleared all crashes and despawned affected agents.")

    def regenerate_world(self, visuals, config, width=400, depth=400):
        self.regenerate(width, depth, self.found_textures, self.texture_dir)
        visuals.regenerate_clouds(15)
        visuals.regenerate_holograms(config.target_hologram_count)
    
    def regenerate(self, width, depth, texture_list, texture_dir):
        # Cleanup
        for obj in self.static_objects:
             if obj in self.renderer.objects: self.renderer.objects.remove(obj)
        self.static_objects = []
        
        for obj in self.building_meshes:
             if obj in self.renderer.objects: self.renderer.objects.remove(obj)
        self.building_meshes = []
        
        for a in self.agents:
            if a.mesh_object in self.renderer.objects: self.renderer.objects.remove(a.mesh_object)
        self.agents = []
        
        if self.signal_mesh and self.signal_mesh in self.renderer.objects:
            self.renderer.objects.remove(self.signal_mesh)
        self.signal_mesh = None
        
        for obj in self.crash_meshes:
            if obj in self.renderer.objects: self.renderer.objects.remove(obj)
        self.crash_meshes = []
        self.crash_clusters = [] # [NEW] Clear clusters
        
        # 1. Generate Layout
        print("Generating BSP Layout...")
        adv_gen = AdvancedCityGenerator(width=width, depth=depth)
        adv_gen.generate(texture_list=texture_list)
        
        # 2. Build Graph
        print("Building Traffic Graph...")
        self.city_gen.build_graph_from_layout(adv_gen)
        
        # 3. Batch Visuals
        self._batch_static_geometry(adv_gen, texture_list, texture_dir)
        
        # 4. Debug Lines
        print("Generating Traffic Debug...")
        debug_shape = self.mesh_gen.generate_traffic_debug(self.city_gen.graph)
        if len(debug_shape.vertices) > 0:
            debug_mat = Material()
            debug_mat.ambient_strength = 1.0 
            debug_mat.diffuse_strength = 0.0
            debug_mat.specular_strength = 0.0
            debug_mesh = MeshObject(debug_shape, debug_mat)
            debug_mesh.draw_mode = gl.GL_LINES 
            self.static_objects.append(debug_mesh)
            self.renderer.addObject(debug_mesh)
            
        # 5. Visualize Failures
        if hasattr(self.city_gen, 'dead_end_lanes') and self.city_gen.dead_end_lanes:
            self._batch_failures()
            
        print(f"City Generated. Nodes: {len(self.city_gen.graph.nodes)}, Edges: {len(self.city_gen.graph.edges)}")

    def _batch_static_geometry(self, adv_gen, texture_list, texture_dir):
        print("Batching Visuals (BSP)...")
        # Infra
        batcher_infra = MeshBatcher()
        for shape in adv_gen.roads: batcher_infra.add_shape(shape)
        for shape in adv_gen.sidewalks: batcher_infra.add_shape(shape)
        for shape in getattr(adv_gen, 'parks', []): batcher_infra.add_shape(shape) 
        
        city_mesh = batcher_infra.build(Material())
        if city_mesh: 
            self.static_objects.append(city_mesh)
            self.renderer.addObject(city_mesh) # Add immediately
        
        # Buildings
        print("Batching Buildings (BSP)...")
        texture_cache = {}
        batchers = {}
        self.building_meshes = [] # New list for buildings
        
        for t_name in texture_list:
            batchers[t_name] = MeshBatcher()
            path = os.path.join(texture_dir, t_name)
            if os.path.exists(path):
                texture_cache[t_name] = Texture(file_path=path)
        
        batchers["default"] = MeshBatcher()
        
        for shape in adv_gen.buildings:
            t_name = getattr(shape, 'texture_name', 'default')
            if t_name in batchers: batchers[t_name].add_shape(shape)
            else: batchers["default"].add_shape(shape)
            
        for t_name, batcher in batchers.items():
            if len(batcher.vertices) == 0: continue
            
            mat = Material()
            if t_name in texture_cache:
                mat = Material(color_texture=texture_cache[t_name])
                mat.specular_strength = 0.1
                mat.texture_scale = glm.vec2(1.0, 1.0)
            else:
                mat.specular_strength = 0.5
                
            mesh = batcher.build(mat)
            if mesh: 
                self.building_meshes.append(mesh)
                self.renderer.addObject(mesh) # Default show

    def _batch_failures(self):
        batcher = MeshBatcher()
        for lane in self.city_gen.dead_end_lanes:
             if lane.waypoints:
                 p = lane.waypoints[-1]
                 c = Cube(color=glm.vec4(1.0, 1.0, 0.0, 0.8), side_length=3.0)
                 c.createGeometry()
                 offset = glm.vec3(p.x, 1.0, p.z)
                 c.vertices[:, 0] += offset.x
                 c.vertices[:, 1] += offset.y
                 c.vertices[:, 2] += offset.z
                 batcher.add_shape(c)
        
        mesh = batcher.build(Material())
        mesh.material.uniforms = {"ambientStrength": 1.0}
        self.static_objects.append(mesh)
        self.renderer.addObject(mesh)

    def update(self, dt, config):
        # 1. Update Nodes
        for node in self.city_gen.graph.nodes:
            node.update(dt)
            
        # 2. Maintain Population
        car_types = [Ambulance, Bus, CyberpunkCar, Pickup, PoliceCar, Sedan, SUV, Tank, Truck, Van]
        self.maintain_population(config.target_agent_count, car_types, config.reckless_chance)
        
        # 3. Update Agents
        alive_agents = []
        for agent in self.agents:
             # Keep agents if they are driving OR crashed (don't remove crashed agents)
             if agent.state == "driving":
                 if agent.alive:
                     agent.update(dt, config.print_stuck_debug, config.print_despawn_debug)
                     alive_agents.append(agent)
                 else:
                     # Despawned normally
                     if agent.mesh_object in self.renderer.objects:
                         self.renderer.objects.remove(agent.mesh_object)
             elif agent.state == "crashed":
                 # Keep crashed agents in list but don't update them (they are static)
                 alive_agents.append(agent)
                 
        self.agents = alive_agents
        
        # 4. Signals
        self._update_signals()
        
        # 5. Crashes
        self.detect_crashes(config)
        self._update_crash_visuals()
        
        # 6. Building Visibility
        for mesh in self.building_meshes:
            is_in = mesh in self.renderer.objects
            if config.show_buildings and not is_in:
                self.renderer.addObject(mesh)
            elif not config.show_buildings and is_in:
                self.renderer.objects.remove(mesh)

    def maintain_population(self, target_count, car_types, reckless_chance):
        # Despawn excess
        while len(self.agents) > target_count:
            removed = self.agents.pop()
            if removed.mesh_object in self.renderer.objects:
                self.renderer.objects.remove(removed.mesh_object)
        
        # Spawn new
        if len(self.agents) < target_count:
            if self.city_gen.graph.edges:
                edge = random.choice(self.city_gen.graph.edges)
                if hasattr(edge, 'lanes') and edge.lanes:
                    lane = random.choice(edge.lanes)
                    
                    is_reckless = (random.random() < reckless_chance)
                    CarClass = random.choice(car_types)
                    car_shape = CarClass()
                    # car_shape.create_geometry() # init does this
                    
                    ag = CarAgent(lane, car_shape=car_shape, is_reckless=is_reckless)
                    self.agents.append(ag)
                    self.renderer.addObject(ag.mesh_object)

    def _update_signals(self):
        signal_shape = self.mesh_gen.generate_dynamic_signals(self.city_gen.graph)
        
        if self.signal_mesh:
             if self.signal_mesh in self.renderer.objects: self.renderer.objects.remove(self.signal_mesh)
             self.signal_mesh = None
             
        if len(signal_shape.vertices) > 0:
             mat = Material()
             mat.uniforms = {"ambientStrength": 1.0, "diffuseStrength": 0.0, "specularStrength": 0.0}
             self.signal_mesh = MeshObject(signal_shape, mat)
             self.signal_mesh.draw_mode = gl.GL_LINES
             self.renderer.addObject(self.signal_mesh)

    def _find_or_create_cluster(self, position, search_radius=8.0):
        # Find existing cluster nearby
        for cluster in self.crash_clusters:
            if glm.distance(position, cluster.center) < search_radius:
                return cluster
        
        # Create new if none found
        cluster = CrashCluster()
        cluster.center = position
        self.crash_clusters.append(cluster)
        return cluster

    def detect_crashes(self, config):
        # Spatial Hash
        spatial_grid = {}
        cell_size = 5.0
        
        for agent in self.agents:
            if agent.state == "crashed": continue # Ignore already crashed agents in detection
            if not agent.alive: continue
            
            # Check if hitting an EXISTING cluster
            # This enables N-way pile-ups where a driving car hits a wreck
            hit_cluster = None
            # Check if hitting an EXISTING cluster
            # This enables N-way pile-ups where a driving car hits a wreck
            hit_cluster = None
            for cluster in self.crash_clusters:
                # Use strict radius for hitting a pile (chain reaction)
                # Collision: distance < (cluster_radius + agent_radius) * overlap_factor
                # is_blocking(pos, margin) checks dist < radius + margin
                # So we want margin = agent.bounding_radius * 0.8 (some overlap)
                if cluster.is_blocking(agent.position, safety_margin=agent.bounding_radius * 0.8):
                     hit_cluster = cluster
                     break
            
            if hit_cluster:
                # Driving agent hit a cluster!
                agent.state = "crashed"
                
                midpoint = agent.position # Rough approx
                hit_cluster.add_agent(agent, midpoint)
                
                if agent.current_lane: agent.current_lane.crash_clusters.append(hit_cluster)
                if agent.mesh_object in self.renderer.objects: self.renderer.objects.remove(agent.mesh_object)
                
                config.total_crashes += 1
                
                if config.crash_report_debug:
                     count = len(hit_cluster.crashed_agents)
                     ids = ", ".join([str(a.id) for a in hit_cluster.crashed_agents])
                     print(f"[ACCIDENT] {count}-way car crash: cars {ids}")
                
                continue # Processed this agent
                
            gx = int(agent.position.x // cell_size)
            gz = int(agent.position.z // cell_size)
            key = (gx, gz)
            if key not in spatial_grid: spatial_grid[key] = []
            spatial_grid[key].append(agent)
            
        crashes = []
        for cell_agents in spatial_grid.values():
            if len(cell_agents) < 2: continue
            for i in range(len(cell_agents)):
                a1 = cell_agents[i]
                for j in range(i + 1, len(cell_agents)):
                    a2 = cell_agents[j]
                    dist = glm.distance(a1.position, a2.position)
                    
                    # Dynamic Collision Threshold
                    # Radii sum is the touching point. 
                    # We want a slight overlap for a crash (e.g. 0.9 factor) or just strict touch.
                    collision_dist = (a1.bounding_radius + a2.bounding_radius) * 0.9
                    
                    if dist < collision_dist:
                        # Collision!
                        if self._should_ignore_collision(a1, a2): continue
                        crashes.append((a1, a2))
                        
        for a1, a2 in crashes:
            if a1.state == "crashed" or a2.state == "crashed": continue
            
            # Midpoint
            midpoint = (a1.position + a2.position) * 0.5
            
            # 1. Update State
            a1.state = "crashed"
            a2.state = "crashed"
            
            # 2. Add to Cluster
            cluster = self._find_or_create_cluster(midpoint)
            
            cluster.add_agent(a1, midpoint)
            cluster.add_agent(a2, midpoint)
            
            # 3. Register with Lanes
            if a1.current_lane: a1.current_lane.crash_clusters.append(cluster)
            if a2.current_lane: a2.current_lane.crash_clusters.append(cluster)
            
            # 4. Remove original meshes
            if a1.mesh_object in self.renderer.objects: self.renderer.objects.remove(a1.mesh_object)
            if a2.mesh_object in self.renderer.objects: self.renderer.objects.remove(a2.mesh_object)
            
            config.total_crashes += 1
            if config.crash_debug:
                print(f"DEBUG: [Car {a1.id}] crashed into [Car {a2.id}]. Cluster ID: {cluster.id}")
                
            if config.crash_report_debug:
                 count = len(cluster.crashed_agents)
                 ids = ", ".join([str(a.id) for a in cluster.crashed_agents])
                 print(f"[ACCIDENT] {count}-way car crash: cars {ids}")

    def _should_ignore_collision(self, a1, a2):
        if a1.current_lane and a2.current_lane and a1.current_lane != a2.current_lane:
             if hasattr(a1.current_lane, 'parent_edge') and hasattr(a2.current_lane, 'parent_edge'):
                 if a1.current_lane.parent_edge == a2.current_lane.parent_edge:
                     return True
        return False

    def _update_crash_visuals(self):
        # Sync Cluster Meshes with Renderer
        for cluster in self.crash_clusters:
            for obj in cluster.get_renderables():
                if obj not in self.renderer.objects:
                    self.renderer.addObject(obj)
                    self.crash_meshes.append(obj) # Keep tracking for manual clear logic if needed

    def get_static_meshes(self):
        return self.static_objects
    
    def get_agent_meshes(self):
        return [a.mesh_object for a in self.agents]
    
    def get_limit_meshes(self, show_buildings):
        # Logic for toggling buildings
        # This is strictly visual, maybe should be in external logic
        # But we hold the objects.
        # Let's let the caller handle toggling by iterating static_objects
        pass 
