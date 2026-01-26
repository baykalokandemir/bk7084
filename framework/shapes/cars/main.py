import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.camera import *
from framework.renderer import *
from framework.light import *
from pyglm import glm
import glfw

# Import individual vehicle classes
from project.racecar import RaceCar
from project.truck import Truck
from project.van import Van
from project.bus import Bus
from project.suv import SUV
from project.pickup import Pickup
from project.sedan import Sedan
from project.policecar import PoliceCar
from project.ambulance import Ambulance
from project.tank import Tank
from project.cyberpunk_car import CyberpunkCar

def main():
    width, height = 1000, 800 # Bigger window
    glwindow = OpenGLWindow(width, height, "Cyberpunk Vehicles")

    camera = Flycamera(width, height, 70.0, 0.1, 200.0)
    camera.transform = glm.translate(glm.vec3(10, 10, 20)) 
    # Look somewhat down
    camera.yaw = -135
    camera.pitch = -30

    glrenderer = GLRenderer(glwindow, camera)

    # Lots of lights for cyber feel
    glrenderer.addLight(PointLight(glm.vec4(20.0, 20.0, 20.0, 1.0), glm.vec4(0.8, 0.8, 0.8, 1.0)))
    glrenderer.addLight(PointLight(glm.vec4(-20.0, 20.0, -20.0, 1.0), glm.vec4(0.5, 0.5, 0.6, 1.0)))
    glrenderer.addLight(PointLight(glm.vec4(0.0, 20.0, 0.0, 1.0), glm.vec4(0.3, 0.3, 0.3, 1.0)))

    # Spawn all 10 vehicles in a grid or line
    vehicles = [
        RaceCar(), Truck(), Van(), Bus(), SUV(),
        Pickup(), Sedan(), PoliceCar(), Ambulance(), Tank(),
        CyberpunkCar()
    ]
    
    # 2 Rows of 5
    row_spacing = 10.0
    col_spacing = 8.0
    
    for i, v in enumerate(vehicles):
        row = i // 5
        col = i % 5
        
        x = col * col_spacing - (2 * col_spacing)
        z = row * row_spacing - (0.5 * row_spacing)
        
        v.transform = glm.translate(glm.vec3(x, 0, z))
        glrenderer.addObject(v)

    print("Controls:")
    print("  WASD + Mouse: Move Camera")
    print("  R: Regenerate Cyberpunk Cars")

    def key_callback(window, key, scancode, action, mods):
        if key == glfw.KEY_R and action == glfw.PRESS:
            print("Regenerating ALL vehicles...")
            for v in vehicles:
                v.regenerate()
                    
        # Forward input to the window's callback to handle camera controls
        glwindow.key_callback(window, key, scancode, action, mods)

    glfw.set_key_callback(glwindow.window, key_callback)

    while not glfw.window_should_close(glwindow.window):
        glrenderer.render()

    glrenderer.delete()
    glwindow.delete()
    return 0

if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
