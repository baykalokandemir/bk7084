
import os
import sys
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
from framework.materials import Material
from framework.camera import Flycamera
from framework.utils.polygon import Polygon
from framework.utils.building import Building
from framework.utils.mesh_batcher import MeshBatcher

def main():
    window = OpenGLWindow(1280, 720, "Building Generation Test")
    camera = Flycamera(window.width, window.height, 70, 0.1, 1000.0)
    camera.position = glm.vec3(0, 50, 80)
    camera.euler_angles.x = -30
    glrenderer = GLRenderer(window, camera)
    
    # Lighting
    glrenderer.addLight(PointLight(glm.vec4(50.0, 100.0, 50.0, 1.0), glm.vec4(0.8, 0.8, 0.8, 1.0)))
    
    # Init ImGui
    imgui.create_context()
    impl = GlfwRenderer(window.window, attach_callbacks=False)
    
    # Callbacks
    def key_callback(win, key, scancode, action, mods):
        impl.keyboard_callback(win, key, scancode, action, mods)
        window.key_callback(win, key, scancode, action, mods)
    glfw.set_key_callback(window.window, key_callback)

    def mouse_button_callback(win, button, action, mods):
        if 0 <= button < 5:
            imgui.get_io().mouse_down[button] = (action == glfw.PRESS)
        window.mouse_button_callback(win, button, action, mods)
    glfw.set_mouse_button_callback(window.window, mouse_button_callback)

    # State
    class AppState:
        def __init__(self):
            self.height = 20.0
            self.window_option = 0 # 0: Wide, 1: Narrow, 2: None
            self.corner_option = 0 # 0: Sharp, 1: Chamfered, 2: Rounded
            self.stepped = False
            self.antenna = False
            self.color = [0.8, 0.3, 0.3]
            
            self.current_poly = None
            self.building_obj = None
            
            self.regenerate_footprint()
            self.dirty = True

        def regenerate_footprint(self):
            # Generate random irregular convex quad
            # Start with a centered rectangle and perturb vertices
            w, h = 20, 20
            dx = w/2
            dy = h/2
            
            # -x -y, +x -y, +x +y, -x +y
            base_verts = [
                glm.vec2(-dx, -dy),
                glm.vec2(dx, -dy),
                glm.vec2(dx, dy),
                glm.vec2(-dx, dy)
            ]
            
            new_verts = []
            for v in base_verts:
                # Perturb by random amount
                offset = glm.vec2(random.uniform(-5, 5), random.uniform(-5, 5))
                new_verts.append(v + offset)
                
            self.current_poly = Polygon(new_verts)
            self.dirty = True

    state = AppState()

    def rebuild_scene():
        if not state.dirty: return
        
        # Remove old object
        if state.building_obj and state.building_obj in glrenderer.objects:
            glrenderer.objects.remove(state.building_obj)
            
        # Process Footprint based on Corners
        poly = state.current_poly
        if state.corner_option == 1: # Chamfered
            poly = poly.chamfer(3.0)
        elif state.corner_option == 2: # Rounded
            poly = poly.fillet(3.0, segments=5)
            
        # Style Params
        style = {
            "floor_height": 3.0,
            "window_ratio": 0.6 if state.window_option != 2 else 0.0,
            "inset_depth": 0.5, # Always inset windows
            "color": glm.vec4(state.color[0], state.color[1], state.color[2], 1.0),
            "window_color": glm.vec4(0.2, 0.3, 0.5, 1.0),
            "stepped": state.stepped, 
            "window_style": "vertical_stripes" if state.window_option == 1 else "single"
        }
        
        # If window option is "None", we can just set ratio to 0 or weird hack?
        # Building class doesn't explicitly check "none".
        # If ratio is 0, window height is 0.
        
        building = Building(poly, state.height, style)
        
        # We manually add antenna if requested since Building class does it randomly or based on height
        # Actually Building.generate checks style["stepped"] or just random.
        # Let's inspect Building.generate again.
        # It calls _add_antenna if random < 0.3 for single block.
        # We want explicit control. 
        # We can subclass or just monkeypatch? 
        # Easier: Modifying Building class is not allowed by task description (I only touch test file ideally, unless I need to fix framework).
        # Wait, I CAN modify framework if needed. But let's see if I can force it.
        # Building.generate() has hardcoded random checks for antenna.
        # Lines 58 and 66 in building.py.
        # For this test to work RELIABLY as a demo, I should probably modify Building class to accept an 'antenna' style param.
        # However, I can also just manually add the antenna mesh to the batcher here if the building doesn't have it?
        # But building returns a single Shape.
        
        # Let's first generate the building.
        shape = building.generate()
        
        # If we need to FORCE antenna and Building didn't add it (or to ensure it does), we might need to rely on chance or edit Building.
        # Correct approach: Edit Building Class to respect a flag.
        # But I'll try to stick to the user request "create a new test/scene file".
        # I will assume for now I should NOT modify the framework unless broken.
        # I will implement a helper `add_antenna` in this file and add it to the batcher if checked.
        # This duplicates logic but keeps framework clean.
        
        batcher = MeshBatcher()
        batcher.add_shape(shape)
        
        if state.antenna:
            # Add antenna mesh manually on top
            # Centroid of top face?
            # Building centroid
            c = poly.centroid
            # Height
            h_top = state.height
            
            # Simple Antenna Mesh
            ant_shape = build_antenna_shape(c, h_top)
            batcher.add_shape(ant_shape)
            
        state.building_obj = batcher.build(Material())
        if state.building_obj:
            glrenderer.addObject(state.building_obj)
            
        state.dirty = False

    def build_antenna_shape(pos_2d, y_start):
        # Re-implement antenna logic return Shape
        from framework.shapes.shape import Shape
        s = Shape()
        h = 5.0
        w = 0.2
        p = glm.vec3(pos_2d.x, y_start, pos_2d.y)
        
        verts = []
        norms = []
        cols = []
        inds = []
        
        p1 = p + glm.vec3(-w, 0, -w)
        p2 = p + glm.vec3(w, 0, -w)
        p3 = p + glm.vec3(w, 0, w)
        p4 = p + glm.vec3(-w, 0, w)
        t1 = p1 + glm.vec3(0, h, 0)
        t2 = p2 + glm.vec3(0, h, 0)
        t3 = p3 + glm.vec3(0, h, 0)
        t4 = p4 + glm.vec3(0, h, 0)
        
        col = glm.vec4(0.5, 0.5, 0.5, 1.0)
        
        def add_q(v1, v2, v3, v4, n):
            idx = len(verts)
            verts.extend([glm.vec4(v1, 1.0), glm.vec4(v2, 1.0), glm.vec4(v3, 1.0), glm.vec4(v4, 1.0)])
            norms.extend([n]*4)
            cols.extend([col]*4)
            inds.extend([idx, idx+1, idx+2, idx, idx+2, idx+3])
            
        add_q(p1, p2, t2, t1, glm.vec3(0, 0, -1))
        add_q(p2, p3, t3, t2, glm.vec3(1, 0, 0))
        add_q(p3, p4, t4, t3, glm.vec3(0, 0, 1))
        add_q(p4, p1, t1, t4, glm.vec3(-1, 0, 0))
        
        s.vertices = np.array([v.to_list() for v in verts], dtype=np.float32)
        s.normals = np.array([n.to_list() for n in norms], dtype=np.float32)
        s.colors = np.array([c.to_list() for c in cols], dtype=np.float32)
        s.indices = np.array(inds, dtype=np.uint32)
        s.uvs = np.zeros((len(verts), 2), dtype=np.float32)
        return s

    # Initial build
    rebuild_scene()

    while not glfw.window_should_close(window.window):
        impl.process_inputs()
        camera.update(0.016)
        
        glrenderer.render()
        
        imgui.new_frame()
        imgui.begin("Building Generator")
        
        if imgui.button("Regenerate Footprint"):
            state.regenerate_footprint()
            state.dirty = True
            
        changed, state.height = imgui.slider_float("Height", state.height, 5.0, 100.0)
        if changed: state.dirty = True
        
        # Windows
        items_win = ["Wide", "Narrow", "None"]
        changed, state.window_option = imgui.combo("Windows", state.window_option, items_win)
        if changed: state.dirty = True
        
        # Corners
        items_corn = ["Sharp", "Chamfered", "Rounded"]
        changed, state.corner_option = imgui.combo("Corners", state.corner_option, items_corn)
        if changed: state.dirty = True
        
        changed, state.stepped = imgui.checkbox("Stepped (Tiered)", state.stepped)
        if changed: state.dirty = True
        
        changed, state.antenna = imgui.checkbox("Antenna", state.antenna)
        if changed: state.dirty = True
        
        changed, state.color = imgui.color_edit3("Color", *state.color)
        if changed: state.dirty = True
        
        imgui.end()
        imgui.render()
        impl.render(imgui.get_draw_data())
        
        if state.dirty:
            rebuild_scene()
            
        glfw.swap_buffers(window.window)
        glfw.poll_events()
        
    glfw.terminate()

if __name__ == "__main__":
    main()
