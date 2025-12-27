# framework/utils/street_light.py

## Overview
A procedural generator that creates a low-poly street light mesh. It constructs a vertical pole, a horizontal arm, and a "bulb" box.

## Key Logic
### Geometry Generation
* **Pole & Arm:** Constructed as simple rectangular prisms (boxes) using the `_add_box` helper method.
* **The "Bulb" Hack:**
    * The bulb geometry is colored with `glm.vec4(1.0, 1.0, 0.8, 1.0)`.
    * **Critical Connection:** This specific yellow color value matches the `if` condition in `framework/shaders/shader.frag`. When the shader sees this color, it ignores lighting calculations and renders the pixels at full brightness, creating the illusion that the bulb is glowing.

## Dependencies
* **Internal:** `framework.shapes.shape`.
* **Libraries:** `pyglm`, `numpy`.