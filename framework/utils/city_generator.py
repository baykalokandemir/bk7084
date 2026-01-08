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

    def apply_irregularity(self, distortion=15.0, cull_chance=0.2):
        """
        Applies a 'Naturalization' texturing to the grid.
        1. Perturbation: Jitters node positions.
        2. Culling: Randomly removes edges to break grid uniformity.
        """
        # Step A: Perturbation (Jitter)
        for node in self.graph.nodes:
            # Jitter
            dx = random.uniform(-distortion, distortion)
            dy = random.uniform(-distortion, distortion)
            node.x += dx
            node.y += dy
            
        # Step B: Culling (The Eraser)
        # Iterate over a copy of edges because we might remove them
        edges_to_check = list(self.graph.edges)
        
        for edge in edges_to_check:
            if random.random() < cull_chance:
                # Optional Safety: Don't orphan nodes?
                # If we remove this edge, do the nodes have other edges?
                start_conns = len(edge.start_node.edges)
                end_conns = len(edge.end_node.edges)
                
                # Check if this edge is the LAST link for either node (orphaned)
                # Note: node.edges currently includes THIS edge.
                # So if len == 1, removing it makes it 0.
                if start_conns <= 1 or end_conns <= 1:
                    continue # Skip removing this edge to prevent orphans
                
                self.graph.remove_edge(edge)

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
                
                pass 

            pass
        
        pass

    def generate_improved(self, num_iterations=50):
        self.graph.clear()
        
        # Initial Node
        start_node = self.graph.add_node(0, 0)
        
        # Initial Turtles: Let's spawn 4 directions for a town center
        self.turtles = [
            Turtle(0, 0, 0),
            Turtle(0, 0, math.pi/2),
            Turtle(0, 0, math.pi),
            Turtle(0, 0, -math.pi/2)
        ]
        
        # Associate turtles with the start node
        for t in self.turtles:
            t.current_node = start_node
            
        for _ in range(num_iterations):
            new_turtles = []
            active_turtles = [t for t in self.turtles if t.active]
            
            if not active_turtles:
                break
                
            for turtle in active_turtles:
                # 1. Proposal Phase
                # Calculate proposed new position
                dx = math.cos(turtle.angle) * self.params['step_size']
                dy = math.sin(turtle.angle) * self.params['step_size']
                new_x = turtle.x + dx
                new_y = turtle.y + dy
                
                # 3. Snap or Create
                target_node, dist = self.graph.get_nearest_node(new_x, new_y, self.params['snap_dist'])
                
                if target_node:
                    # Snap to existing
                    turtle.x = target_node.x
                    turtle.y = target_node.y
                    # Connect
                    self.graph.add_edge(turtle.current_node, target_node, width=self.params['road_width'])
                    # Stop turtle if we hit an existing part of the graph (loop closure)
                    turtle.active = False
                else:
                    # Create new
                    turtle.x = new_x
                    turtle.y = new_y
                    target_node = self.graph.add_node(new_x, new_y)
                    self.graph.add_edge(turtle.current_node, target_node, width=self.params['road_width'])
                    
                    # Update turtle state
                    turtle.current_node = target_node
                    
                    # 4. Branching
                    if len(self.turtles) + len(new_turtles) < 500: # Safety Cap
                        if random.random() < self.params['branch_prob']:
                            # Branch left or right
                            angle_offset = math.pi/2 if random.random() < 0.5 else -math.pi/2
                            new_angle = turtle.angle + angle_offset
                            new_t = Turtle(turtle.x, turtle.y, new_angle)
                            new_t.current_node = target_node
                            new_turtles.append(new_t)

            self.turtles.extend(new_turtles)