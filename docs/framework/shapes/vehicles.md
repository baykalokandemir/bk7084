# Vehicle System Documentation

The vehicle system in this framework provides a robust and performance-optimized way to render complex 3D vehicle models. It is built upon a polymorphic architecture centered around the `BaseVehicle` class.

## BaseVehicle Architecture

`BaseVehicle` is the abstract base class for all car types. It inherits from `Object` and manages the construction and rendering of composite vehicle geometry.

- **Path**: `framework/shapes/cars/vehicle.py`
- **Inheritance**: `Object` -> `BaseVehicle`

### Key Features

1.  **Composite Geometry**: Vehicles are built from multiple parts (body, wheels, windows, etc.) rather than a single static mesh. This allows for modular construction using primitives like Cubes, Trapezoids, and Cylinders.
2.  **Polymorphism**: The `CarAgent` class can accept any instance of `BaseVehicle` (or even a raw `Shape`), allowing the simulation to handle diverse vehicle types uniformly.

### Optimization: Mesh Batching

To maintain high performance (~60 FPS) with many vehicles (e.g., 50+), `BaseVehicle` implements a **Static Mesh Batching** system.

#### The Problem
Drawing a vehicle part-by-part (4 wheels + body + windows + lights) results in 10-50 draw calls per car. With 50 cars, this creates 2500+ draw calls per frame, causing severe CPU/Driver overhead.

#### The Solution
`BaseVehicle` automatically batches the geometry of each vehicle subclass into 4 optimized meshes based on material:
1.  **Body**: The main chassis (Grey/Color).
2.  **Wheel**: All 4 wheels (Black rubber).
3.  **Glass**: Windows (Shiny black).
4.  **Glow**: Lights and emissive elements.

These batched meshes are **cached statically** per class.
- The first time a `Tank` is instantiated, its geometry is generated and batched into 4 shared `MeshObject`s.
- All subsequent `Tank` instances reuse these same 4 `MeshObject`s (with their own model transform).
- **Result**: Draw calls per car are constant (<= 4), regardless of complexity.

### Creating a New Vehicle

To create a new vehicle, inherit from `BaseVehicle` and implement `create_geometry`. Use the helper methods `add_box`, `add_trap`, and `add_wheel` to define the shape. **Do not create MeshObjects manually** if you want to benefit from auto-batching.

```python
from framework.shapes.cars.vehicle import BaseVehicle
from pyglm import glm

class MyCustomCar(BaseVehicle):
    def create_geometry(self):
        # Chassis
        self.add_box(glm.vec4(1, 0, 0, 1), glm.vec3(2, 1, 4), glm.vec3(0, 1, 0), self.body_mat)
        # Wheels
        self.add_wheel(0.5, 0.4, glm.vec3(1, 0, 1))
        self.add_wheel(0.5, 0.4, glm.vec3(-1, 0, 1))
        # ...
```

## Available Vehicle Types

The following vehicle classes are available in `framework/shapes/cars/`:

| Class Name | File | Description |
| :--- | :--- | :--- |
| **Ambulance** | `ambulance.py` | A medical emergency vehicle. |
| **Bus** | `bus.py` | A large public transport vehicle. |
| **CyberpunkCar** | `cyberpunk_car.py` | A high-detail, futuristic vehicle with glowing accents. |
| **Pickup** | `pickup.py` | A utility truck with an open cargo bed. |
| **PoliceCar** | `policecar.py` | A law enforcement sedan with sirens. |
| **RaceCar** | `racecar.py` | A low-profile, aerodynamic sports car. |
| **Sedan** | `sedan.py` | A standard passenger car (similar to the base design). |
| **SUV** | `suv.py` | A generic Sports Utility Vehicle. |
| **Tank** | `tank.py` | A heavy military vehicle with a turret and barrel. |
| **Truck** | `truck.py` | A heavy transport truck. |
| **Van** | `van.py` | A generic delivery or passenger van. |

## Usage in Simulation

To use these vehicles in `CarAgent`:

```python
from framework.utils.car_agent import CarAgent
from framework.shapes.cars.tank import Tank
from framework.shapes.cars.policecar import PoliceCar
import random

# Select a class
car_classes = [Tank, PoliceCar]
CarClass = random.choice(car_classes)

# Instantiate
car_shape = CarClass()

# Pass to Agent
agent = CarAgent(start_lane, car_shape=car_shape)
```
