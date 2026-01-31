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
from exercises.components.camera_controller import CameraController

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
    
    # Texture Asset Path
    texture_dir = os.path.join(os.path.dirname(__file__), "assets", "building_textures")
    manager = CityManager(glrenderer, texture_dir)
    camera_ctrl = CameraController(camera)

    ui = CityUI(config, manager, visuals, glrenderer, camera_ctrl)

    manager.regenerate_world(visuals, config)

    while not glfw.window_should_close(window.window):
        # Update
        dt = 0.016 # Fixed step for simplicity, or measure
        time = glfw.get_time()
        
        # Camera
        camera_ctrl.update(dt, manager.agents)

        manager.update(dt, config)
        visuals.update(dt, time, config)
        
        # Render
        glrenderer.render()
        
        # Debug Render
        for agent in manager.agents: agent.render_debug(glrenderer, camera)

        # UI
        ui_manager.render(lambda: ui.draw())
        
        glfw.swap_buffers(window.window)
        glfw.poll_events()
        
    ui_manager.shutdown()
    window.delete()
    glfw.terminate()

if __name__ == "__main__":
    main()
