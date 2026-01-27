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
            # New Lane Logic
            if not hasattr(edge, 'lanes') or not edge.lanes:
                continue
                
            for lane in edge.lanes:
                # Determine color based on index or direction?
                # We stored Forward first, Backward second in edge.generate_lanes()
                # Lane 0 = Forward, Lane 1 = Backward (usually)
                
                # Check travel direction relative to edge?
                # Lane waypoints are ordered in travel direction.
                # Let's simple check if start point is closer to edge.start or edge.end
                
                start_wp = lane.waypoints[0]
                
                # Just color by index for now to separate them visually if needed, 
                # or assume 0 is Fwd, 1 is Bwd based on our generating logic.
                
                color = c_fwd if lane == edge.lanes[0] else c_bwd
                if len(edge.lanes) > 2:
                     # Fallback for future multi-lane
                     color = c_fwd if (edge.lanes.index(lane) % 2 == 0) else c_bwd

                # Draw Segments
                for i in range(len(lane.waypoints) - 1):
                    p1 = lane.waypoints[i]
                    p2 = lane.waypoints[i+1]
                    
                    v1 = glm.vec4(p1.x, y_off, p1.z, 1.0)
                    v2 = glm.vec4(p2.x, y_off, p2.z, 1.0)
                    
                    verts.append(v1)
                    verts.append(v2)
                    
                    # [MODIFIED] Static Lanes = White (faint)
                    c_white = glm.vec4(1.0, 1.0, 1.0, 0.3)
                    colors.append(c_white)
                    colors.append(c_white)
        
        # [MODIFIED] Removed Curves Loop (Moved to dynamic)
            
        # Pack into Shape
        if not verts: return Shape()
        
        shape.vertices = np.array([v.to_list() for v in verts], dtype=np.float32)
        shape.colors = np.array([c.to_list() for c in colors], dtype=np.float32)
        
        # Set Normals to UP to catch light (Lines don't have real normals)
        shape.normals = np.tile([0.0, 1.0, 0.0], (len(verts), 1)).astype(np.float32)
        
        shape.uvs = np.zeros((len(verts), 2), dtype=np.float32)
        shape.indices = np.array(range(len(verts)), dtype=np.uint32)
        
        return shape

    def generate_dynamic_signals(self, graph):
        """
        [NEW] dynamic traffic signals.
        Returns a Shape containing intersection curves colored by their current signal state.
        This should be called every frame or few frames.
        """
        shape = Shape()
        verts = []
        colors = []
        
        y_off = 0.8 # Same height as lanes
        
        c_green = glm.vec4(0.0, 1.0, 0.0, 1.0)
        c_yellow = glm.vec4(1.0, 1.0, 0.0, 1.0)
        c_red = glm.vec4(1.0, 0.0, 0.0, 1.0)
        
        for node in graph.nodes:
            # We need to map connections (which store geometry) to signal state (which is per Incoming Lane).
            # Connection key is (from_lane_id, to_lane_id)
            
            for key, curve_points in node.connections.items():
                if len(curve_points) < 2: continue
                
                from_lane_id = key[0]
                
                # Get Signal State
                state = node.get_signal(from_lane_id)
                
                # Map Color
                if state == "GREEN":
                    cc = c_green
                elif state == "YELLOW":
                    cc = c_yellow
                else:
                    cc = c_red
                    
                # Draw Curve
                for i in range(len(curve_points) - 1):
                    p1 = curve_points[i]
                    p2 = curve_points[i+1]
                    
                    v1 = glm.vec4(p1.x, y_off, p1.z, 1.0)
                    v2 = glm.vec4(p2.x, y_off, p2.z, 1.0)
                    
                    verts.append(v1)
                    verts.append(v2)
                    colors.append(cc)
                    colors.append(cc)

        # Pack
        if not verts: return Shape()
        
        shape.vertices = np.array([v.to_list() for v in verts], dtype=np.float32)
        shape.colors = np.array([c.to_list() for c in colors], dtype=np.float32)
        shape.normals = np.tile([0.0, 1.0, 0.0], (len(verts), 1)).astype(np.float32)
        shape.uvs = np.zeros((len(verts), 2), dtype=np.float32)
        shape.indices = np.array(range(len(verts)), dtype=np.uint32)
        
        return shape