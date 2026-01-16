from pyglm import glm
from project.vehicle import BaseVehicle
from framework.shapes import Cube, Cylinder
from framework.shapes.trapezoid import Trapezoid
from framework.objects import MeshObject

class CyberpunkCar(BaseVehicle):
    def create_geometry(self):
        # Materials
        # Was (0.1, 0.1, 0.12) - too dark. Lightened for visibility.
        c_body = glm.vec4(0.25, 0.25, 0.3, 1.0) # Dark metallic blue-grey
        c_trim = glm.vec4(0.7, 0.6, 0.3, 1.0) # Gold/Brass trim
        c_mech = glm.vec4(0.15, 0.15, 0.15, 1.0) # Dark mechanical grey
        c_red_glow = glm.vec4(1.0, 0.1, 0.1, 1.0)
        c_cyan_glow = glm.vec4(0.0, 0.8, 1.0, 1.0)
        c_white_glow = glm.vec4(1.0, 1.0, 1.0, 1.0)
        
        # --- 1. CHASSIS / FLOOR ---
        # Main slab
        self.add_box(c_mech, glm.vec3(2.2, 0.4, 4.8), glm.vec3(0, 0.4, 0), self.body_mat)
        
        # Side side skirts (Gold)
        self.add_box(c_trim, glm.vec3(2.3, 0.15, 3.0), glm.vec3(0, 0.2, 0), self.body_mat)
        
        # --- 2. REAR ENGINE / BODY ---
        # Big blocky rear, slight taper
        self.add_box(c_body, glm.vec3(2.2, 0.8, 2.0), glm.vec3(0, 0.9, -1.5), self.body_mat)
        
        # Rear Slats (The "Horizontal Bar Lighting" housing)
        # Creating a stack of horizontal fins at the back
        for i in range(6):
            y = 0.4 + i * 0.12
            # Wide slat
            self.add_box(c_mech, glm.vec3(2.3, 0.05, 0.5), glm.vec3(0, y, -2.5 + i*0.02), self.body_mat)
            
            # Inset Red Light between slats?
            if i % 2 == 0:
                self.add_box(c_red_glow, glm.vec3(2.25, 0.02, 0.5), glm.vec3(0, y + 0.06, -2.5), self.glow_mat)

        # Huge Rear Taillight Bar
        self.add_box(c_red_glow, glm.vec3(2.2, 0.15, 0.1), glm.vec3(0, 1.1, -2.6), self.glow_mat)
        
        # --- 3. CABIN ---
        # Low, sleek, angular
        # Using a trapezoid for the main greenhouse but detailing it with pillars
        
        # Main glasshouse shape
        self.add_trap(c_body, glm.vec3(1.8, 0.6, 2.0), glm.vec3(0, 1.4, 0.2), 0.6, self.body_mat)
        # Windows (inset)
        self.add_trap(c_mech, glm.vec3(1.85, 0.5, 1.8), glm.vec3(0, 1.4, 0.2), 0.65, self.glass_mat)
        
        # Roof Louvers / Detail
        self.add_box(c_body, glm.vec3(1.4, 0.05, 1.5), glm.vec3(0, 1.72, 0), self.body_mat)
        
        # C-Pillar / Flying Buttresses (Triangular supports at back of cabin)
        # Left
        self.add_box(c_body, glm.vec3(0.2, 0.6, 1.0), glm.vec3(-0.9, 1.3, -1.0), self.body_mat)
        # Right
        self.add_box(c_body, glm.vec3(0.2, 0.6, 1.0), glm.vec3(0.9, 1.3, -1.0), self.body_mat)

        # FILLER BLOCK (Fixing the hole in the middle)
        # Fills space between Chassis (top 0.6) and Cabin (bottom ~1.1) / Rear Body
        self.add_box(c_mech, glm.vec3(2.1, 0.8, 2.5), glm.vec3(0, 0.8, -0.2), self.body_mat)

        # --- 4. FRONT HOOD ---
        # Long, low wedge - Extended to meet the cabin/filler
        # Increased length to 3.2 and shifted back to 1.6 to fully intersect windshield base.
        self.add_trap(c_body, glm.vec3(2.1, 0.4, 3.2), glm.vec3(0, 0.9, 1.6), 0.3, self.body_mat)
        
        # Nose detailed block
        self.add_box(c_body, glm.vec3(2.1, 0.3, 0.5), glm.vec3(0, 0.7, 3.4), self.body_mat)
        
        # LOWER CHIN / UNDER-FILL (Filling the triangle under the hood)
        # Tapered block underneath
        self.add_trap(c_mech, glm.vec3(2.0, 0.4, 1.5), glm.vec3(0, 0.4, 2.7), 0.6, self.body_mat)
        
        # Headlights (Thin slits)
        self.add_box(c_white_glow, glm.vec3(2.0, 0.05, 0.1), glm.vec3(0, 0.7, 3.66), self.glow_mat)
        
        # --- 5. FENDERS / WIDEBODY ---
        # Front Fenders (Boxy, vented)
        # L
        self.add_box(c_body, glm.vec3(0.4, 0.5, 1.2), glm.vec3(-1.15, 0.7, 1.8), self.body_mat)
        # Vents on top fender
        self.add_box(c_mech, glm.vec3(0.3, 0.05, 0.8), glm.vec3(-1.15, 0.96, 1.8), self.body_mat)
        
        # R
        self.add_box(c_body, glm.vec3(0.4, 0.5, 1.2), glm.vec3(1.15, 0.7, 1.8), self.body_mat)
        self.add_box(c_mech, glm.vec3(0.3, 0.05, 0.8), glm.vec3(1.15, 0.96, 1.8), self.body_mat)
        
        # Rear Fenders (Wide intakes)
        # L
        self.add_box(c_body, glm.vec3(0.4, 0.6, 1.4), glm.vec3(-1.2, 0.8, -1.5), self.body_mat)
        # Side Intake Slats (Vertical)
        for z in range(3):
            self.add_box(c_mech, glm.vec3(0.1, 0.4, 0.1), glm.vec3(-1.42, 0.8, -1.2 - z*0.2), self.body_mat)
            
        # R
        self.add_box(c_body, glm.vec3(0.4, 0.6, 1.4), glm.vec3(1.2, 0.8, -1.5), self.body_mat)
        for z in range(3):
            self.add_box(c_mech, glm.vec3(0.1, 0.4, 0.1), glm.vec3(1.42, 0.8, -1.2 - z*0.2), self.body_mat)

        # --- 6. SPOILER ---
        # Bi-plane style? Or just big wing.
        # Supports
        self.add_box(c_body, glm.vec3(0.1, 0.4, 0.5), glm.vec3(-1.0, 1.4, -2.5), self.body_mat)
        self.add_box(c_body, glm.vec3(0.1, 0.4, 0.5), glm.vec3(1.0, 1.4, -2.5), self.body_mat)
        # Wing
        self.add_box(c_body, glm.vec3(2.4, 0.05, 0.8), glm.vec3(0, 1.6, -2.6), self.body_mat)
        # Endplates
        self.add_box(c_body, glm.vec3(0.05, 0.3, 0.8), glm.vec3(-1.2, 1.7, -2.6), self.body_mat)
        self.add_box(c_body, glm.vec3(0.05, 0.3, 0.8), glm.vec3(1.2, 1.7, -2.6), self.body_mat)

        # --- 7. WHEELS ---
        # Big chunky tires
        self.add_wheel(0.55, 0.5, glm.vec3(-1.3, 0.55, 1.8))
        self.add_wheel(0.55, 0.5, glm.vec3(1.3, 0.55, 1.8))
        self.add_wheel(0.6, 0.6, glm.vec3(-1.35, 0.6, -1.8))
        self.add_wheel(0.6, 0.6, glm.vec3(1.35, 0.6, -1.8))
        
        # Wheel Covers (Turbofans)
        # Just simple cylinder caps
        # Need rotation logic for covers but I don't have it easily here without custom mesh orientation
        # So I'll just skip covers to keep it simple code-wise but detailed geometry-wise.
