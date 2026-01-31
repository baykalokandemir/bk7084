import numpy as np
import OpenGL.GL as gl
from framework.objects import MeshObject
from framework.shapes.shape import Shape
from pyglm import glm

class MeshBatcher:
    def __init__(self):
        self.vertices = []
        self.normals = []
        self.uvs = []
        self.colors = []
        self.indices = []
        self.index_offset = 0

    def add_shape(self, shape, transform=None, color=None):
        """
        Adds a shape to the batch.
        shape: Shape object (must have vertices, normals, indices, etc.)
        transform: glm.mat4 (optional)
        color: glm.vec4 (optional override)
        """
        # Ensure shape has geometry
        if not hasattr(shape, 'vertices') or shape.vertices is None or len(shape.vertices) == 0:
            if hasattr(shape, 'createGeometry'):
                shape.createGeometry()
            else:
                print(f"[MeshBatcher] Shape has no vertices and no createGeometry method, skipping")
                return
        
        # Check again after creation attempt
        if not hasattr(shape, 'vertices') or shape.vertices is None or len(shape.vertices) == 0:
            print(f"[MeshBatcher] Still no vertices after createGeometry!")
            return
        
        s_verts = shape.vertices
        s_norms = shape.normals
        s_uvs = shape.uvs
        s_inds = shape.indices
        s_cols = shape.colors
        
        count = len(s_verts)
        if count == 0:
            return

        # Apply Transform
        if transform is not None:
            # Convert glm matrix to numpy
            mat_list = transform.to_list()
            m_np = np.array(mat_list, dtype=np.float32).reshape(4, 4)
            
            # Transform vertices: V' = V @ M
            v_new = s_verts @ m_np
            
            # Transform normals using 3x3 rotation part
            rot_3x3 = m_np[:3, :3]
            
            # Handle normals
            if s_norms is None or len(s_norms) == 0:
                n_new = np.tile([0, 1, 0], (count, 1)).astype(np.float32)
            else:
                n_new = s_norms @ rot_3x3
                # Normalize
                norms = np.linalg.norm(n_new, axis=1, keepdims=True)
                norms[norms < 0.0001] = 1.0
                n_new = n_new / norms
            
        else:
            v_new = s_verts
            if s_norms is None or len(s_norms) == 0:
                n_new = np.tile([0, 1, 0], (count, 1)).astype(np.float32)
            else:
                n_new = s_norms
            
        # Colors
        if color is not None:
            # Override colors
            c_new = np.tile(np.array(color.to_list(), dtype=np.float32), (count, 1))
        else:
            if s_cols is not None and len(s_cols) > 0:
                c_new = s_cols
            else:
                c_new = np.ones((count, 4), dtype=np.float32)

        # UVs
        u_new = s_uvs if s_uvs is not None and len(s_uvs) > 0 else np.zeros((count, 2), dtype=np.float32)

        # Append
        self.vertices.append(v_new)
        self.normals.append(n_new)
        self.uvs.append(u_new)
        self.colors.append(c_new)
        
        # Indices - offset them
        i_new = s_inds + self.index_offset
        self.indices.append(i_new)
        
        self.index_offset += count

    def add_vehicle(self, vehicle):
        """
        Convenience method to add all parts from a BaseVehicle.
        vehicle: BaseVehicle with parts[] attribute
        """
        if not hasattr(vehicle, 'parts') or not vehicle.parts:
            print(f"[MeshBatcher] Vehicle has no parts to add!")
            return
        
        for i, part in enumerate(vehicle.parts):
            if not hasattr(part, 'mesh'):
                print(f"[MeshBatcher] Part {i} has no mesh, skipping")
                continue
            
            local_tf = part.local_transform if hasattr(part, 'local_transform') else glm.mat4(1.0)
            self.add_shape(part.mesh, transform=local_tf)

    def build(self, material=None):
        """
        Returns a MeshObject containing all batched geometry.
        If material is None, returns just the Shape.
        """
        if not self.vertices:
            return None
            
        # Concatenate
        all_verts = np.vstack(self.vertices)
        all_norms = np.vstack(self.normals)
        all_uvs = np.vstack(self.uvs)
        all_cols = np.vstack(self.colors)
        all_inds = np.concatenate(self.indices)
        
        # Create Shape
        shape = Shape()
        shape.vertices = all_verts
        shape.normals = all_norms
        shape.uvs = all_uvs
        shape.colors = all_cols
        shape.indices = all_inds
        
        shape.createBuffers()
        
        if material is None:
            return shape
        else:
            return MeshObject(shape, material)
    
    def reset(self):
        """Clear the batcher to start a new batch"""
        self.vertices = []
        self.normals = []
        self.uvs = []
        self.colors = []
        self.indices = []
        self.index_offset = 0


# Backwards compatibility alias
class VehicleMerger:
    """Legacy wrapper - use MeshBatcher instead"""
    
    @staticmethod
    def merge_vehicle(vehicle):
        """
        Takes a BaseVehicle with parts[], returns a single Shape.
        DEPRECATED: Use MeshBatcher.add_vehicle() instead.
        """
        batcher = MeshBatcher()
        batcher.add_vehicle(vehicle)
        return batcher.build()