from pyglm import glm
from framework.shapes.cars.vehicle import BaseVehicle
from framework.shapes import Cube, Cylinder
from framework.shapes.trapezoid import Trapezoid
from framework.objects import MeshObject

import random

class CyberpunkCar(BaseVehicle):
    def regenerate(self):
        self.parts = []
        self.create_geometry()

    def create_geometry(self):
        # --- Randomization Parameters ---
        # 1. Size/Scale Variations
        # Slight variation in overall length/width factors
        len_factor = random.uniform(0.9, 1.15)
        width_factor = random.uniform(0.95, 1.1)
        height_factor = random.uniform(0.95, 1.05)
        
        # 2. Wheel Location (Wheelbase)
        wheel_z_offset = random.uniform(-0.2, 0.3) # Move wheels slightly
        
        # 3. Angles (Trapezoid Taper)
        cabin_taper = random.uniform(0.5, 0.75)
        hood_taper = random.uniform(0.2, 0.5)
        
        # 4. Colors
        # Base palettes
        palettes = [
            # Classic Dark Blue/Grey
            (glm.vec4(0.25, 0.25, 0.3, 1.0), glm.vec4(0.7, 0.6, 0.3, 1.0), glm.vec4(1.0, 0.1, 0.1, 1.0)), 
            # Matte Black + Neon Green
            (glm.vec4(0.1, 0.1, 0.1, 1.0), glm.vec4(0.2, 0.2, 0.2, 1.0), glm.vec4(0.0, 1.0, 0.2, 1.0)),
            # Silver + Cyan
            (glm.vec4(0.6, 0.6, 0.7, 1.0), glm.vec4(0.3, 0.3, 0.3, 1.0), glm.vec4(0.0, 0.8, 1.0, 1.0)),
            # Military Green + Orange
            (glm.vec4(0.2, 0.3, 0.2, 1.0), glm.vec4(0.1, 0.1, 0.1, 1.0), glm.vec4(1.0, 0.5, 0.0, 1.0)),
            # Rusty/Red + White
            (glm.vec4(0.4, 0.2, 0.2, 1.0), glm.vec4(0.3, 0.3, 0.3, 1.0), glm.vec4(1.0, 1.0, 1.0, 1.0)),
        ]
        
        selected_palette = random.choice(palettes)
        c_body = selected_palette[0]
        c_trim = selected_palette[1]
        c_main_glow = selected_palette[2] # Primary accent light (rear/accents)
        
        c_mech = glm.vec4(0.15, 0.15, 0.15, 1.0) # Dark mechanical grey constant
        c_headlight = glm.vec4(0.9, 0.9, 1.0, 1.0) # White-ish headlights
        
        # 5. Headlight Shape
        headlight_type = random.choice(['slit', 'circle', 'square', 'dual_slit'])
        
        # --- GEOMETRY CONSTRUCTION ---
        
        # --- 1. CHASSIS / FLOOR ---
        # Main slab
        chassis_len = 4.8 * len_factor
        chassis_width = 2.2 * width_factor
        self.add_box(c_mech, glm.vec3(chassis_width, 0.4, chassis_len), glm.vec3(0, 0.4, 0), self.body_mat)
        
        # Side side skirts
        # Adjust length relative to chassis
        self.add_box(c_trim, glm.vec3(chassis_width + 0.1, 0.15, chassis_len * 0.6), glm.vec3(0, 0.2, 0), self.body_mat)
        
        # --- 2. REAR ENGINE / BODY ---
        rear_len = 2.0 * len_factor
        rear_z_pos = -1.5 * len_factor
        
        self.add_box(c_body, glm.vec3(chassis_width, 0.8 * height_factor, rear_len), glm.vec3(0, 0.9 * height_factor, rear_z_pos), self.body_mat)
        
        # Rear Slats (The "Horizontal Bar Lighting" housing)
        num_slats = random.randint(4, 7)
        for i in range(num_slats):
            y = 0.4 + i * 0.12
            # Wide slat
            # Adjust z slightly based on count
            slat_z = (rear_z_pos - (rear_len/2)) + (i * 0.02) - 0.2 
            self.add_box(c_mech, glm.vec3(chassis_width + 0.1, 0.05, 0.5), glm.vec3(0, y, slat_z), self.body_mat)
            
            # Inset Glow Light between slats
            if i % 2 == 0:
                self.add_box(c_main_glow, glm.vec3(chassis_width + 0.05, 0.02, 0.5), glm.vec3(0, y + 0.06, slat_z), self.glow_mat)

        # Huge Rear Taillight Bar
        self.add_box(c_main_glow, glm.vec3(chassis_width, 0.15, 0.1), glm.vec3(0, 1.1 * height_factor, rear_z_pos - (rear_len/2) - 0.1), self.glow_mat)
        
        # --- 3. CABIN ---
        # Using a trapezoid for the main greenhouse but detailing it with pillars
        cabin_width = 1.8 * width_factor
        cabin_len = 2.0 * len_factor
        cabin_z = 0.2
        cabin_h = 0.6 * height_factor
        
        # Main glasshouse shape
        self.add_trap(c_body, glm.vec3(cabin_width, cabin_h, cabin_len), glm.vec3(0, 1.4 * height_factor, cabin_z), cabin_taper, self.body_mat)
        # Windows (inset)
        self.add_trap(c_mech, glm.vec3(cabin_width + 0.05, cabin_h - 0.1, cabin_len - 0.2), glm.vec3(0, 1.4 * height_factor, cabin_z), cabin_taper + 0.05, self.glass_mat)
        
        # Roof Louvers / Detail
        self.add_box(c_trim, glm.vec3(cabin_width * 0.8, 0.05, cabin_len * 0.8), glm.vec3(0, (1.4 * height_factor) + (cabin_h/2) + 0.02, cabin_z), self.body_mat)
        
        # Left
        buttress_x = (cabin_width / 2)
        self.add_box(c_body, glm.vec3(0.2, cabin_h, cabin_len/2), glm.vec3(-buttress_x, 1.3 * height_factor, cabin_z - cabin_len/2 - 0.2), self.body_mat)
        # Right
        self.add_box(c_body, glm.vec3(0.2, cabin_h, cabin_len/2), glm.vec3(buttress_x, 1.3 * height_factor, cabin_z - cabin_len/2 - 0.2), self.body_mat)

        # FILLER BLOCK
        self.add_box(c_mech, glm.vec3(chassis_width - 0.1, 0.8 * height_factor, 2.5 * len_factor), glm.vec3(0, 0.8 * height_factor, -0.2), self.body_mat)

        # --- 4. FRONT HOOD ---
        # Long, low wedge - Extended to meet the cabin/filler
        hood_len = 3.2 * len_factor
        hood_z = 1.6 * len_factor
        
        self.add_trap(c_body, glm.vec3(chassis_width - 0.1, 0.4 * height_factor, hood_len), glm.vec3(0, 0.9 * height_factor, hood_z), hood_taper, self.body_mat)
        
        # Nose detailed block
        nose_z = hood_z + (hood_len/2) + 0.2
        self.add_box(c_body, glm.vec3(chassis_width - 0.1, 0.3, 0.5), glm.vec3(0, 0.7 * height_factor, nose_z), self.body_mat)
        
        # LOWER CHIN / UNDER-FILL (Filling the triangle under the hood)
        # Tapered block underneath
        self.add_trap(c_mech, glm.vec3(chassis_width - 0.2, 0.4, 1.5), glm.vec3(0, 0.4, hood_z + 1.0), 0.6, self.body_mat)
        
        # --- HEADLIGHTS ---
        # Randomized headlight shapes
        hl_z_pos = nose_z + 0.26
        
        if headlight_type == 'slit':
            self.add_box(c_headlight, glm.vec3(chassis_width - 0.2, 0.05, 0.1), glm.vec3(0, 0.7 * height_factor, hl_z_pos), self.glow_mat)
            
        elif headlight_type == 'dual_slit':
            # Two thin lines stacked
            self.add_box(c_headlight, glm.vec3(chassis_width - 0.2, 0.03, 0.1), glm.vec3(0, (0.7 * height_factor) + 0.05, hl_z_pos), self.glow_mat)
            self.add_box(c_headlight, glm.vec3(chassis_width - 0.2, 0.03, 0.1), glm.vec3(0, (0.7 * height_factor) - 0.05, hl_z_pos), self.glow_mat)

        elif headlight_type == 'square':
            # Two blocky lights
             self.add_box(c_headlight, glm.vec3(0.4, 0.15, 0.1), glm.vec3(-(chassis_width/2)+0.6, 0.7 * height_factor, hl_z_pos), self.glow_mat)
             self.add_box(c_headlight, glm.vec3(0.4, 0.15, 0.1), glm.vec3((chassis_width/2)-0.6, 0.7 * height_factor, hl_z_pos), self.glow_mat)
             
        elif headlight_type == 'circle':
            # Cylinder headlights
            # Left
            self.add_wheel(0.15, 0.2, glm.vec3(-(chassis_width/2)+0.6, 0.7 * height_factor, hl_z_pos))

            # Quad lights
            for off in [-0.2, 0.2]:
                 self.add_box(c_headlight, glm.vec3(0.15, 0.15, 0.1), glm.vec3(-(chassis_width/2)+0.6 + off, 0.7 * height_factor, hl_z_pos), self.glow_mat)
                 self.add_box(c_headlight, glm.vec3(0.15, 0.15, 0.1), glm.vec3((chassis_width/2)-0.6 + off, 0.7 * height_factor, hl_z_pos), self.glow_mat)


        # --- 5. FENDERS / WIDEBODY ---
        # Front Fenders (Boxy, vented)
        fender_x = (chassis_width / 2) + 0.05
        fender_z = 1.8 + wheel_z_offset
        
        # L
        self.add_box(c_body, glm.vec3(0.4, 0.5, 1.2), glm.vec3(-fender_x, 0.7, fender_z), self.body_mat)
        self.add_box(c_mech, glm.vec3(0.3, 0.05, 0.8), glm.vec3(-fender_x, 0.96, fender_z), self.body_mat)
        
        # R
        self.add_box(c_body, glm.vec3(0.4, 0.5, 1.2), glm.vec3(fender_x, 0.7, fender_z), self.body_mat)
        self.add_box(c_mech, glm.vec3(0.3, 0.05, 0.8), glm.vec3(fender_x, 0.96, fender_z), self.body_mat)
        
        # Rear Fenders (Wide intakes)
        rear_fender_z = -1.5 + wheel_z_offset
        # L
        self.add_box(c_body, glm.vec3(0.4, 0.6, 1.4), glm.vec3(-fender_x - 0.05, 0.8, rear_fender_z), self.body_mat)
        # Side Intake Slats (Vertical)
        for z in range(3):
            self.add_box(c_mech, glm.vec3(0.1, 0.4, 0.1), glm.vec3(-fender_x - 0.27, 0.8, rear_fender_z + 0.3 - z*0.2), self.body_mat)
            
        # R
        self.add_box(c_body, glm.vec3(0.4, 0.6, 1.4), glm.vec3(fender_x + 0.05, 0.8, rear_fender_z), self.body_mat)
        for z in range(3):
            self.add_box(c_mech, glm.vec3(0.1, 0.4, 0.1), glm.vec3(fender_x + 0.27, 0.8, rear_fender_z + 0.3 - z*0.2), self.body_mat)

        # --- 6. SPOILER ---
        # Randomize spoiler type
        spoiler_type = random.choice(['wing', 'ducktail', 'none'])
        
        if spoiler_type == 'wing':
            # Supports
            self.add_box(c_body, glm.vec3(0.1, 0.4, 0.5), glm.vec3(-0.8, 1.4 * height_factor, rear_z_pos - 1.0), self.body_mat)
            self.add_box(c_body, glm.vec3(0.1, 0.4, 0.5), glm.vec3(0.8, 1.4 * height_factor, rear_z_pos - 1.0), self.body_mat)
            # Wing
            self.add_box(c_body, glm.vec3(chassis_width + 0.2, 0.05, 0.8), glm.vec3(0, 1.6 * height_factor, rear_z_pos - 1.1), self.body_mat)
            # Endplates
            self.add_box(c_body, glm.vec3(0.05, 0.3, 0.8), glm.vec3(-(chassis_width/2)-0.1, 1.7 * height_factor, rear_z_pos - 1.1), self.body_mat)
            self.add_box(c_body, glm.vec3(0.05, 0.3, 0.8), glm.vec3((chassis_width/2)+0.1, 1.7 * height_factor, rear_z_pos - 1.1), self.body_mat)
        
        elif spoiler_type == 'ducktail':
             self.add_trap(c_body, glm.vec3(chassis_width, 0.4, 0.5), glm.vec3(0, 1.2 * height_factor, rear_z_pos - 1.0), 0.7, self.body_mat)

        # --- 7. WHEELS ---
        # Big chunky tires
        # Scale wheel size slightly
        wheel_radius = random.uniform(0.5, 0.65)
        wheel_width = random.uniform(0.5, 0.6)
        
        wheel_x_offset = (chassis_width / 2) + 0.2
        
        self.add_wheel(wheel_radius, wheel_width, glm.vec3(-wheel_x_offset, wheel_radius, fender_z))
        self.add_wheel(wheel_radius, wheel_width, glm.vec3(wheel_x_offset, wheel_radius, fender_z))
        self.add_wheel(wheel_radius, wheel_width, glm.vec3(-wheel_x_offset - 0.05, wheel_radius, rear_fender_z))
        self.add_wheel(wheel_radius, wheel_width, glm.vec3(wheel_x_offset + 0.05, wheel_radius, rear_fender_z))
