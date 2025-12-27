# project/main.py

## Overview
This is the default boilerplate entry point for the assignment. It initializes a basic window and camera, adds a single test object (a purple cube), and starts the render loop.

## Antigravity/AI Note
**This file is NOT the entry point for the procedural city.** It does not import `SceneManager`, `AdvancedCityGenerator`, or any of the custom shaders. If run with the "New" framework, it will likely fail or freeze because the default `GLRenderer` has had its event polling removed (likely because the custom scripts in `exercises/` handle their own loops).

## Key Logic
* **Setup:** 600x600 Window.
* **Camera:** `FlyCamera`.
* **Scene:** One `PointLight` and one translucent purple `Cube`.