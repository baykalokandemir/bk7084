from pyglm import glm
import random
import math
from framework.objects.mesh_object import MeshObject
from framework.shapes.car import Car
from framework.shapes.uvsphere import UVSphere
from framework.materials.material import Material

class CarAgent:
    # Shared Debug Shape (Static)
    debug_sphere_mesh = None

    def __init__(self, start_lane, car_shape=None):
        self.current_lane = start_lane
        self.current_curve = None # List of points if turning
        self.speed = 15.0 # Units/sec
        
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
        self.alive = True # [NEW] Signal for removal

        # Visuals
        # Create a dedicated MeshObject for this agent
        # We share the geometry (Car Shape) but have unique transform (MeshObject)
        if car_shape is None:
            # Bright Yellow
            car_shape = Car(body_color=glm.vec4(1.0, 1.0, 0.0, 1.0))
            car_shape.createGeometry()
            
        self.mesh_object = MeshObject(car_shape, Material())
        
        # Randomize color slightly via material uniform? 
        # Car shape has baked colors. 
        # We could update the vertices colors, but sharing shape prevents unique colors per car.
        # Ideally, we used InstancedMeshObject for many cars, but distinct MeshObjects is fine for < 100.
        
        # Init static debug mesh if needed
        if CarAgent.debug_sphere_mesh is None:
             sphere = UVSphere(radius=0.5, color=glm.vec4(1.0, 0.0, 1.0, 1.0)) # Magenta Target
             sphere.createGeometry()
             mat = Material()
             mat.uniforms = { "ambientStrength": 1.0, "diffuseStrength": 0.0, "specularStrength": 0.0 }
             CarAgent.debug_sphere_mesh = MeshObject(sphere, mat)

    def update(self, dt):
        if not self.alive: return # Don't update dead agents

        # Stuck Check
        if glm.distance(self.position, self.last_position) < 0.01:
            self.time_since_last_move += dt
            if self.time_since_last_move > 2.0:
                print(f"[ALERT] Car stuck at {self.position}. Target Index: {self.target_index}/{len(self.path) if self.path else 0}")
                self.time_since_last_move = 0.0 # Reset to avoid spam
        else:
            self.time_since_last_move = 0.0
            self.last_position = glm.vec3(self.position)

        if not self.path or self.target_index >= len(self.path):
            self.pick_next_path()
            if not self.alive: return
            return

        # Target Point
        target = self.path[self.target_index]
        
        # Direction to target
        vec_to_target = target - self.position
        dist = glm.length(vec_to_target)
        
        # Move
        if dist > 0.001:
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
            self.target_index += 1
            
        # Update Transform
        self._update_transform()
        
    def _update_transform(self):
        # Translate
        mat = glm.translate(self.position)
        
        # Rotate to face orientation
        # Default Car faces +Z? Check Car class.
        # Car class: "Front face (z = +len/2)". So +Z is Front.
        # We want +Z to align with self.orientation.
        
        # LookAt is usually (eye, center, up).
        # We want a rotation that maps (0,0,1) to orientation.
        
        # Simple method: atan2
        # yaw = atan2(dir.x, dir.z)
        yaw = math.atan2(self.orientation.x, self.orientation.z)
        
        rot = glm.rotate(yaw, glm.vec3(0, 1, 0))
        scale = glm.scale(glm.vec3(1.5, 1.5, 1.5))
        
        self.mesh_object.transform = mat * rot * scale
        
        # Also ensure wheel rotation or similar? (Not needed for simple viz)

    def pick_next_path(self):
        # We reached end of current path
        
        if self.current_curve:
            # We just finished a curve. Find the lane it leads to.
            # self.current_curve is a list of points.
            # We don't have a direct link "Curve -> Lane" stored easily in Agent?
            # Storing it on State Transition is better.
            
            self.current_lane = self.next_lane_after_curve
            self.current_curve = None
            self.path = self.current_lane.waypoints
            self.target_index = 0
            # print(f"[DEBUG] Finished Turn. Entering Lane {self.current_lane.id}")
            
            # Snap to start to fix drift
            if self.path:
                self.position = self.path[0]
                self.target_index = 1
            
        elif self.current_lane:
            # We reached end of a Lane. Look for connections at the Dest Node.
            # PREVIOUSLY BUGGY: edge = self.current_lane.parent_edge; node = edge.end_node
            # CORRECT: Use explicit destination stored on Lane
            node = self.current_lane.dest_node
            
            if not len(node.connections):
                 # No connections at all
                 print(f"[WARN] Despawning car at Node {node.id} (No connections).")
                 self.alive = False
                 return

            # Find connections starting with our lane ID
            valid_keys = [k for k in node.connections.keys() if k[0] == self.current_lane.id]
            
            if valid_keys:
                # Pick Random
                key = random.choice(valid_keys)
                
                # key is (from_id, to_id)
                next_lane_id = key[1]
                
                # Find the Lane object for next_lane_id?
                # We need a lookup or search.
                # Only way is to search outgoing edges of node.
                
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
                    self.current_lane = None
                    print(f"[DEBUG] Car at Node {node.id} chose turn to Lane {next_lane.id}. Path Len: {len(self.path)}")
                else:
                    print(f"[ERROR] Car at Node {node.id}: Selected connection {key} but could not find Next Lane object!")
                    # Hard fail or Despawn? Despawn to be safe
                    self.alive = False
            else:
                # Dead End (e.g. edge of map)
                print(f"[WARN] Despawning car at Node {node.id} (Lane {self.current_lane.id} has no outlets).")
                self.alive = False

    def render_debug(self, renderer, camera):
        # Draw Target Sphere
        if self.path and self.target_index < len(self.path):
            target = self.path[self.target_index]
            
            if CarAgent.debug_sphere_mesh:
                # Set Transform
                # This is a shared mesh object usually used for static props, 
                # but we can reuse it by changing transform before draw.
                # WARNING: If renderer batches or queues, this fails. 
                # Usually Object.draw() executes immediately in this frameworks (checked MeshObject.draw).
                
                # We need to access lights? Pass empty list or minimal.
                # Renderer usually handles this.
                # We can call debug_sphere_mesh.draw(camera, [])
                
                CarAgent.debug_sphere_mesh.transform = glm.translate(target)
                CarAgent.debug_sphere_mesh.draw(camera, [])
            
        # Draw Path (Cyan)? 
        # Hard without immediate mode or dynamic mesh.
        # We rely on existing debug lines for static path.
        pass
