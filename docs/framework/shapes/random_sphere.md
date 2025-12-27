# framework/shapes/random_sphere.py

## Overview
A procedural shape generator that creates a "Cloud Sphere". It distributes points across the surface of a sphere using either a uniform random distribution or a latitude/longitude grid.

## Changelog (Original vs. Current)
* **New File:** This file did not exist in the original framework.

## Key Classes & Functions
### `RandomSphere(Shape)`
* `__init__(radius, point_count, mode)`: Sets parameters.
* `createGeometry()`:
    * **Random Mode (Math):** Uses "Archimedes' Hat-Box Theorem" logic to ensure points are uniformly distributed on the sphere surface.
        * Picks $z$ randomly between $[-1, 1]$.
        * Picks $\theta$ randomly between $[0, 2\pi]$.
        * Calculates radius at height $z$: $r = \sqrt{1 - z^2}$.
        * Converts to Cartesian: $x = r \cos(\theta)$, $y = r \sin(\theta)$.
    * **Regular Mode:** Standard UV Sphere generation.
        * Iterates `stacks` (Latitude) from $+\pi/2$ to $-\pi/2$.
        * Iterates `sectors` (Longitude) from $0$ to $2\pi$.
        * Generates a point at every intersection.

## Dependencies
* **Internal:** `framework.shapes.shape`.
* **Libraries:** `pyglm`, `numpy`, `random`.