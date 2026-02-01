from .mesh_object import MeshObject
from ..shapes.uvsphere import UVSphere
from ..materials.material import Material
from ..light import DirectionalLight
import glm
import math
import OpenGL.GL as gl

class Skybox(MeshObject):
    def __init__(self, time_scale=1.0):
        # 1. Geometry: Large Sphere
        # High segment count for smooth gradient/sun movement if we used vertex shader for it, 
        # but we use pixel shader, so stacks can be lower.
        mesh = UVSphere(radius=10.0, stacks=32, slices=32) 
        
        # 2. Material
        mat = Material(vertex_shader="skybox.vert", fragment_shader="skybox.frag")
        mat.uniforms["topColor"] = glm.vec3(0.0)
        mat.uniforms["bottomColor"] = glm.vec3(0.0) 
        mat.uniforms["sunPosition"] = glm.vec3(0.0, 1.0, 0.0)
        mat.uniforms["moonPosition"] = glm.vec3(0.0, -1.0, 0.0)
        
        super().__init__(mesh, mat)
        
        # 3. State
        self.time_scale = time_scale
        self.current_time = 8.0 # Start at 8 AM
        self.day_duration = 24.0
        
        # 4. Light Sources (Managed by Skybox)
        # Rays coming DOWN (-Y)
        self.sun_light = DirectionalLight(direction=glm.vec3(0, -1, 0), color=glm.vec4(1.0, 0.95, 0.9, 1.2))
        self.moon_light = DirectionalLight(direction=glm.vec3(0, 1, 0), color=glm.vec4(0.1, 0.15, 0.3, 0.3))
        
    def update(self, dt):
        self.current_time += dt * self.time_scale
        self.current_time %= self.day_duration
        
        # 0 = Midnight, 6 = Sunrise, 12 = Noon, 18 = Sunset
        # Angle 0 = Sunrise (East, +X), PI/2 = Noon (+Y)
        
        # Map time to angle: (Time - 6) * (2PI / 24)
        noon_offset = 6.0
        angle = ((self.current_time - noon_offset) / 24.0) * math.pi * 2.0
        
        
        orbit_radius = 1.0
        # Noon (Angle pi/2): sin=1 => +Y (Up).
        sun_dir = glm.vec3(math.cos(angle), math.sin(angle), 0.1) 
        sun_dir = glm.normalize(sun_dir)
        
        # Update Lights
        self.sun_light.direction = -sun_dir
        self.moon_light.direction = sun_dir # Opposite
        
        # Update Material
        self.material.uniforms["sunPosition"] = sun_dir # Direction TO sun
        self.material.uniforms["moonPosition"] = -sun_dir # Direction TO moon
        
        # --- Color Gradient Logic ---
        height = sun_dir.y
        
        # Colors
        night_col_top = glm.vec3(0.0, 0.0, 0.05)
        night_col_bot = glm.vec3(0.0, 0.02, 0.1)
        
        sunrise_col_top = glm.vec3(0.2, 0.4, 0.7)
        sunrise_col_bot = glm.vec3(1.0, 0.4, 0.2) # Orange
        
        day_col_top = glm.vec3(0.1, 0.5, 0.9)
        day_col_bot = glm.vec3(0.6, 0.8, 0.95) # Cyan/White
        
        top = glm.vec3(0)
        bot = glm.vec3(0)
        
        if height > 0.2: # Full Day
            top = day_col_top
            bot = day_col_bot
            self.sun_light.color = glm.vec4(1.0, 0.95, 0.9, 1.2)
            self.moon_light.color = glm.vec4(0,0,0,0)
            
        elif height < -0.2: # Full Night
            top = night_col_top
            bot = night_col_bot
            self.sun_light.color = glm.vec4(0,0,0,0)
            self.moon_light.color = glm.vec4(0.2, 0.25, 0.4, 0.4) # Moon light
            
        else:
            t = (height + 0.2) / 0.4 
            
            if height > 0: # 0 to 0.2 (Sunrise to Day)
                 t_sub = height / 0.2
                 top = glm.mix(sunrise_col_top, day_col_top, t_sub)
                 bot = glm.mix(sunrise_col_bot, day_col_bot, t_sub)
                 self.sun_light.color = glm.mix(glm.vec4(1.0, 0.5, 0.2, 0.0), glm.vec4(1.0, 0.95, 0.9, 1.2), t_sub)
                 self.moon_light.color = glm.vec4(0,0,0,0)
            else: # -0.2 to 0 (Night to Sunrise)
                 t_sub = (height + 0.2) / 0.2
                 top = glm.mix(night_col_top, sunrise_col_top, t_sub)
                 bot = glm.mix(night_col_bot, sunrise_col_bot, t_sub)
                 self.sun_light.color = glm.vec4(0,0,0,0)
                 self.moon_light.color = glm.mix(glm.vec4(0.2, 0.25, 0.4, 0.4), glm.vec4(0,0,0,0), t_sub)

        self.material.uniforms["topColor"] = top
        self.material.uniforms["bottomColor"] = bot
        
    def draw(self, camera, lights):
        
        gl.glDepthFunc(gl.GL_LEQUAL)
        gl.glCullFace(gl.GL_FRONT) 
        
        super().draw(camera, [])
        
        gl.glCullFace(gl.GL_BACK) # Restore
        gl.glDepthFunc(gl.GL_LESS) # Restore
