# framework/utils/vehicle_merger.py
import numpy as np
from ..shapes.shape import Shape

try:
    from pyglm import glm
except ImportError:
    import glm

class VehicleMerger:
    """Merges BaseVehicle parts into a single optimized mesh"""
    
    @staticmethod
    def merge_vehicle(vehicle):
        """
        Takes a BaseVehicle with parts[], returns a single Shape.
        Bakes all part transforms into a single mesh.
        """
        if not hasattr(vehicle, 'parts') or not vehicle.parts:
            print(f"[VehicleMerger] No parts to merge!")
            return Shape()
        
        all_verts = []
        all_norms = []
        all_colors = []
        all_uvs = []
        all_indices = []
        vertex_offset = 0
        
        for i, part in enumerate(vehicle.parts):
            # Get mesh data
            if not hasattr(part, 'mesh'):
                print(f"[VehicleMerger] Part {i} has no mesh, skipping")
                continue
                
            mesh = part.mesh
            
            # FORCE geometry creation if not already done
            if not hasattr(mesh, 'vertices') or mesh.vertices is None or len(mesh.vertices) == 0:
                if hasattr(mesh, 'createGeometry'):
                    mesh.createGeometry()
                else:
                    print(f"[VehicleMerger] Part {i}: No createGeometry method!")
                    continue
            
            # Check again after creation attempt
            if not hasattr(mesh, 'vertices') or mesh.vertices is None or len(mesh.vertices) == 0:
                print(f"[VehicleMerger] Part {i}: Still no vertices after createGeometry!")
                continue
            
            verts_np = mesh.vertices
            count = len(verts_np)
            
            # Get local transform
            local_tf = part.local_transform if hasattr(part, 'local_transform') else glm.mat4(1.0)
            
            # Convert glm matrix to numpy (column-major to row-major)
            mat_list = local_tf.to_list()
            tf_np = np.array(mat_list, dtype=np.float32).reshape(4, 4)
            
            # Apply transform: vertices are row vectors, so V' = V * M
            transformed_verts = verts_np @ tf_np
            
            # Transform normals
            norms_np = mesh.normals
            if norms_np is None or len(norms_np) == 0:
                norms_np = np.tile([0, 1, 0], (count, 1)).astype(np.float32)
            
            # Use 3x3 part for normals
            rot_3x3 = tf_np[:3, :3]
            norms_tf = norms_np @ rot_3x3
            
            # Normalize
            norms_len = np.linalg.norm(norms_tf, axis=1, keepdims=True)
            norms_len[norms_len < 0.0001] = 1.0
            norms_tf = norms_tf / norms_len
            
            # Get colors
            if hasattr(mesh, 'colors') and mesh.colors is not None and len(mesh.colors) > 0:
                colors = mesh.colors
            else:
                colors = np.ones((count, 4), dtype=np.float32)
            
            # Get UVs
            if hasattr(mesh, 'uvs') and mesh.uvs is not None and len(mesh.uvs) > 0:
                uvs = mesh.uvs
            else:
                uvs = np.zeros((count, 2), dtype=np.float32)
            
            # Offset indices
            inds = mesh.indices + vertex_offset
            
            # Accumulate
            all_verts.append(transformed_verts)
            all_norms.append(norms_tf)
            all_colors.append(colors)
            all_uvs.append(uvs)
            all_indices.append(inds)
            
            vertex_offset += count
        
        if not all_verts:
            print("[VehicleMerger] ERROR: No vertices collected!")
            return Shape()
        
        # Concatenate
        merged_shape = Shape()
        merged_shape.vertices = np.vstack(all_verts)
        merged_shape.normals = np.vstack(all_norms)
        merged_shape.colors = np.vstack(all_colors)
        merged_shape.uvs = np.vstack(all_uvs)
        merged_shape.indices = np.concatenate(all_indices)
             
        merged_shape.createBuffers()
        
        return merged_shape