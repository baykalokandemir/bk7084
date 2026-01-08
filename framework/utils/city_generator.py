import math
import random
from framework.utils.city_graph import CityGraph, Node, Edge

class Turtle:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        self.angle = angle # in radians
        self.active = True

    def move(self, distance):
        self.x += math.cos(self.angle) * distance
        self.y += math.sin(self.angle) * distance

class CityGenerator:
    def __init__(self):
        self.graph = CityGraph()
        self.turtles = []
        self.params = {
            'step_size': 20.0,
            'snap_dist': 10.0,
            'branch_prob': 0.2,
            'max_steps': 100,
            'road_width': 10.0
        }

    # Deterministic Grid Generator (USE THIS ONE)
    def generate_grid(self, rows=10, cols=10, spacing=40.0):
        self.graph.clear()
        
        # 1. Create a dictionary to store nodes by grid coordinate (r, c)
        grid_nodes = {}

        # 2. Create Nodes
        for r in range(rows):
            for c in range(cols):
                # Center the grid around (0,0)
                x = (c - cols / 2) * spacing
                y = (r - rows / 2) * spacing
                
                node = self.graph.add_node(x, y)
                grid_nodes[(r, c)] = node

        # 3. Create Edges (Horizontal and Vertical only)
        for r in range(rows):
            for c in range(cols):
                curr_node = grid_nodes[(r, c)]
                
                # Connect to Right Neighbor
                if c < cols - 1:
                    right_node = grid_nodes[(r, c+1)]
                    self.graph.add_edge(curr_node, right_node, width=10.0)
                
                # Connect to Top Neighbor
                if r < rows - 1:
                    top_node = grid_nodes[(r+1, c)]
                    self.graph.add_edge(curr_node, top_node, width=10.0)

    # Legacy / Experimental Turtle Generator
    def generate(self):
        self.graph.clear()
        # Start with one turtle at 0,0
        start_node = self.graph.add_node(0, 0)
        self.turtles = [Turtle(0, 0, 0)] # Moving East
        
        steps = 0
        while self.turtles and steps < self.params['max_steps']:
            steps += 1
            new_turtles = []
            
            for turtle in self.turtles:
                if not turtle.active: continue
                
                # Move
                turtle.move(self.params['step_size'])
                
                # Snap Logic
                target_node, dist = self.graph.get_nearest_node(turtle.x, turtle.y, self.params['snap_dist'])
                
                if target_node:
                    # Snap to it
                    turtle.x = target_node.x
                    turtle.y = target_node.y
                    turtle.active = False 
                else:
                    # Create new node
                    target_node = self.graph.add_node(turtle.x, turtle.y)