import glm
import random
from framework.objects.mesh_object import MeshObject
from framework.materials.material import Material
from framework.utils.mesh_batcher import MeshBatcher

class CrashCluster:
    """
    Represents a pile-up of crashed vehicles.
    
    Manages visual representation of wrecked cars and provides spatial
    blocking for traffic avoidance. Clusters can grow as more vehicles
    crash into existing pile-ups (chain reactions).
    """
    _id_counter = 0
    BASE_BLOCKING_RADIUS = 3.0
    RADIUS_GROWTH_PER_CAR = 0.8

    def __init__(self):
        self.id = CrashCluster._id_counter
        CrashCluster._id_counter += 1
        
        self.center = glm.vec3(0, 0, 0)
        self.crashed_agents = []
        self.mesh_objects = []
        self.blocking_radius = self.BASE_BLOCKING_RADIUS

    def add_agent(self, agent, collision_point):
        """
        Adds an agent to the cluster and creates a visual wreck representation.
        """
        # Calculate old count before appending
        old_count = len(self.crashed_agents)
        
        self.crashed_agents.append(agent)
        
        # [FIX] Try to reuse existing mesh from agent to preserve color/size
        vehicle_shape = None
        if hasattr(agent, 'mesh_object') and hasattr(agent.mesh_object, 'mesh'):
             vehicle_shape = agent.mesh_object.mesh
             
        if vehicle_shape is None:
             # Fallback: Recreate vehicle from agent's type
             # This happens if mesh was already deleted or not fully initialized
             from exercises.components.city_manager import CityManager
             vehicle_shape = CityManager.get_car_shape_by_name(agent.vehicle_type)
        
        # Batch into single mesh
        batcher = MeshBatcher()
        
        # Check if it's a Complex BaseVehicle (has parts) or a simple Shape
        if hasattr(vehicle_shape, 'parts'):
             batcher.add_vehicle(vehicle_shape)
        else:
             batcher.add_shape(vehicle_shape)
        
        # Force wreck material
        wreck_mat = Material()
        wreck_mat.uniforms = {"ambientStrength": 0.4, "diffuseStrength": 0.5, "specularStrength": 0.1}
        
        wreck_mesh = batcher.build(wreck_mat) 
        
        # Randomize transform to look like a wreck
        offset = glm.vec3(
            random.uniform(-1.0, 1.0),
            random.uniform(0.0, 1.0),
            random.uniform(-1.0, 1.0)
        )
        pos = collision_point + offset
        
        # Random Rotation
        angle_x = random.uniform(0, 360)
        angle_y = random.uniform(0, 360)
        angle_z = random.uniform(0, 360)
        
        # Apply Transform
        wreck_mesh.transform = glm.translate(pos) * \
                               glm.rotate(glm.radians(angle_x), glm.vec3(1, 0, 0)) * \
                               glm.rotate(glm.radians(angle_y), glm.vec3(0, 1, 0)) * \
                               glm.rotate(glm.radians(angle_z), glm.vec3(0, 0, 1))
                               
        self.mesh_objects.append(wreck_mesh)
        
        # Incremental center update (more efficient)
        if old_count == 0:
            self.center = agent.position
        else:
            new_count = len(self.crashed_agents)
            self.center = (self.center * old_count + agent.position) / new_count
            
        # Update Blocking Radius
        self.blocking_radius = self.BASE_BLOCKING_RADIUS + len(self.crashed_agents) * self.RADIUS_GROWTH_PER_CAR

    def is_blocking(self, position, safety_margin=4.0):
        """
        Checks if a position is within the blocking radius of this cluster.
        """
        dist = glm.distance(position, self.center)
        return dist < (self.blocking_radius + safety_margin)

    def get_renderables(self):
        """
        Returns list of renderable objects for the renderer.
        """
        return self.mesh_objects
