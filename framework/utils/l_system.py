from pyglm import glm
import random

class LSystem:
    """
    Lindenmayer System (L-system) for procedural generation of fractal patterns.
    
    Generates strings through recursive symbol substitution and interprets them
    as 3D turtle graphics commands to produce branching structures. Commonly used
    for procedural plants, trees, and organic patterns.
    
    Commands:
        F: Move forward (creates transform)
        +/-: Rotate around Z-axis (yaw)
        &/^: Rotate around X-axis (pitch)
        \\/: Rotate around Y-axis (roll)
        [/]: Push/pop transform stack (branching)
    """
    
    def __init__(self, axiom="F", rules=None, angle=30.0, length=2.0, angle_range=None):
        """
        Initialize L-system with production rules and parameters.
        
        Args:
            axiom: Starting string (default "F")
            rules: Dict mapping symbols to replacement strings (default branching rule)
            angle: Base rotation angle in degrees (default 30.0)
            length: Forward movement distance (default 2.0)
            angle_range: Optional (min_deg, max_deg) for randomized angles
        """
        self.axiom = axiom
        self.rules = rules if rules is not None else {"F": "F[+F][-F]"}
        self.angle = glm.radians(angle)
        self.length = length
        self.angle_range = angle_range # Tuple (min_deg, max_deg)

    def generate_string(self, iterations=2):
        """
        Apply production rules recursively to generate L-system string.
        
        Args:
            iterations: Number of recursive substitution steps
        
        Returns:
            str: Generated L-system command string
        """
        s = self.axiom
        for _ in range(iterations):
            s = "".join(self.rules.get(char, char) for char in s)
        return s
        
    def get_turn_angle(self):
        """
        Get rotation angle, randomized if angle_range is set.
        
        Returns:
            float: Angle in radians
        """
        if self.angle_range:
            deg = random.uniform(self.angle_range[0], self.angle_range[1])
            return glm.radians(deg)
        return self.angle

    def interpret_transforms(self, s, max_points=None):
        """
        Interprets L-system string as 3D turtle graphics commands.
        
        Simulates a turtle moving through 3D space: F moves forward,
        rotation commands change orientation, brackets push/pop state
        for branching. Returns transform matrix at each F position.
        
        Args:
            s: L-system command string
            max_points: Optional limit on number of transforms returned
        
        Returns:
            list[glm.mat4]: Transform matrices for each forward step
        """
        stack = []
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
