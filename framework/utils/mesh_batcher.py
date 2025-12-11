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
        # Ensure shape data is available (numpy arrays)
        # We need to convert them to lists or process as numpy
        
        # Helper to get data
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
            # Transform vertices
            # V_new = M * V
            # We need to do this efficiently. 
            # Convert to glm, transform, back to list? Or numpy math.
            
            # Numpy approach: (N, 4) * (4, 4)
            # Vertices are (N, 4) [x, y, z, w]
            # M is (4, 4)
            # V_new = V @ M.T
            
            # m_np = np.array(transform.to_list(), dtype=np.float32).T # WRONG: glm list is cols, np array cols are rows.
            m_np = np.array(transform.to_list(), dtype=np.float32)
            v_new = s_verts @ m_np
            
            # Transform normals
            # N_new = N @ (M_inv_trans).T = N @ M_inv
            # Rotation only: N @ M.T (if orthogonal)
            # Let's assume uniform scale/rotation.
            # Normal matrix = mat3(transpose(inverse(model)))
            # If we use glm:
            nm = glm.transpose(glm.inverse(transform))
            nm_np = np.array(nm.to_list(), dtype=np.float32)
            
            # Normals are (N, 3) or (N, 4)? Shape usually stores (N, 3).
            # If (N, 3), we need 3x3 matrix.
            # Extract 3x3 from nm_np
            nm_3x3 = nm_np[:3, :3] # ? Wait, nm_np is 4x4.
            
            # Let's just use 4x4 for normals with w=0
            n_4 = np.hstack([s_norms, np.zeros((count, 1), dtype=np.float32)])
            n_new_4 = n_4 @ nm_np
            n_new = n_new_4[:, :3]
            
            # Normalize
            norms = np.linalg.norm(n_new, axis=1, keepdims=True)
            # Avoid divide by zero
            norms[norms == 0] = 1.0
            n_new = n_new / norms
            
        else:
            v_new = s_verts
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
        u_new = s_uvs if s_uvs is not None else np.zeros((count, 2), dtype=np.float32)

        # Append
        self.vertices.append(v_new)
        self.normals.append(n_new)
        self.uvs.append(u_new)
        self.colors.append(c_new)
        
        # Indices
        # Offset indices
        i_new = s_inds + self.index_offset
        self.indices.append(i_new)
        
        self.index_offset += count

    def build(self, material):
        """
        Returns a MeshObject containing all batched geometry.
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
        
        return MeshObject(shape, material)
