import os
import sys
import math
import random
import numpy as np

# Add framework to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

import glfw
import glm
import imgui
from imgui.integrations.glfw import GlfwRenderer

from framework.window import OpenGLWindow
from framework.renderer import GLRenderer
from framework.light import PointLight
from framework.utils.advanced_city_generator import AdvancedCityGenerator
from framework.utils.mesh_batcher import MeshBatcher
from framework.utils.street_light import StreetLight
from framework.utils.road_network import RoadNetwork
from framework.materials import Material
from framework.camera import Flycamera

class CityBuilder:
    def __init__(self):
        self.width = 400.0
        self.depth = 400.0
        self.split_blocks = True
        self.use_diagonals = False
        self.add_town_square = False
        self.generate_roads = False
        self.generate_sidewalks = False
        self.generate_street_lights = False
        
        self.generator = None
        self.batcher = None
        self.city_object = None
        self.lights = []
        
        # Internal state
        self.polygons_to_draw = [] # For debugging/visualizing logical blocks if no meshes
        
    def build(self, renderer):
        # Initialize Core Generator
        # We set min_block_area higher to make it clearer for demo? Or keep default.
        # ortho_chance: 1.0 if not use_diagonals else 0.4?
        ortho = 0.4 if self.use_diagonals else 1.0
        
        gen = AdvancedCityGenerator(width=self.width, depth=self.depth, ortho_chance=ortho)
        
        # Re-initialize lists manually to match our custom flow
        gen.blocks = []
        gen.roads = []
        gen.sidewalks = []
        gen.street_light_poses = []
        gen.road_network = RoadNetwork()
        
        self.polygons_to_draw = []
        
        # 1. Town Square (Optional)
        if self.add_town_square:
            city_sectors, town_square_poly = gen._create_town_square(gen.root)
            
            # If town square exists, we might want to visualize it
            # The 'town_square_poly' is the center hole.
            
            # Add Town Square Road Ring logic manually if needed or copy from generator
            if town_square_poly and self.generate_roads:
                verts = town_square_poly.vertices
                n = len(verts)
                for i in range(n):
                    v1 = verts[i]
                    v2 = verts[(i+1)%n]
                    gen.road_network.add_segment(v1, v2, 14.0, 4)
                    
            # Park/Sidewalk logic for Town Square
            if town_square_poly and self.generate_sidewalks:
                 half_road_w = 7.0
                 sidewalk_w = 4.0
                 sidewalk_outer = town_square_poly.inset(half_road_w)
                 sidewalk_inner = sidewalk_outer.inset(sidewalk_w)
                 gen._generate_sidewalk(sidewalk_outer, sidewalk_inner)
                 # Park
                 park_poly = sidewalk_inner
                 park_shape = park_poly.extrude(0.5)
                 # Green
                 park_shape.colors = np.array([[0.2, 0.8, 0.2, 1.0]] * len(park_shape.vertices), dtype=np.float32)
                 gen.parks.append(park_shape)
                 
        else:
            city_sectors = [gen.root]
            
        # 2. Split Blocks (Optional? The user said "split city into blocks")
        # If disabled, we just have the sectors.
        raw_blocks = []
        if self.split_blocks:
            for sector in city_sectors:
                gen._split_city_recursive(sector, raw_blocks, 1)
        else:
            raw_blocks = city_sectors
            
        # Visualize Raw Blocks (Logical Layout) if roads not generated?
        # Or always visualize them if we don't have road meshes yet?
        # If we generate roads, we draw roads. If we generate sidewalks, we draw sidewalks/blocks.
        # Let's save raw_blocks to draw them as debug shapes if we want.
        self.polygons_to_draw.extend(raw_blocks)
            
        # 3. Roads
        if self.generate_roads:
            if gen.road_network:
                road_meshes, road_edges = gen.road_network.generate_meshes()
                gen.roads.extend(road_meshes)
                
                # 4. Street Lights (Only if roads exist)
                if self.generate_street_lights:
                    # Copy pasting light generation logic
                    light_spacing = 25.0
                    sidewalk_offset = 0.5 
                    
                    for edge in road_edges:
                        start = edge['start']
                        end = edge['end']
                        normal = edge['normal']
                        vec = end - start
                        length = glm.length(vec)
                        direction = glm.normalize(vec)
                        curr_dist = light_spacing * 0.5
                        while curr_dist < length:
                            pos = start + direction * curr_dist
                            pos += normal * sidewalk_offset
                            target_x = -normal
                            target_y = glm.vec3(0, 1, 0)
                            target_z = glm.normalize(glm.cross(target_x, target_y))
                            rot = glm.mat4(
                                glm.vec4(target_x, 0.0),
                                glm.vec4(target_y, 0.0),
                                glm.vec4(target_z, 0.0),
                                glm.vec4(0, 0, 0, 1.0)
                            )
                            # Create translation matrix
                            trans = glm.translate(pos)
                            gen.street_light_poses.append(trans * rot)
                            curr_dist += light_spacing

        # 5. Sidewalks (and Blocks shrinking)
        if self.generate_sidewalks:
            final_blocks = []
            for raw_block in raw_blocks:
                # Shrink to create road gaps
                curb_poly = raw_block.inset(3.0)
                block = curb_poly.inset(2.0)
                final_blocks.append(block)
                
                gen._generate_sidewalk(curb_poly, block)
            
            # Update what we visualize for blocks
            self.polygons_to_draw = final_blocks
            
        self.generator = gen
        self._update_renderer(renderer)
        
    def _update_renderer(self, renderer):
        # Clear old object
        if self.city_object and self.city_object in renderer.objects:
            renderer.objects.remove(self.city_object)
        
        batcher = MeshBatcher()
        
        # 1. Blocks / Polygons
        # If we have sidewalks, 'polygons_to_draw' are the inner blocks (lots).
        # If we don't, they are raw blocks. 
        # We can draw them as flat shapes.
        for poly in self.polygons_to_draw:
            # Extrude slightly or just flat mesh?
            # Let's extrude 0.1 to be visible
            shape = poly.extrude(0.1)
            # Random color
            col = glm.vec4(random.uniform(0.3, 0.5), random.uniform(0.3, 0.5), random.uniform(0.3, 0.5), 1.0)
            batcher.add_shape(shape, color=col)
            
        # 2. Roads
        for shape in self.generator.roads:
            batcher.add_shape(shape)
            
        # 3. Sidewalks
        for shape in self.generator.sidewalks:
            batcher.add_shape(shape)
            
        # 4. Parks
        for shape in self.generator.parks:
            col = glm.vec4(0.2, 0.8, 0.2, 1.0)
            batcher.add_shape(shape, color=col)
            
        # 5. Street Lights
        all_bulb_positions = []
        if self.generate_street_lights and len(self.generator.street_light_poses) > 0:
            sl_gen = StreetLight()
            sl_shape = sl_gen.generate_mesh()
             
            for pose in self.generator.street_light_poses:
                # Validate pose
                is_valid = True
                for c in range(4):
                    for r in range(4):
                        if math.isnan(pose[c][r]) or math.isinf(pose[c][r]):
                            is_valid = False
                if is_valid:
                    batcher.add_shape(sl_shape, transform=pose)
                    bulb_local = glm.vec4(sl_gen.bulb_offset, 1.0)
                    bulb_world = pose * bulb_local
                    all_bulb_positions.append(bulb_world)
                    
        self.lights = all_bulb_positions
        
        self.city_object = batcher.build(Material())
        if self.city_object:
            renderer.addObject(self.city_object)


