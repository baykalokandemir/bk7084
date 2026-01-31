from pyglm import glm
import random
import math
from framework.objects.mesh_object import MeshObject
from framework.shapes.car import Car
from framework.shapes.uvsphere import UVSphere
from framework.materials.material import Material
from framework.utils.mesh_batcher import MeshBatcher

class CarAgent:

    debug_sphere_mesh = None
    _id_counter = 0 # Identity Persistence

    def __init__(self, start_lane, car_shape=None, is_reckless=False):
        self.id = CarAgent._id_counter
        CarAgent._id_counter += 1
        
        self.current_lane = start_lane
        self.register_on_lane(self.current_lane) # Register immediately
        self.current_curve = None # List of points if turning
        self.max_speed = 15.0
        self.speed = self.max_speed # Units/sec
        
        # Determine initial path
        self.path = self.current_lane.waypoints
        self.target_index = 0
        
        # Init Position
        if self.path:
            p = self.path[0]
            self.position = glm.vec3(p.x, p.y, p.z)
            self.target_index = 1
        else:
            self.position = glm.vec3(0, 0, 0)
            
        self.orientation = glm.vec3(0, 0, 1) # Default Fwd
        
        # Stuck Detection
        self.last_position = glm.vec3(self.position)
        self.time_since_last_move = 0.0
        self.alive = True # Signal for removal
        self.debug_stop_index = -1 # Stop at specific waypoint index
        self.manual_brake = False # Stopped via GUI
        self.blocked_by_id = None # To avoid spamming debug prints
        
        # Reckless Driver
        self.is_reckless = is_reckless

        # Visuals
        if car_shape is None:
            # Color Logic
            if self.is_reckless:
                # Orange for Reckless
                body_color = glm.vec4(1.0, 0.5, 0.0, 1.0)
            else:
                # Bright Yellow for Normal
                body_color = glm.vec4(1.0, 1.0, 0.0, 1.0)
                
            car_shape = Car(body_color=body_color)
            car_shape.createGeometry()
            
        # Determine if car_shape is a raw Geometry (Shape) or a Full Object (BaseVehicle)
        from framework.shapes.shape import Shape
        if isinstance(car_shape, Shape):
            # Already a single shape
            self.mesh_object = MeshObject(car_shape, Material())
        else:
            # It's a BaseVehicle with multiple parts - MERGE IT using MeshBatcher
            batcher = MeshBatcher()
            batcher.add_vehicle(car_shape)
            
            # Use appropriate material (body material as default)
            mat = car_shape.body_mat if hasattr(car_shape, 'body_mat') else Material()
            
            # Build returns MeshObject if material provided, Shape if not
            self.mesh_object = batcher.build(mat)
        
        # Init static debug mesh if needed
        if CarAgent.debug_sphere_mesh is None:
             sphere = UVSphere(radius=0.5, color=glm.vec4(1.0, 0.0, 1.0, 1.0)) # Magenta Target
             sphere.createGeometry()
             mat = Material()
             mat.uniforms = { "ambientStrength": 1.0, "diffuseStrength": 0.0, "specularStrength": 0.0 }
             CarAgent.debug_sphere_mesh = MeshObject(sphere, mat)

    def update(self, dt, print_stuck_debug=False, print_despawn_debug=False):
        if not self.alive: return # Don't update dead agents
        
        # Check if we should debug stop
        should_debug_stop = self.manual_brake or (self.debug_stop_index != -1 and self.target_index >= self.debug_stop_index)

        # Braking logic
        # Only check if we are on a lane
        blocked = False
        blocking_car_id = None

        # Reckless drivers IGNORE traffic (but still respect manual/debug stops)
        if self.current_lane and not self.is_reckless:
            # Check other agents on this lane
            for other in self.current_lane.active_agents:
                if other is self: continue
                if not other.alive: continue
                
                # If target_index is higher, they are ahead
                # If equal, check distance to that target
                is_ahead = False
                if other.target_index > self.target_index:
                    is_ahead = True
                elif other.target_index == self.target_index:
                    # Both aiming for same point. Who is closer?
                    d_me = glm.distance(self.position, self.path[self.target_index])
                    d_him = glm.distance(other.position, other.path[other.target_index])
                    if d_him < d_me:
                        is_ahead = True
                        
                if is_ahead:
                    dist = glm.distance(self.position, other.position)
                    if dist < 4.0: # [TUNING] Safety Distance
                        blocked = True
                        blocking_car_id = other.id
                        break
        
        if should_debug_stop:
             self.speed = 0.0
        else:
             # Combined Braking Logic
             
             # 1. Traffic Signal Check
             signal_stop = False
             
             # Only check signals if we are near the end of a lane (approaching intersection)
             if self.current_lane and self.path:
                 # Check distance to end of path (approx dist to node)
                 if self.target_index >= len(self.path) - 1:
                     dist_to_end = glm.distance(self.position, self.path[-1])
                     if dist_to_end < 15.0:
                         # Query Signal
                         node = self.current_lane.dest_node
                         signal = node.get_signal(self.current_lane.id)
                         
                         if signal == "RED":
                             if self.is_reckless and random.random() < 0.5:
                                 pass # Run it
                             else:
                                 signal_stop = True
                         elif signal == "YELLOW":
                             if self.is_reckless:
                                 self.speed = 25.0 # Speed up
                             else:
                                 signal_stop = True
             
             # 2. Apply Speed
             if signal_stop or blocked:
                 self.speed = 0.0
                 if blocked and self.blocked_by_id != blocking_car_id:
                     self.blocked_by_id = blocking_car_id
             else:
                 # Restore speed if not blocked and no red light
                 if not (self.is_reckless and self.speed > 20.0):
                     self.speed = self.max_speed
                 self.blocked_by_id = None

        # Stuck Check
        # Skip stuck check if we are intentionally stopped
        if not (should_debug_stop or signal_stop or blocked) and glm.distance(self.position, self.last_position) < 0.01:
            self.time_since_last_move += dt
            if self.time_since_last_move > 2.0:
                if (print_stuck_debug):
                    print(f"[ALERT] [Car {self.id}] Stuck at {self.position}. Target Index: {self.target_index}/{len(self.path) if self.path else 0}")
                self.time_since_last_move = 0.0 # Reset to avoid spam
        else:
            self.time_since_last_move = 0.0
            self.last_position = glm.vec3(self.position)

        if not self.path or self.target_index >= len(self.path):
            self.pick_next_path(print_despawn_debug=print_despawn_debug)
            if not self.alive: return
            return

        # Target Point
        target = self.path[self.target_index]
        
        # Direction to target
        vec_to_target = target - self.position
        dist = glm.length(vec_to_target)
        
        # Move
        if dist > 0.1:
            direction = glm.normalize(vec_to_target)
            self.orientation = direction
            move_step = direction * self.speed * dt
            
            # Check overshot
            if glm.length(move_step) >= dist:
                self.position = target
                self.target_index += 1
            else:
                self.position += move_step
        else:
            # Snap and increment
            self.position = glm.vec3(target)
            self.target_index += 1
            
        # Update Transform
        self._update_transform()

    def register_on_lane(self, lane):
        if lane and self not in lane.active_agents:
            lane.active_agents.append(self)

    def deregister_from_lane(self, lane):
        if lane and self in lane.active_agents:
            lane.active_agents.remove(self)

    def _update_transform(self):
        # Translate
        mat = glm.translate(self.position)
        
        # Rotate to face orientation
        yaw = math.atan2(self.orientation.x, self.orientation.z)
        
        rot = glm.rotate(yaw, glm.vec3(0, 1, 0))
        scale = glm.scale(glm.vec3(1.5, 1.5, 1.5))
        
        self.mesh_object.transform = mat * rot * scale

    def pick_next_path(self, print_despawn_debug=False):
        # We reached end of current path
        
        if self.current_curve:
            # We just finished a curve. Find the lane it leads to.
            self.deregister_from_lane(self.current_lane)
            self.current_lane = self.next_lane_after_curve
            
            self.register_on_lane(self.current_lane)
            
            self.current_curve = None
            self.path = self.current_lane.waypoints
            self.target_index = 0
            
            # Snap to start to fix drift
            if self.path:
                p = self.path[0]
                self.position = glm.vec3(p.x, p.y, p.z) # [FIX] Explicit Copy
                self.target_index = 1
            
        elif self.current_lane:
            # We reached end of a Lane. Look for connections at the Dest Node.
            node = self.current_lane.dest_node
            
            if not len(node.connections):
                 # No connections at all
                 if (print_despawn_debug):
                     print(f"[WARN] [Car {self.id}] Despawning at Node {node.id} (No connections).")
                 self.deregister_from_lane(self.current_lane) # [NEW] Cleanup
                 self.alive = False
                 return

            # Find connections starting with our lane ID
            valid_keys = [k for k in node.connections.keys() if k[0] == self.current_lane.id]
            
            if valid_keys:
                # Pick Random
                key = random.choice(valid_keys)
                
                # key is (from_id, to_id)
                next_lane_id = key[1]
                
                # Find the Lane object for next_lane_id
                next_lane = None
                for out_edge in node.edges:
                    if not hasattr(out_edge, 'lanes'): continue
                    for l in out_edge.lanes:
                        if l.id == next_lane_id:
                            next_lane = l
                            break
                    if next_lane: break
                
                if next_lane:
                    self.current_curve = node.connections[key]
                    self.next_lane_after_curve = next_lane
                    
                    self.path = self.current_curve
                    self.target_index = 0
                    
                    # Do not snap position, curve starts at lane end (roughly)
                    self.deregister_from_lane(self.current_lane)
                    self.current_lane = None
                else:
                    self.deregister_from_lane(self.current_lane)
                    self.alive = False
            else:
                # Dead End (e.g. edge of map)
                print(f"[WARN] [Car {self.id}] Despawning at Node {node.id} (Lane {self.current_lane.id} has no outlets).")
                self.deregister_from_lane(self.current_lane)
                self.alive = False

    def render_debug(self, renderer, camera):
        # Draw Target Sphere
        if self.path and self.target_index < len(self.path):
            target = self.path[self.target_index]
            
            if CarAgent.debug_sphere_mesh:
                CarAgent.debug_sphere_mesh.transform = glm.translate(target)
                CarAgent.debug_sphere_mesh.draw(camera, [])

        pass