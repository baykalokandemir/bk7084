import os
import sys

# Add framework to path
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from framework.window import OpenGLWindow
from framework.renderer import GLRenderer
from framework.camera import Flycamera
from framework.light import PointLight
import OpenGL.GL as gl
import glfw
import glm
import imgui
from imgui.integrations.glfw import GlfwRenderer

# Import all vehicles
from framework.shapes.cars.ambulance import Ambulance
from framework.shapes.cars.bus import Bus
from framework.shapes.cars.cyberpunk_car import CyberpunkCar
from framework.shapes.cars.pickup import Pickup
from framework.shapes.cars.policecar import PoliceCar
from framework.shapes.cars.racecar import RaceCar
from framework.shapes.cars.sedan import Sedan
from framework.shapes.cars.suv import SUV
from framework.shapes.cars.tank import Tank
from framework.shapes.cars.truck import Truck
from framework.shapes.cars.van import Van

def main():
    try:
        window = OpenGLWindow(1280, 720, "Vehicle Inspector")
    except Exception as e:
        print(f"Failed to create window: {e}")
        return

    # Camera
    camera = Flycamera(window.width, window.height, 70, 0.1, 1000.0)
    camera.position = glm.vec3(5, 5, 10)
    camera.cardinal_direction = glm.vec3(-0.5, -0.2, -0.8) # Look at center
    # camera.look_at(glm.vec3(0, 0, 0)) # Helper if available, otherwise manual aim
    
    # Renderer
    glrenderer = GLRenderer(window, camera)
    
    # Light
    glrenderer.addLight(PointLight(glm.vec4(10.0, 20.0, 10.0, 1.0), glm.vec4(1.0, 1.0, 1.0, 1.0)))
    
    # ImGui
    imgui.create_context()
    impl = GlfwRenderer(window.window, attach_callbacks=False)
    
    # Input Callbacks
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
    car_classes = [
        ("Ambulance", Ambulance),
        ("Bus", Bus),
        ("Cyberpunk Car", CyberpunkCar),
        ("Pickup", Pickup),
        ("Police Car", PoliceCar),
        ("Race Car", RaceCar),
        ("Sedan", Sedan),
        ("SUV", SUV),
        ("Tank", Tank),
        ("Truck", Truck),
        ("Van", Van)
    ]
    
    selected_idx = [0] # List for ImGui reference
    current_car_obj = None
    
    def spawn_car():
        nonlocal current_car_obj
        
        # Cleanup
        if current_car_obj:
            if current_car_obj in glrenderer.objects:
                glrenderer.objects.remove(current_car_obj)
            # BaseVehicle adds parts which are MeshObjects.
            # BaseVehicle itself is NOT an Object in the renderer list directly in my old code?
            # Wait, BaseVehicle inherits Object.
            # But in test_graph_city, we added `ag.mesh_object` which IS the BaseVehicle (or wrapper).
            # If BaseVehicle is passed to wrapper, wrapper is added.
            # If CarAgent.mesh_object = BaseVehicle instance, then BaseVehicle IS added.
            pass
            
        # In this scene we don't use CarAgent, we just render the car directly.
        # But BaseVehicle.parts contains the actual MeshObjects that render?
        # Let's check BaseVehicle.draw.
        # It iterates self.parts and calls draw().
        # So we add the BaseVehicle instance to renderer.objects.
        
        # Double check cleanup:
        # GLRenderer.render calls o.draw(). BaseVehicle.draw calls part.draw().
        # So yes, we just remove the BaseVehicle instance from renderer.objects.
        
        # Instantiate
        name, cls = car_classes[selected_idx[0]]
        print(f"Spawning {name}...")
        
        car = cls() # This triggers batch caching if needed
        # car.create_geometry() # Called in __init__
        
        # Transform: Center it
        car.transform = glm.mat4(1.0)
        
        # Add to renderer
        glrenderer.addObject(car)
        current_car_obj = car

    # Init
    spawn_car()

    # Loop
    while not glfw.window_should_close(window.window):
        impl.process_inputs()
        camera.update(0.016)
        
        # Render Scene
        glrenderer.render()
        
        # Render GUI
        imgui.new_frame()
        imgui.begin("Vehicle Control")
        
        changed, selected_idx[0] = imgui.combo("Type", selected_idx[0], [c[0] for c in car_classes])
        if changed:
            spawn_car()
            
        if imgui.button("Regenerate"):
            spawn_car()
            
        imgui.text(f"Camera Pos: {camera.position.x:.1f}, {camera.position.y:.1f}, {camera.position.z:.1f}")
            
        imgui.end()
        imgui.render()
        impl.render(imgui.get_draw_data())
        
        glfw.swap_buffers(window.window)
        glfw.poll_events()
        
    window.destroy()

if __name__ == "__main__":
    main()