def main():
    window = OpenGLWindow(1280, 720, "City Gen Step-by-Step")
    camera = Flycamera(window.width, window.height, 70, 0.1, 1000.0)
    camera.position = glm.vec3(0, 150, 150)
    camera.euler_angles.x = -60
    glrenderer = GLRenderer(window, camera)
    
    # Sun
    glrenderer.addLight(PointLight(glm.vec4(100.0, 200.0, 100.0, 1.0), glm.vec4(0.8, 0.8, 0.8, 1.0)))
    
    imgui.create_context()
    impl = GlfwRenderer(window.window, attach_callbacks=False)
    
    # Input callbacks
    def key_callback(win, key, scancode, action, mods):
        impl.keyboard_callback(win, key, scancode, action, mods)
        window.key_callback(win, key, scancode, action, mods)
    glfw.set_key_callback(window.window, key_callback)

    def mouse_button_callback(win, button, action, mods):
        if 0 <= button < 5:
            imgui.get_io().mouse_down[button] = (action == glfw.PRESS)
        window.mouse_button_callback(win, button, action, mods)
    glfw.set_mouse_button_callback(window.window, mouse_button_callback)
    
    builder = CityBuilder()
    builder.build(glrenderer)
    
    while not glfw.window_should_close(window.window):
        impl.process_inputs()
        camera.update(0.016)
        
        # Dynamic Lighting
        base_lights = [glrenderer.lights[0]] if glrenderer.lights else []
        active = list(base_lights)
        
        if builder.lights:
            # Sort by dist
            cam_p = camera.position
            def dist_key(lp):
                d = glm.vec3(lp) - cam_p
                return glm.dot(d, d)
            
            sorted_bulbs = sorted(builder.lights, key=dist_key)
            for b in sorted_bulbs[:8]:
                active.append(PointLight(b, glm.vec4(1.0, 0.9, 0.7, 1.0)))
        
        glrenderer.lights = active
        glrenderer.render()
        
        # GUI
        imgui.new_frame()
        imgui.begin("City Generation Controls")
        
        changed = False
        
        # A) Size
        _, builder.width = imgui.slider_float("Width", builder.width, 100.0, 1000.0)
        _, builder.depth = imgui.slider_float("Depth", builder.depth, 100.0, 1000.0)
        if _ : changed = True
        
        # B) Split Blocks
        _, builder.split_blocks = imgui.checkbox("Split into Blocks", builder.split_blocks)
        if _ : changed = True
        
        # C) Diagonals
        if builder.split_blocks:
            _, builder.use_diagonals = imgui.checkbox("Enable Diagonal Splits", builder.use_diagonals)
            if _ : changed = True
            
        # D) Center Hexagon
        _, builder.add_town_square = imgui.checkbox("Add Center Hexagon/Square", builder.add_town_square)
        if _ : changed = True
        
        imgui.separator()
        
        # E) Roads
        _, builder.generate_roads = imgui.checkbox("Generate Roads (Mesh)", builder.generate_roads)
        if _ : changed = True
        
        # F) Sidewalks
        _, builder.generate_sidewalks = imgui.checkbox("Add Sidewalks", builder.generate_sidewalks)
        if _ : changed = True
        
        # G) Lamps
        _, builder.generate_street_lights = imgui.checkbox("Add Street Lamps", builder.generate_street_lights)
        if _ : changed = True
        
        if imgui.button("Regenerate Force"):
            changed = True
            
        if changed:
            builder.build(glrenderer)
            
        imgui.end()
        imgui.render()
        impl.render(imgui.get_draw_data())
        
        glfw.swap_buffers(window.window)
        glfw.poll_events()
        
    glfw.terminate()

if __name__ == "__main__":
    main()
