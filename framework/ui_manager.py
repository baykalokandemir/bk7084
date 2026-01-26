import imgui
import colorsys

class UIManager:
    def __init__(self):
        pass

    def render(self, config, scene_manager, renderer):
        imgui.new_frame()
        
        imgui.begin("Hologram Controls")
        
        # --- L-System Settings ---
        if imgui.collapsing_header("L-System Rules", visible=True)[0]:
            # Iterations
            changed, config.L_ITERATIONS = imgui.slider_int("Iterations", config.L_ITERATIONS, 1, 5)
            
            # Size Limit
            changed, config.L_SIZE_LIMIT = imgui.slider_int("Max Objects", config.L_SIZE_LIMIT, 1, 50)
            
            # Step Length
            changed, config.L_LENGTH = imgui.slider_float("Step Length", config.L_LENGTH, 0.5, 5.0)
            
            # Angle Range
            imgui.text("Angle Variance (Min/Max Deg)")
            changed, new_min = imgui.slider_float("Min Angle", config.L_ANGLE_MIN, 0.0, 180.0)
            if changed: config.L_ANGLE_MIN = new_min
            
            changed, new_max = imgui.slider_float("Max Angle", config.L_ANGLE_MAX, 0.0, 180.0)
            if changed: config.L_ANGLE_MAX = new_max
            
            imgui.separator()
            if imgui.button("Regenerate Structure"):
                new_objects = scene_manager.generate_scene(config)
                renderer.objects = []
                for obj in new_objects:
                    renderer.addObject(obj)

        # --- Visual Settings (Uniforms) ---
        if imgui.collapsing_header("Hologram Visuals", visible=True)[0]:
            _, config.GRID_SPACING = imgui.slider_float("Grid Spacing", config.GRID_SPACING, 0.02, 0.5)
            
            _, config.POINT_SIZE = imgui.slider_float("Point Size", config.POINT_SIZE, 1.0, 50.0)
            
            # Point Shape Combo
            clicked, current = imgui.combo("Shape", config.POINT_SHAPE, config.POINT_SHAPES)
            if clicked:
                config.POINT_SHAPE = current
                
            # Color
            changed, config.POINT_CLOUD_COLOR = imgui.color_edit3("Color", *config.POINT_CLOUD_COLOR)
            
            _, config.ENABLE_GLOW = imgui.checkbox("Enable Glow", config.ENABLE_GLOW)
            
            # Regenerate if Grid Spacing changes (requires rebuilding buffers)
            # Actually, grid spacing is a Uniform in shader? 
            # NO! Grid spacing is used in GridPointCloudGenerator to CREATE vertices.
            # So changing grid spacing requires Regeneration.
            if imgui.button("Apply Grid Changes"):
                new_objects = scene_manager.generate_scene(config)
                renderer.objects = []
                for obj in new_objects:
                    renderer.addObject(obj)
                    
        # --- Post Process ---
        if imgui.collapsing_header("Post Processing", visible=True)[0]:
            _, config.USE_ABERRATION = imgui.checkbox("Chromatic Aberration", config.USE_ABERRATION)
            if config.USE_ABERRATION:
                _, config.ABERRATION_STRENGTH = imgui.slider_float("Strength##Aber", config.ABERRATION_STRENGTH, 0.0, 0.05)
                
            _, config.USE_BLUR = imgui.checkbox("Blur", config.USE_BLUR)
            if config.USE_BLUR:
                _, config.BLUR_STRENGTH = imgui.slider_float("Strength##Blur", config.BLUR_STRENGTH, 0.0, 0.01)

        imgui.end()
        imgui.render()
