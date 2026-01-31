import glm
import random
from framework.objects.mesh_object import MeshObject
from framework.materials.material import Material

class CrashCluster:
    _id_counter = 0

    def __init__(self):
        self.id = CrashCluster._id_counter
        CrashCluster._id_counter += 1
        
        self.center = glm.vec3(0, 0, 0)
        self.crashed_agents = []
        self.mesh_objects = []
        self.blocking_radius = 3.0

    def add_agent(self, agent, collision_point, crash_shape, material=None):
        """
        Adds an agent to the cluster and creates a visual wreck representation.
        """
        self.crashed_agents.append(agent)
        
        # Use provided material or default
        mat = material if material else Material()
        
        # Create visual wreck (using placeholder shape for now)
        wreck_mesh = MeshObject(crash_shape, mat)
        
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
        
        # Recalculate Center based on all agents in cluster
        if self.crashed_agents:
            sum_pos = glm.vec3(0)
            for a in self.crashed_agents:
                sum_pos += a.position
            self.center = sum_pos / len(self.crashed_agents)
            
        # Update Blocking Radius (expands as pile-up grows)
        self.blocking_radius = 3.0 + len(self.crashed_agents) * 0.8

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
