from pyglm import glm
import numpy as np
import random
from ..shapes.shape import Shape

class PointCloudGenerator:
    @staticmethod
    def generate(source_shape, point_count, color=glm.vec4(1.0), mode='random'):
        """
        Generates a point cloud Shape from a source Shape by sampling its surface.
        mode: 'random' or 'poisson'
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
                triangles.append((v0, v1, v2))
        else:
            # Non-indexed mesh (triangle soup)
            for i in range(0, len(vertices), 3):
                v0 = glm.vec3(vertices[i][0], vertices[i][1], vertices[i][2])
                v1 = glm.vec3(vertices[i+1][0], vertices[i+1][1], vertices[i+1][2])
                v2 = glm.vec3(vertices[i+2][0], vertices[i+2][1], vertices[i+2][2])
                triangles.append((v0, v1, v2))
                
        # Calculate triangle areas
        areas = []
        total_area = 0.0
        for v0, v1, v2 in triangles:
            # Area = 0.5 * |cross(v1-v0, v2-v0)|
            edge1 = v1 - v0
            edge2 = v2 - v0
            area = 0.5 * glm.length(glm.cross(edge1, edge2))
            areas.append(area)
            total_area += area
            
        new_verts = []
        new_norms = []
        new_uvs = []
        
        if mode == 'random':
            # Weighted random sampling of triangles
            selected_indices = random.choices(range(len(triangles)), weights=areas, k=point_count)
            
            for idx in selected_indices:
                v0, v1, v2 = triangles[idx]
                p, n = PointCloudGenerator._sample_triangle(v0, v1, v2)
                
                # Explicitly convert to python floats
                if not isinstance(p, glm.vec3): p = glm.vec3(p)
                x, y, z = float(p.x), float(p.y), float(p.z)
                
                new_verts.append(glm.vec4(x, y, z, 1.0))
                new_norms.append(n)
                new_uvs.append(glm.vec2(0.0, 0.0))
                
        elif mode == 'poisson':
            # Poisson Disk Sampling (Dart Throwing)
            # Estimate radius
            # Area ~= N * PI * r^2 (packing density affects this, but let's approximate)
            # r ~= sqrt(Area / (N * PI))
            # We use a slightly smaller radius to ensure we can fit enough points
            radius = np.sqrt(total_area / (point_count * np.pi)) * 0.8
            radius2 = radius * radius
            cell_size = radius / np.sqrt(3)
            
            grid = {} # (ix, iy, iz) -> [points]
            
            def get_grid_idx(p):
                return (int(p.x / cell_size), int(p.y / cell_size), int(p.z / cell_size))
            
            # We need to generate candidates. 
            # Generating one by one is slow if rejection rate is high.
            # Let's generate batches.
            batch_size = 1000
            attempts = 0
            max_attempts = point_count * 10 # Safety break
            
            while len(new_verts) < point_count and attempts < max_attempts:
                # Generate a batch of candidates
                candidate_indices = random.choices(range(len(triangles)), weights=areas, k=batch_size)
                
                for idx in candidate_indices:
                    if len(new_verts) >= point_count:
                        break
                        
                    v0, v1, v2 = triangles[idx]
                    p, n = PointCloudGenerator._sample_triangle(v0, v1, v2)
                    
                    if not isinstance(p, glm.vec3): p = glm.vec3(p)
                    
                    # Check against grid
                    grid_idx = get_grid_idx(p)
                    valid = True
                    
                    # Check neighbors (3x3x3)
                    for dx in [-1, 0, 1]:
                        for dy in [-1, 0, 1]:
                            for dz in [-1, 0, 1]:
                                neighbor_idx = (grid_idx[0]+dx, grid_idx[1]+dy, grid_idx[2]+dz)
                                if neighbor_idx in grid:
                                    for existing_p in grid[neighbor_idx]:
                                        # Distance check
                                        dist2 = glm.distance2(p, existing_p)
                                        if dist2 < radius2:
                                            valid = False
                                            break
                                if not valid: break
                            if not valid: break
                        if not valid: break
                    
                    if valid:
                        # Accept point
                        if grid_idx not in grid:
                            grid[grid_idx] = []
                        grid[grid_idx].append(p)
                        
                        x, y, z = float(p.x), float(p.y), float(p.z)
                        new_verts.append(glm.vec4(x, y, z, 1.0))
                        new_norms.append(n)
                        new_uvs.append(glm.vec2(0.0, 0.0))
                    
                    attempts += 1
            
            print(f"Poisson Sampling: Requested {point_count}, Generated {len(new_verts)} (Radius: {radius:.4f})")

        # Calculate Density (Optional)
        # We store density in the X component of the UV coordinate
        # Simple brute-force density for now (N^2 is okay for N=2000)
        
        positions = [glm.vec3(v.x, v.y, v.z) for v in new_verts]
        densities = []
        search_radius = 0.1 # Adjust based on scale
        search_radius2 = search_radius * search_radius
        
        for i, p in enumerate(positions):
            count = 0
            for j, other_p in enumerate(positions):
                if i == j: continue
                if glm.distance2(p, other_p) < search_radius2:
                    count += 1
            
            # Normalize density (0 to 1 roughly)
            # Max neighbors expected ~ 10-20 depending on radius
            d = min(count / 15.0, 1.0) 
            densities.append(d)
            
        # Update UVs with density
        for i in range(len(new_uvs)):
            new_uvs[i] = glm.vec2(densities[i], 0.0)

        # Create new Shape
        pc_shape = Shape()
        pc_shape.vertices = np.array(new_verts, dtype=np.float32)
        pc_shape.normals = np.array(new_norms, dtype=np.float32)
        pc_shape.colors = np.full((len(new_verts), 4), color, dtype=np.float32)
        pc_shape.uvs = np.array(new_uvs, dtype=np.float32)
        pc_shape.indices = None # Point cloud
        
        # Fix for the "createGeometry" error if it persists or is needed by renderer
        pc_shape.createGeometry = lambda: None 
        
        return pc_shape

    @staticmethod
    def _sample_triangle(v0, v1, v2):
        r1 = random.random()
        r2 = random.random()
        sqrt_r1 = np.sqrt(r1)
        u = 1.0 - sqrt_r1
        v = sqrt_r1 * (1.0 - r2)
        w = sqrt_r1 * r2
        p = u * v0 + v * v1 + w * v2
        n = glm.normalize(p) # Approximate normal
        return p, n
