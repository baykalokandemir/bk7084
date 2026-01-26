from pyglm import glm
import OpenGL.GL as gl
from .grid_point_cloud_generator import GridPointCloudGenerator
from ..objects import MeshObject
from ..materials import Material

class HologramWrapper:
    # Shared material instance (created on demand or passed in? better to create fresh or reuse carefully)
    # Since material has uniforms that might be unique per object instance (like base_color, point_size),
    # we should create a new Material instance for each Hologram to allow independent control.
    # OR we use MeshObject's ability to override uniforms if supported. 
    # framework/objects.py MeshObject usually shares material but uniforms are stored in material.
    # If we share material object, changing one color changes all.
    # So we must create a NEW Material instance for each hologram.
    
    @staticmethod
    def create(source_shape, 
               spacing=0.2, 
               color=glm.vec3(0.0, 0.9, 1.0), 
               point_size=10.0, 
               point_shape=0, # 0: Circle, 1: Square
               enable_glow=True,
               transform=glm.mat4(1.0)):
        """
        Creates a MeshObject configured as a Hologram (Point Cloud) from a source shape.
        
        Args:
            source_shape: The input Shape object (Mesh).
            spacing (float): Grid spacing for point generation. Default 0.2.
            color (glm.vec3): Hologram color (RGB). Default Cyan.
            point_size (float): Size of points. Default 10.0.
            point_shape (int): 0 for Circle, 1 for Square. Default 0.
            enable_glow (bool): Whether to enable the glow effect. Default True.
            transform (glm.mat4): Initial transform matrix.
            
        Returns:
            MeshObject: The ready-to-render hologram object.
        """
        
        # 1. Generate Point Cloud Geometry
        pc_shape = GridPointCloudGenerator.generate(source_shape, spacing=spacing)
        pc_shape.createBuffers()
        
        # 2. Create Unique Material Instance
        # This ensures each hologram can have its own color/settings
        mat = Material(vertex_shader="mikoshi_shader.vert", fragment_shader="mikoshi_shader.frag")
        
        # 3. Configure Material Uniforms (Defaults)
        mat.uniforms["enable_glow"] = enable_glow
        mat.uniforms["is_point_mode"] = True
        mat.uniforms["base_color"] = color
        mat.uniforms["point_size"] = point_size
        mat.uniforms["shape_type"] = point_shape
        mat.uniforms["anim_x"] = True # Always animate
        mat.uniforms["anim_y"] = True # Always animate
        
        # Time needs to be updated per frame by the main loop. 
        # We'll initialize it to 0.
        mat.uniforms["time"] = 0.0
        
        # 4. Create and Return MeshObject
        obj = MeshObject(pc_shape, mat, transform=transform, draw_mode=gl.GL_POINTS)
        
        return obj
