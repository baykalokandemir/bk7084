import os
from pyglm import glm
import OpenGL.GL as gl
from framework.shapes import UVSphere, Cube, RandomCube, RandomSphere, Car
from framework.objects import MeshObject
from framework.utils.point_cloud_generator import PointCloudGenerator
from framework.gltf_loader import load_gltf
from framework.materials import Material

class SceneManager:
    def __init__(self):
        self.mikoshi_mat = Material(vertex_shader="mikoshi_shader.vert", fragment_shader="mikoshi_shader.frag")
        self.slice_mat = Material(vertex_shader="slice_shader.vert", fragment_shader="slice_shader.frag")
        self.slice_offset = 0.0
        self.objects = []

    def generate_scene(self, config):
        points_list = []
        loaded_objects = []
        
        if config.GLTF_PATH and os.path.exists(config.GLTF_PATH):
            print(f"Loading GLTF: {config.GLTF_PATH}")
            loaded_objects = load_gltf(config.GLTF_PATH)
            
        mode_str = config.SAMPLING_MODES[config.SAMPLING_MODE]
        
        if loaded_objects:
            for obj in loaded_objects:
                if obj.mesh.vertices is None or len(obj.mesh.vertices) == 0:
                    continue
                
                # Apply scale to transform
                transform = glm.scale(obj.transform, glm.vec3(config.GLTF_SCALE))
                
                if config.USE_POINT_CLOUD:
                    # Generate Point Cloud
                    pc_shape = PointCloudGenerator.generate(obj.mesh, config.POINT_COUNT, mode=mode_str)
                    pc_shape.createBuffers()
                    
                    pc_obj = MeshObject(pc_shape, self.mikoshi_mat, transform=transform, draw_mode=gl.GL_POINTS)
                    points_list.append(pc_obj)
                    
                    slice_obj = MeshObject(pc_shape, self.slice_mat, transform=transform, draw_mode=gl.GL_POINTS)
                    points_list.append(slice_obj)
                else:
                    # Use Original Mesh
                    if obj.mesh.VAO is None:
                        obj.mesh.createGeometry()
                        obj.mesh.createBuffers()
                    
                    # Render the Slice Shader on the mesh
                    slice_obj = MeshObject(obj.mesh, self.slice_mat, transform=transform, draw_mode=gl.GL_TRIANGLES)
                    points_list.append(slice_obj)
                
        else:
            # Standard Shapes (Source Meshes)
            source_sphere = UVSphere(radius=0.8)
            source_cube = Cube(side_length=1.6)
            
            # 1. Point Cloud Cube (Mikoshi Mat)
            pc_shape_cube = PointCloudGenerator.generate(source_cube, config.POINT_COUNT, mode=mode_str)
            pc_shape_cube.createBuffers()
            obj1 = MeshObject(pc_shape_cube, self.mikoshi_mat, transform=glm.translate(glm.vec3(-5.0, 0, 0)), draw_mode=gl.GL_POINTS)
            points_list.append(obj1)
            
            # 2. Point Cloud Sphere (Mikoshi Mat)
            pc_shape_sphere = PointCloudGenerator.generate(source_sphere, config.POINT_COUNT, mode=mode_str)
            pc_shape_sphere.createBuffers()
            obj2 = MeshObject(pc_shape_sphere, self.mikoshi_mat, transform=glm.translate(glm.vec3(-3.0, 0, 0)), draw_mode=gl.GL_POINTS)
            points_list.append(obj2)
            
            # 3. Random Cube (Mikoshi Mat)
            random_cube = RandomCube(side_length=1.6, point_count=config.POINT_COUNT*2, mode='regular')
            if random_cube.VAO is None:
                random_cube.createGeometry()
                random_cube.createBuffers()
            obj3 = MeshObject(random_cube, self.mikoshi_mat, transform=glm.translate(glm.vec3(-1.0, 0, 0)), draw_mode=gl.GL_POINTS)
            points_list.append(obj3)
            
            # 4. Random Sphere (Mikoshi Mat)
            random_sphere = RandomSphere(radius=0.8, point_count=config.POINT_COUNT*2, mode='regular')
            if random_sphere.VAO is None:
                random_sphere.createGeometry()
                random_sphere.createBuffers()
            obj4 = MeshObject(random_sphere, self.mikoshi_mat, transform=glm.translate(glm.vec3(1.0, 0, 0)), draw_mode=gl.GL_POINTS)
            points_list.append(obj4)
            
            # 5. Regular Cube with Slice Shader
            if source_cube.VAO is None:
                source_cube.createGeometry()
                source_cube.createBuffers()
            obj5 = MeshObject(source_cube, self.slice_mat, transform=glm.translate(glm.vec3(3.0, 0, 0)), draw_mode=gl.GL_TRIANGLES)
            points_list.append(obj5)
            
            # 6. Regular Sphere with Slice Shader
            if source_sphere.VAO is None:
                source_sphere.createGeometry()
                source_sphere.createBuffers()
            obj6 = MeshObject(source_sphere, self.slice_mat, transform=glm.translate(glm.vec3(5.0, 0, 0)), draw_mode=gl.GL_TRIANGLES)
            points_list.append(obj6)

            # 7. Basic Car (Mikoshi Mat)
            car = Car()
            pc_shape_car = PointCloudGenerator.generate(car, config.POINT_COUNT, mode=mode_str)
            pc_shape_car.createBuffers()
            obj7 = MeshObject(pc_shape_car, self.mikoshi_mat, transform=glm.translate(glm.vec3(0.0, 0, 4.0)), draw_mode=gl.GL_POINTS)
            points_list.append(obj7)

        self.objects = points_list
        # Initial uniform update
        self.update_uniforms(config, 0.0)
        return self.objects

    def update_uniforms(self, config, dt):
        if config.SLICE_ANIMATE:
            self.slice_offset += config.SLICE_SPEED * dt
            
        for obj in self.objects:
            if obj.material == self.mikoshi_mat:
                obj.material.uniforms["enable_glow"] = config.ENABLE_GLOW
                obj.material.uniforms["is_point_mode"] = (obj.draw_mode == gl.GL_POINTS)
                obj.material.uniforms["base_color"] = glm.vec3(*config.POINT_CLOUD_COLOR)
            elif obj.material == self.slice_mat:
                obj.material.uniforms["slice_spacing"] = config.SLICE_SPACING
                obj.material.uniforms["slice_thickness"] = config.SLICE_THICKNESS
                obj.material.uniforms["slice_normal"] = glm.vec3(*config.SLICE_NORMAL)
                obj.material.uniforms["warp_factor"] = config.SLICE_WARP
                obj.material.uniforms["slice_offset"] = self.slice_offset
                obj.material.uniforms["color"] = glm.vec3(*config.SLICE_COLOR)
