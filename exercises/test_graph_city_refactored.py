
import os
import sys
import glfw
import glm

# Add framework to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from framework.window import OpenGLWindow
from framework.renderer import GLRenderer
from framework.camera import Flycamera
from framework.utils.ui_manager import UIManager
from exercises.components.simulation_state import SimulationState
from exercises.components.city_ui import CityUI
from exercises.components.city_visuals import CityVisuals
from exercises.components.city_manager import CityManager

def main():
    try:
        window = OpenGLWindow(1280, 720, "Graph City Test - Refactored")
    except Exception as e:
        print(f"Failed to create window: {e}")
        return

    camera = Flycamera(window.width, window.height, 70, 0.1, 1000.0)
    camera.position = glm.vec3(0, 150, 150)
    camera.euler_angles.x = -60
    glrenderer = GLRenderer(window, camera)
    
    # Components
    visuals = CityVisuals(glrenderer)
    # Visuals init lights/skybox to renderer
    glrenderer.addObject(visuals.skybox)
    glrenderer.addLight(visuals.skybox.sun_light)
    glrenderer.addLight(visuals.skybox.moon_light)

    ui_manager = UIManager(window.window)
    ui_manager.setup_input_chaining(window)
    
    config = SimulationState()
    ui = CityUI(config)
    manager = CityManager(glrenderer)
    
    tracking_state = {"is_tracking": False, "target_id": 0, "found": False}

    # Texture Asset Scan
    texture_dir = os.path.join(os.path.dirname(__file__), "assets", "building_textures")
    found_textures = []
    if os.path.exists(texture_dir):
        found_textures = [f for f in os.listdir(texture_dir) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]

    def regenerate():
        manager.regenerate(400, 400, found_textures, texture_dir)
        visuals.regenerate_clouds(15)
        visuals.regenerate_holograms(config.target_hologram_count)

    regenerate()

    while not glfw.window_should_close(window.window):
        # Update
        dt = 0.016 # Fixed step for simplicity, or measure
        time = glfw.get_time()
        
        # Camera
        if not tracking_state["is_tracking"]:
            camera.update(dt)
        else:
            target = next((a for a in manager.agents if a.id == tracking_state["target_id"]), None)
            tracking_state["found"] = (target is not None)
            if target:
                offset_dist = 15.0
                desired = target.position - (target.orientation * offset_dist) + glm.vec3(0, 6.0, 0)
                camera.position = desired
                camera.front = glm.normalize((target.position + glm.vec3(0, 2.0, 0)) - camera.position)
                camera.updateView()
                # Simple Euler sync to prevent snapping on exit (optional simplified)

        manager.update(dt, config)
        visuals.update(dt, time, config)
        
        # Render
        glrenderer.render()
        
        # Debug Render
        for agent in manager.agents: agent.render_debug(glrenderer, camera)

        # UI
        ui_manager.render(lambda: ui.draw(
            manager.city_gen, manager.agents, manager.static_objects + manager.crash_meshes + ([manager.signal_mesh] if manager.signal_mesh else []), 
            glrenderer, manager.crash_shape, visuals.skybox, tracking_state, regenerate, 
            lambda: visuals.regenerate_holograms(config.target_hologram_count)
        ))
        
        glfw.swap_buffers(window.window)
        glfw.poll_events()
        
    ui_manager.shutdown()
    window.delete()
    glfw.terminate()

if __name__ == "__main__":
    main()
