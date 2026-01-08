import math
import numpy as np
from pyglm import glm
import OpenGL.GL as gl
from framework.shapes.shape import Shape

class MeshGenerator:
    """
    Converts a CityGraph into 3D meshes using the Hub & Spoke method.
    """
    def generate(self, graph):
        meshes = []
        
        # 1. Generate Hubs (Nodes)
        for node in graph.nodes:
            # Determine radius based on connected edges
            max_width = 0
            for edge in node.edges:
                if edge.width > max_width:
                    max_width = edge.width
            
            # Hub Radius
            # Radius = max(connected_road_widths) / 2
            hub_radius = max_width / 2.0
            if hub_radius < 1.0: hub_radius = 5.0 # Default min size
            
            # Store radius on node for edge generation later
            node.hub_radius = hub_radius
            
            # Create Circle Mesh
            meshes.append(self._create_circle_mesh(node.x, node.y, hub_radius))
            
        # 2. Generate Spokes (Edges)
        for edge in graph.edges:
            # Get start/end hub radii
            r1 = getattr(edge.start_node, 'hub_radius', 0)
            r2 = getattr(edge.end_node, 'hub_radius', 0)
            
            # Create Rect Mesh
            meshes.append(self._create_road_segment(edge, r1, r2))
            
        return meshes

    def generate_debug_lines(self, graph):
        """
        Creates a single Shape containing GL_LINES for all edges in the graph.
        Useful for debugging graph connectivity without Hub & Spoke geometry.
        """
        shape = Shape()
        verts = []
        colors = []
        
        y_height = 0.5 # Lift off ground slightly
        
        for edge in graph.edges:
            p1 = edge.start_node
            p2 = edge.end_node
            
            verts.append(glm.vec3(p1.x, y_height, p1.y))
            verts.append(glm.vec3(p2.x, y_height, p2.y))
            
            col = glm.vec4(1.0, 1.0, 0.0, 1.0) # Yellow lines
            colors.append(col)
            colors.append(col)
            
        shape.vertices = np.array([v.to_list() for v in verts], dtype=np.float32)
        shape.colors = np.array([c.to_list() for c in colors], dtype=np.float32)
        
        # No normals/uvs needed for lines usually, but good to have empty placeholders
        shape.normals = np.zeros((len(verts), 3), dtype=np.float32)
        shape.uvs = np.zeros((len(verts), 2), dtype=np.float32)
        shape.indices = np.array(range(len(verts)), dtype=np.uint32) # Sequential
        
        return shape

    def _create_circle_mesh(self, x, y, radius, segments=16):
        shape = Shape()
        verts = []
        norms = []
        uvs = []
        
        # Center vertex
        # Slightly elevated to overlap cleanly
        y_height = 0.05
        
        # Triangle Fan
        # Center - CHANGE: vec3 -> vec4
        verts.append(glm.vec4(x, y_height, y, 1.0))
        norms.append(glm.vec3(0, 1, 0))
        uvs.append(glm.vec2(0.5, 0.5))
        
        # Rim
        for i in range(segments + 1):
            theta = (i / segments) * 2 * math.pi
            px = x + math.cos(theta) * radius
            py = y + math.sin(theta) * radius
            
            # CHANGE: vec3 -> vec4
            verts.append(glm.vec4(px, y_height, py, 1.0))
            norms.append(glm.vec3(0, 1, 0))
            uvs.append(glm.vec2(0.5 + 0.5*math.cos(theta), 0.5 + 0.5*math.sin(theta)))
            
        # Indices
        inds = []
        for i in range(segments):
            inds.extend([0, i+1, i+2])
            
        # Color (Dark Gray for asphalt)
        cols = [glm.vec4(0.2, 0.2, 0.2, 1.0)] * len(verts)
        
        shape.vertices = np.array([v.to_list() for v in verts], dtype=np.float32)
        shape.normals = np.array([n.to_list() for n in norms], dtype=np.float32)
        shape.uvs = np.array([u.to_list() for u in uvs], dtype=np.float32)
        shape.colors = np.array([c.to_list() for c in cols], dtype=np.float32)
        shape.indices = np.array(inds, dtype=np.uint32)
        
        return shape

    def _create_road_segment(self, edge, r1, r2):
        # Calculate start and end points shortened by radii
        p1 = glm.vec2(edge.start_node.x, edge.start_node.y)
        p2 = glm.vec2(edge.end_node.x, edge.end_node.y)
        
        direction = p2 - p1
        dist = glm.length(direction)
        if dist < 0.001: return Shape() # Zero length edge
        
        dir_norm = glm.normalize(direction)
        
        # Shorten
        start_pos = p1 + dir_norm * r1
        end_pos = p2 - dir_norm * r2
        
        # If radii overlap (segment too short), adjust
        if r1 + r2 > dist:
            mid = (p1 + p2) * 0.5
            start_pos = mid
            end_pos = mid
        
        # Perpendicular for width
        perp = glm.vec2(-dir_norm.y, dir_norm.x)
        half_w = edge.width / 2.0
        
        # 4 Corners
        # Start Left, Start Right, End Right, End Left
        sl = start_pos + perp * half_w
        sr = start_pos - perp * half_w
        er = end_pos - perp * half_w
        el = end_pos + perp * half_w
        
        y_height = 0.05
        
        # CHANGE: vec3 -> vec4
        v1 = glm.vec4(sl.x, y_height, sl.y, 1.0)
        v2 = glm.vec4(sr.x, y_height, sr.y, 1.0)
        v3 = glm.vec4(er.x, y_height, er.y, 1.0)
        v4 = glm.vec4(el.x, y_height, el.y, 1.0)
        
        shape = Shape()
        verts = [v1, v2, v3, v4]
        norms = [glm.vec3(0,1,0)] * 4
        uvs = [glm.vec2(0,0), glm.vec2(1,0), glm.vec2(1,1), glm.vec2(0,1)]
        cols = [glm.vec4(0.2, 0.2, 0.2, 1.0)] * 4
        inds = [0, 1, 2, 0, 2, 3]
        
        shape.vertices = np.array([v.to_list() for v in verts], dtype=np.float32)
        shape.normals = np.array([n.to_list() for n in norms], dtype=np.float32)
        shape.uvs = np.array([u.to_list() for u in uvs], dtype=np.float32)
        shape.colors = np.array([c.to_list() for c in cols], dtype=np.float32)
        shape.indices = np.array(inds, dtype=np.uint32)
        
        return shape