"""

  /$$$$$$$  /$$   /$$ /$$$$$$$$ /$$$$$$   /$$$$$$  /$$   /$$
 | $$__  $$| $$  /$$/|_____ $$//$$$_  $$ /$$__  $$| $$  | $$
 | $$  \\ $$| $$ /$$/      /$$/| $$$$\\ $$| $$  \\ $$| $$  | $$
 | $$$$$$$ | $$$$$/      /$$/ | $$ $$ $$|  $$$$$$/| $$$$$$$$
 | $$__  $$| $$  $$     /$$/  | $$\\ $$$$ >$$__  $$|_____  $$
 | $$  \\ $$| $$\\  $$   /$$/   | $$ \\ $$$| $$  \\ $$      | $$
 | $$$$$$$/| $$ \\  $$ /$$/    |  $$$$$$/|  $$$$$$/      | $$
 |_______/ |__/  \\__/|__/      \\______/  \\______/       |__/

In this assignment, we explore L-systems to generate a fractal binary tree.
We start with an axiom (a single symbol), and apply production rules repeatedly to grow a string.
Each symbol in the string has a meaning: "F" means draw a branch, "+" and "-" turn the angle,
and "[" and "]" push and pop the current turtle state (position, angle, and branch length).
A turtle state is simply a snapshot of the “turtle’s” current position, orientation, and drawing parameters
(like branch length or scale) that can be saved and restored while interpreting an L-system


By interpreting the final string, we build a branching structure:
every "F" becomes a cylinder segment, oriented along the current angle,
and every push/pop allows us to return to earlier branch points and grow new branches.
This recursive rewriting and interpretation produces a tree-like fractal.
"""

import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from framework.camera import Flycamera
from framework.window import *
from framework.renderer import *
from framework.light import *
from framework.shapes import Quad, Cylinder
from framework.objects import InstancedMeshObject, MeshObject
from framework.materials import Material
from pyglm import glm
import numpy as np
import random


class FractalBinaryTree:
    def __init__(self, renderer, depth=2, base_length=1.0, angle_deg=30.0, length_scale=0.7):
        self.renderer = renderer
        self.depth = depth
        self.base_length = base_length
        self.angle = glm.radians(angle_deg)
        self.length_scale = length_scale

        #[1.0]: Build an L-system string
        # It starts from an axiom, and is then iteratively mutated using the rule.
        # Keep in mind that the L-system is then evaluated using a cursor, often referred to as a "turtle"
        # https://en.wikipedia.org/wiki/Turtle_graphics

        #TODO [1.1]: change the rule such that the tree splits into two branches at every point,
        # where one curls to the left, and one to the right.
        # You can make use of the following alphabet:
        # - "F": Places a branch, and moves the cursor
        # - "[": pushes a state. Think of this as saving the cursor's state (position, angle, depth)
        #           Without it, you are more limited: every two consecutive steps are directly tied to each other.
        # - "]": pops a state. Think of this as going back to the previous state
        # - "-": rotate to the left
        # - "+": rotate to the right
        # - "+": rotate to the right
        # For a binary tree, you only need to change what F transforms into.
        # For this L-system, there is just one rule that transforms every "F" into something else.

        axiom = "F"
        rules = {
            #this is in format "from_string":"to_string"
            #this rule basically says: every "F" in the string should be replaced by "F[F]"
            "F": "F[-F][F][+F]"
        }

        # TODO [1.2]: Try different rules (by changing the rules = {} part)
        #  What happens when you don't use the stack? (square brackets)
        #  Can you make a tree that splits into three branches every step?

        def apply_rules(s, rules):
            for old, new in rules.items():
                s = s.replace(old, new)
            return s

        #[1.3] iteratively resolve the rule by applying it on the string.
        # TODO: Play with different values for depth, what difference does it make?
        #  (try to not make it too large, the string (might) grow exponentially!)
        s = axiom
        for _ in range(depth):
            s = apply_rules(s, rules)

        print(s)


        # Interpret into transforms/colors
        transforms, colors = self.interpret(s)

        # Wrap in instanced cylinder: every branch of the tree is a cylinder
        base_cyl = Cylinder(radius=0.08, height=1.0, segments=12, color=glm.vec4(1.0))
        cyl_mat = Material()
        self.inst = InstancedMeshObject(base_cyl, cyl_mat, transforms=transforms, colors=colors)
        renderer.addObject(self.inst)

    def interpret(self, s):
        # Turtle state in X–Y plane (Z = 0)
        class State:
            def __init__(self, pos, ang, length):
                self.pos = pos
                self.ang = ang
                self.length = length

            def clone(self):
                return State(glm.vec3(self.pos), self.ang, self.length)

        stack = []
        st = State(pos=glm.vec3(0, 0, 0), ang=glm.radians(0.0), length=self.base_length)  # start pointing up

        # we collect the transforms and colors for instancing here
        transforms = []
        colors = []

        #The string is evaluated here. we need one if statement per character in the alphabet
        for ch in s:
            if ch == "F":
                Rz = glm.rotate(st.ang, glm.vec3(0, 0, 1))
                mid_local = glm.vec3(0, st.length * 0.5, 0)
                tip_local = glm.vec3(0, st.length, 0)

                T = (
                    glm.translate(st.pos)
                    * Rz
                    * glm.translate(mid_local)
                    * glm.scale(glm.vec3(1.0, st.length, 1.0))
                )
                transforms.append(T)

                #TODO [2.2]: Use the length variable (after doing 2.1) to create a color gradient.
                #   Optionally, change the state class to store more data to do this.
                colors.append(glm.vec4(1.0))

                # Advance turtle position to tip (in world space)
                st.pos = st.pos + (Rz * glm.vec4(tip_local, 0.0)).xyz

                #TODO [2.1]: Reduce length for next segment
                st.length *= 1.0
            elif ch == "+":
                st.ang += self.angle
            elif ch == "-":
                st.ang -= self.angle
            elif ch == "[":
                stack.append(st.clone())
            elif ch == "]":
                st = stack.pop()

                # TODO [3.0]: Add randomness to any of the operations, try to get a slightly more organic tree.

        return transforms, colors


def main():
    width, height = 600, 600
    glwindow = OpenGLWindow(width, height)

    camera = Flycamera(width, height, 70.0, 0.1, 100.0)
    camera.draw_camera = False
    camera.position += glm.vec3(0.0, 4.0, 5.0)
    camera.updateView()

    glrenderer = GLRenderer(glwindow, camera)

    glrenderer.addLight(PointLight(glm.vec4(10.0, 10.0, 0.0, 1.0),
                                   glm.vec4(0.5, 0.5, 0.5, 1.0)))
    glrenderer.addLight(PointLight(glm.vec4(0.0, 10.0, 10.0, 1.0),
                                   glm.vec4(0.5, 0.5, 0.5, 1.0)))

    # a tiled floor at y=0
    floor_shape = Quad(width=100, height=100)
    floor_mat = Material(fragment_shader="grid.frag")
    floor_obj = MeshObject(floor_shape, floor_mat)
    floor_obj.transform = glm.rotate(glm.radians(-90), glm.vec3(1, 0, 0))
    glrenderer.addObject(floor_obj)

    fractal = FractalBinaryTree(glrenderer, depth=5, base_length=3.0, angle_deg=32.0, length_scale=0.7)

    while not glfw.window_should_close(glwindow.window):
        glrenderer.render()

    glrenderer.delete()
    glwindow.delete()
    return 0


if __name__ == "__main__":
    main()
