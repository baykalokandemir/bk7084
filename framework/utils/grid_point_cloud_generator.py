from pyglm import glm
import numpy as np
from ..shapes.shape import Shape

class GridPointCloudGenerator:
    @staticmethod
    def generate(source_shape, spacing=0.2, color=glm.vec4(1.0)):
        """
        Generates a point cloud Shape from a source Shape by sampling its surface
        using a triplanar grid projection.
        
        spacing: distance between grid points in world space units.
        """
        # Ensure source geometry is created
        if len(source_shape.vertices) == 0:
            source_shape.createGeometry()
            
        vertices = source_shape.vertices
        indices = source_shape.indices
        
        # Extract triangles
        triangles = []
        if indices is not None and len(indices) > 0:
            # Indexed mesh
            for i in range(0, len(indices), 3):
                idx0 = indices[i]
                idx1 = indices[i+1]
                idx2 = indices[i+2]
                v0 = glm.vec3(vertices[idx0][0], vertices[idx0][1], vertices[idx0][2])
                v1 = glm.vec3(vertices[idx1][0], vertices[idx1][1], vertices[idx1][2])
                v2 = glm.vec3(vertices[idx2][0], vertices[idx2][1], vertices[idx2][2])
                # Access normals if available for better dominant axis selection?
                # We can compute face normal from vertices.
                triangles.append((v0, v1, v2))
        else:
            # Non-indexed mesh
            for i in range(0, len(vertices), 3):
                v0 = glm.vec3(vertices[i][0], vertices[i][1], vertices[i][2])
                v1 = glm.vec3(vertices[i+1][0], vertices[i+1][1], vertices[i+1][2])
                v2 = glm.vec3(vertices[i+2][0], vertices[i+2][1], vertices[i+2][2])
                triangles.append((v0, v1, v2))

        new_verts = []
        new_norms = []
        new_uvs = []
        
        # Small epsilon to catch points exactly on edges
        epsilon = 1e-5

        for v0, v1, v2 in triangles:
            # Calculate geometric normal
            edge1 = v1 - v0
            edge2 = v2 - v0
            normal = glm.normalize(glm.cross(edge1, edge2))
            
            # 1. Determine Dominant Axis
            nx, ny, nz = abs(normal.x), abs(normal.y), abs(normal.z)
            
            # Helper to check point is in triangle 3D
            def is_in_triangle(p, a, b, c):
                # Barycentric technique
                v0 = c - a
                v1 = b - a
                v2 = p - a

                dot00 = glm.dot(v0, v0)
                dot01 = glm.dot(v0, v1)
                dot02 = glm.dot(v0, v2)
                dot11 = glm.dot(v1, v1)
                dot12 = glm.dot(v1, v2)

                denominator = dot00 * dot11 - dot01 * dot01
                if abs(denominator) < 1e-8:
                    return False
                    
                invDenom = 1 / denominator
                u = (dot11 * dot02 - dot01 * dot12) * invDenom
                v = (dot00 * dot12 - dot01 * dot02) * invDenom

                return (u >= -epsilon) and (v >= -epsilon) and (u + v <= 1 + epsilon)

            points_on_tri = []
            
            # Determine projection plane and scan
            if nx >= ny and nx >= nz:
                # X-Dominant: Project to YZ plane
                # Plane eq: normal.x * x + normal.y * y + normal.z * z = D
                # D = dot(normal, v0)
                # x = (D - normal.y*y - normal.z*z) / normal.x
                
                D = glm.dot(normal, v0)
                
                min_y = min(v0.y, v1.y, v2.y)
                max_y = max(v0.y, v1.y, v2.y)
                min_z = min(v0.z, v1.z, v2.z)
                max_z = max(v0.z, v1.z, v2.z)
                
                start_y = np.floor(min_y / spacing) * spacing
                start_z = np.floor(min_z / spacing) * spacing
                
                y = start_y
                while y <= max_y + spacing:
                    z = start_z
                    while z <= max_z + spacing:
                        # Solve X
                        if abs(normal.x) > 1e-4:
                            x = (D - normal.y * y - normal.z * z) / normal.x
                            p = glm.vec3(x, y, z)
                            if is_in_triangle(p, v0, v1, v2):
                                points_on_tri.append(p)
                        z += spacing
                    y += spacing

            elif ny >= nx and ny >= nz:
                # Y-Dominant: Project to XZ plane
                # y = (D - normal.x*x - normal.z*z) / normal.y
                D = glm.dot(normal, v0)
                
                min_x = min(v0.x, v1.x, v2.x)
                max_x = max(v0.x, v1.x, v2.x)
                min_z = min(v0.z, v1.z, v2.z)
                max_z = max(v0.z, v1.z, v2.z)
                
                start_x = np.floor(min_x / spacing) * spacing
                start_z = np.floor(min_z / spacing) * spacing
                
                x = start_x
                while x <= max_x + spacing:
                    z = start_z
                    while z <= max_z + spacing:
                        if abs(normal.y) > 1e-4:
                            y = (D - normal.x * x - normal.z * z) / normal.y
                            p = glm.vec3(x, y, z)
                            if is_in_triangle(p, v0, v1, v2):
                                points_on_tri.append(p)
                        z += spacing
                    x += spacing
                    
            else:
                # Z-Dominant: Project to XY plane
                # z = (D - normal.x*x - normal.y*y) / normal.z
                D = glm.dot(normal, v0)
                
                min_x = min(v0.x, v1.x, v2.x)
                max_x = max(v0.x, v1.x, v2.x)
                min_y = min(v0.y, v1.y, v2.y)
                max_y = max(v0.y, v1.y, v2.y)
                
                start_x = np.floor(min_x / spacing) * spacing
                start_y = np.floor(min_y / spacing) * spacing
                
                x = start_x
                while x <= max_x + spacing:
                    y = start_y
                    while y <= max_y + spacing:
                        if abs(normal.z) > 1e-4:
                            z = (D - normal.x * x - normal.y * y) / normal.z
                            p = glm.vec3(x, y, z)
                            if is_in_triangle(p, v0, v1, v2):
                                points_on_tri.append(p)
                        y += spacing
                    x += spacing

            for p in points_on_tri:
                new_verts.append(glm.vec4(p.x, p.y, p.z, 1.0))
                new_norms.append(normal)
                # Use simplified density or grid UVs
                # For grid, UV could be world position
                new_uvs.append(glm.vec2(0.0, 0.0))

        # Create new Shape
        pc_shape = Shape()
        pc_shape.vertices = np.array(new_verts, dtype=np.float32)
        pc_shape.normals = np.array(new_norms, dtype=np.float32)
        pc_shape.colors = np.full((len(new_verts), 4), color, dtype=np.float32)
        pc_shape.uvs = np.array(new_uvs, dtype=np.float32)
        pc_shape.indices = None
        
        pc_shape.createGeometry = lambda: None 
        
        return pc_shape
