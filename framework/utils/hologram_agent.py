from pyglm import glm
import random

class HologramAgent:
    def __init__(self, mesh_object, rotation_speed=1.0, rotation_axis=None):
        self.mesh_object = mesh_object
        self.base_transform = glm.mat4(mesh_object.transform) # Store initial static placement (relative to group logic?)
        # Wait, if we are rotating "in place", we want to rotate around the object's center.
        # But the object's transform includes its position offset from the group center.
        # If we just multiply rotation, it rotates around the origin (0,0,0) of the object's local space.
        # If the object was created with vertices centered at 0,0,0 and translated via transform, 
        # then modifying that transform with a rotation *before* the translation makes it spin in place.
        # Matrix order: T * R * S.
        
        # However, `mesh_object.transform` is ALREADY a combined matrix (likely Global or Local-to-Root).
        # To spin in place, we need to decompose it or maintain Position and Rotation separate.
        
        # Simpler approach:
        # Store the "Position" and "Initial Rotation" separately if possible.
        # OR:
        # Just maintain a `current_rotation_angle` and rebuild the matrix every frame.
        # T (fixed from L-System) * R (dynamic) * S (fixed).
        
        # Since we don't easily decompose the matrix without issues, let's assume the L-System
        # gave us a matrix `M_static`. This M_static positions the object in the cluster.
        # We want to add a "Spin" on top of that.
        # Final = M_static * R_spin? 
        # No, M_static already contains translation. 
        # If we do M_static * R_spin, we rotate around the object's own local origin (which is correct for spin-in-place).
        
        self.initial_transform = glm.mat4(mesh_object.transform)
        self.current_angle = 0.0
        self.rotation_speed = rotation_speed # Radians per second
        
        if rotation_axis is None:
            # Random axis
            self.rotation_axis = glm.normalize(glm.vec3(
                random.uniform(-1, 1),
                random.uniform(-1, 1),
                random.uniform(-1, 1)
            ))
        else:
            self.rotation_axis = rotation_axis
            
    def update(self, dt):
        self.current_angle += self.rotation_speed * dt
        
        # Create rotation matrix
        rot = glm.rotate(self.current_angle, self.rotation_axis)
        
        # Apply: Original (Pos/Scale) * Rotation
        # Note: If Original also had rotation, this appends new rotation.
        # Ideally: we want to spin around the mesh's geometric center.
        # Assuming mesh vertices are centered:
        # Final = ParentTransform * LocalPos * Rotation * Scale
        
        # The L-System gave us a fully baked transform T.
        # We assume T = Translate * Rotate_LSystem * Scale.
        # We want: T * Rotate_Spin. (Rotate in local space).
        
        self.mesh_object.transform = self.initial_transform * rot
