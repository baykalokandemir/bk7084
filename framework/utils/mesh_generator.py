from framework.shapes.shape import Shape
from pyglm import glm
import numpy as np

class MeshGenerator:
    """
    Debug Visualization Tool.
    Primarily used now to visualize the invisible Traffic Graph logic over the BSP geometry.
    """
    def generate_traffic_debug(self, graph):
        """
        Creates a Shape with GL_LINES for traffic lanes.
        Forward Lane (Green): Right of center
        Backward Lane (Red): Left of center
        """
        shape = Shape()
        verts = []
        colors = []
        
        # Colors (Vec4 for Renderer) - Neon
        c_fwd = glm.vec4(0.0, 1.0, 0.2, 1.0) # Neon Green
        c_bwd = glm.vec4(1.0, 0.0, 0.2, 1.0) # Neon Red
        
        y_off = 0.8 # Lift higher above road
        
        for edge in graph.edges:
            # 1. Robust Coordinate Extraction
            # Nodes might store vec3, vec2, or tuples. Force to vec3(x, 0, z)
            def to_vec3(n):
                if hasattr(n, 'x') and hasattr(n, 'y'):
                    return glm.vec3(n.x, 0, n.y) # Assume flat 2D graph logic
                return glm.vec3(n[0], 0, n[1])
                
            p1 = to_vec3(edge.start_node)
            p2 = to_vec3(edge.end_node)
            
            # 2. Check length to prevent NaN
            direction = p2 - p1
            length = glm.length(direction)
            
            if length < 0.1: continue
                
            # 3. Safe Math (using vec3 for calculations)
            dir_norm = glm.normalize(direction)
            # Perpendicular vector (rotate 90 deg around Y) -> (x, 0, z) -> (-z, 0, x)
            perp = glm.vec3(-dir_norm.z, 0, dir_norm.x)
            
            # Offset amount (0.15 of width to pull towards center)
            offset = (edge.width * 0.15)
            
            # 4. Calculate Lane Centers (still vec3)
            # Forward Lane (Right side)
            f_start = p1 + perp * offset
            f_end   = p2 + perp * offset
            
            # Backward Lane (Left side)
            b_start = p1 - perp * offset
            b_end   = p2 - perp * offset
            
            # Lift up
            f_start.y += y_off
            f_end.y   += y_off
            b_start.y += y_off
            b_end.y   += y_off
            
            # 5. Append as Vec4 (Required for Renderer Stride)
            verts.append(glm.vec4(f_start, 1.0))
            verts.append(glm.vec4(f_end, 1.0))
            colors.append(c_fwd)
            colors.append(c_fwd)
            
            verts.append(glm.vec4(b_start, 1.0))
            verts.append(glm.vec4(b_end, 1.0))
            colors.append(c_bwd)
            colors.append(c_bwd)
            
        # Pack into Shape
        if not verts: return Shape()
        
        shape.vertices = np.array([v.to_list() for v in verts], dtype=np.float32)
        shape.colors = np.array([c.to_list() for c in colors], dtype=np.float32)
        
        # Set Normals to UP to catch light (Lines don't have real normals)
        shape.normals = np.tile([0.0, 1.0, 0.0], (len(verts), 1)).astype(np.float32)
        
        shape.uvs = np.zeros((len(verts), 2), dtype=np.float32)
        shape.indices = np.array(range(len(verts)), dtype=np.uint32)
        
        return shape