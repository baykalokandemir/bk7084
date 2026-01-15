import imgui
import colorsys
import os

class UIManager:
    def __init__(self):
        self.gltf_path_buffer = "" # Buffer for text input

    def render(self, config, scene_manager, renderer):
        imgui.new_frame()
        
        imgui.begin("Mikoshi Controls")
        
        # Generation Settings
        if imgui.collapsing_header("Generation", visible=True)[0]:
            changed, config.POINT_COUNT = imgui.input_int("Point Count", config.POINT_COUNT)
            
            # Sampling Mode Combo
            clicked, current = imgui.combo("Sampling Mode", config.SAMPLING_MODE, config.SAMPLING_MODES)
            if clicked:
                config.SAMPLING_MODE = current
                
            changed_scale, config.GLTF_SCALE = imgui.slider_float("GLTF Scale", config.GLTF_SCALE, 0.01, 1.0)
            
            changed_cloud, config.USE_POINT_CLOUD = imgui.checkbox("Use Point Cloud", config.USE_POINT_CLOUD)

            imgui.separator()
            imgui.text("Point Settings")
            _, config.POINT_SIZE = imgui.slider_float("Point Size", config.POINT_SIZE, 1.0, 50.0)
            
            clicked_shape, current_shape = imgui.combo("Point Shape", config.POINT_SHAPE, config.POINT_SHAPES)
            if clicked_shape:
                config.POINT_SHAPE = current_shape
                
            imgui.text("Animation")
            _, config.ANIM_RESIZE_X = imgui.checkbox("Resize Horizontal", config.ANIM_RESIZE_X)
            _, config.ANIM_RESIZE_Y = imgui.checkbox("Resize Vertical", config.ANIM_RESIZE_Y)
            
            imgui.separator()
            imgui.text("Model Loading")
            
            # Text Input for GLTF Path
            # Note: imgui.input_text returns (changed, value)
            # We initialize buffer with current config path if empty
            if not self.gltf_path_buffer and config.GLTF_PATH:
                self.gltf_path_buffer = config.GLTF_PATH
                
            changed_path, self.gltf_path_buffer = imgui.input_text("GLTF Path", self.gltf_path_buffer, 256)
            
            if imgui.button("Load / Regenerate"):
                # Update config path from buffer
                if self.gltf_path_buffer.strip():
                    config.GLTF_PATH = self.gltf_path_buffer.strip()
                else:
                    config.GLTF_PATH = None
                    
                # Regenerate Scene
                new_objects = scene_manager.generate_scene(config)
                renderer.objects = [] # Clear existing
                for obj in new_objects:
                    renderer.addObject(obj)
        
        # Slice Settings
        if imgui.collapsing_header("Slice Shader", visible=True)[0]:
            _, config.SLICE_SPACING = imgui.slider_float("Spacing", config.SLICE_SPACING, 0.01, 1.0)
            _, config.SLICE_THICKNESS = imgui.slider_float("Thickness", config.SLICE_THICKNESS, 0.001, 0.1)
            _, config.SLICE_WARP = imgui.slider_float("Warp", config.SLICE_WARP, 0.0, 0.5)
            _, config.SLICE_SPEED = imgui.slider_float("Speed", config.SLICE_SPEED, 0.0, 2.0)
            _, config.SLICE_ANIMATE = imgui.checkbox("Animate", config.SLICE_ANIMATE)
            
            # Normal (Vec3)
            changed, new_normal = imgui.slider_float3("Normal", *config.SLICE_NORMAL, min_value=-1.0, max_value=1.0)
            if changed:
                config.SLICE_NORMAL = list(new_normal)
            
        # Visuals
        if imgui.collapsing_header("Visuals", visible=True)[0]:
            _, config.ENABLE_GLOW = imgui.checkbox("Enable Glow", config.ENABLE_GLOW)
            
            imgui.separator()
            imgui.text("Point Cloud Color")
            # Hue Slider
            changed_hue, config.POINT_CLOUD_HUE = imgui.slider_float("PC Hue", config.POINT_CLOUD_HUE, 0.0, 1.0)
            if changed_hue:
                # Update RGB from Hue (keeping Saturation and Value high)
                r, g, b = colorsys.hsv_to_rgb(config.POINT_CLOUD_HUE, 1.0, 1.0)
                config.POINT_CLOUD_COLOR = [r, g, b]
                
            # RGB Picker
            changed_color, config.POINT_CLOUD_COLOR = imgui.color_edit3("PC Color", *config.POINT_CLOUD_COLOR)
            if changed_color:
                # Update Hue from RGB (approximate)
                h, s, v = colorsys.rgb_to_hsv(*config.POINT_CLOUD_COLOR)
                config.POINT_CLOUD_HUE = h

            imgui.separator()
            imgui.text("Slice Color")
            # Hue Slider
            changed_hue_slice, config.SLICE_HUE = imgui.slider_float("Slice Hue", config.SLICE_HUE, 0.0, 1.0)
            if changed_hue_slice:
                r, g, b = colorsys.hsv_to_rgb(config.SLICE_HUE, 1.0, 1.0)
                config.SLICE_COLOR = [r, g, b]
                
            # RGB Picker
            changed_color_slice, config.SLICE_COLOR = imgui.color_edit3("Slice Color", *config.SLICE_COLOR)
            if changed_color_slice:
                h, s, v = colorsys.rgb_to_hsv(*config.SLICE_COLOR)
                config.SLICE_HUE = h
            changed_color_slice, config.SLICE_COLOR = imgui.color_edit3("Slice Color", *config.SLICE_COLOR)
            if changed_color_slice:
                h, s, v = colorsys.rgb_to_hsv(*config.SLICE_COLOR)
                config.SLICE_HUE = h
                
        # Post Processing
        if imgui.collapsing_header("Post Processing", visible=True)[0]:
            _, config.USE_ABERRATION = imgui.checkbox("Enable Chromatic Aberration", config.USE_ABERRATION)
            if config.USE_ABERRATION:
                _, config.ABERRATION_STRENGTH = imgui.slider_float("Aberration Strength", config.ABERRATION_STRENGTH, 0.0, 0.05, "%.4f")
            
            _, config.USE_BLUR = imgui.checkbox("Enable Blur", config.USE_BLUR)
            if config.USE_BLUR:
                _, config.BLUR_STRENGTH = imgui.slider_float("Blur Strength", config.BLUR_STRENGTH, 0.0001, 0.01, "%.4f")
            
        imgui.end()
        
        imgui.render()
