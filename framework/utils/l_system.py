from pyglm import glm
import random

class LSystem:
    def __init__(self, axiom="F", rules=None, angle=30.0, length=2.0, angle_range=None):
        self.axiom = axiom
        self.rules = rules if rules is not None else {"F": "F[+F][-F]"}
        self.angle = glm.radians(angle)
        self.length = length
        self.angle_range = angle_range # Tuple (min_deg, max_deg)

    def generate_string(self, iterations=2):
        s = self.axiom
        for _ in range(iterations):
            next_s = ""
            for char in s:
                next_s += self.rules.get(char, char)
            s = next_s
        return s
        
    def get_turn_angle(self):
        if self.angle_range:
            deg = random.uniform(self.angle_range[0], self.angle_range[1])
            return glm.radians(deg)
        return self.angle

    def interpret_transforms(self, s, max_points=None):
        """
        Interprets the string 's' into a list of glm.mat4 transforms.
        Returns at most max_points transforms (if specified).
        """
        stack = []
        
        pos = glm.vec3(0, 0, 0)
        current_transform = glm.mat4(1.0)
        
        results = []
        
        def add_result(mat):
            if max_points is None or len(results) < max_points:
                results.append(glm.mat4(mat)) 

        for char in s:
            if max_points is not None and len(results) >= max_points:
                break
                
            if char == "F":
                move = glm.translate(glm.vec3(0, self.length, 0))
                current_transform = current_transform * move
                add_result(current_transform)
                
            elif char == "+": # Rotate Z
                rot = glm.rotate(self.get_turn_angle(), glm.vec3(0, 0, 1))
                current_transform = current_transform * rot
            elif char == "-": # Rotate -Z
                rot = glm.rotate(-self.get_turn_angle(), glm.vec3(0, 0, 1))
                current_transform = current_transform * rot
            elif char == "&": # Rotate X
                rot = glm.rotate(self.get_turn_angle(), glm.vec3(1, 0, 0))
                current_transform = current_transform * rot
            elif char == "^": # Rotate -X
                rot = glm.rotate(-self.get_turn_angle(), glm.vec3(1, 0, 0))
                current_transform = current_transform * rot
            elif char == "\\": # Rotate Y
                rot = glm.rotate(self.get_turn_angle(), glm.vec3(0, 1, 0))
                current_transform = current_transform * rot
            elif char == "/": # Rotate -Y
                rot = glm.rotate(-self.get_turn_angle(), glm.vec3(0, 1, 0))
                current_transform = current_transform * rot
            elif char == "[":
                stack.append(glm.mat4(current_transform))
            elif char == "]":
                if stack:
                    current_transform = stack.pop()
                    
        return results


