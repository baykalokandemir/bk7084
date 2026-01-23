import glm

class PointLight ():
    """
    A light source for shading
    """

    def __init__ (self, pos, color):
        """
        Constructor
        Receives the position and color of the point light source
        """
        self.position = pos
        self.color = color


class DirectionalLight():
    """
    A directional light source (e.g. Sun/Moon)
    """
    def __init__(self, direction, color, ambient=0.1):
        """
        direction: vec3 or vec4 (will be normalized)
        color: vec4 (r,g,b,intensity)
        ambient: float multiplier for ambient component
        """
        self.direction = glm.normalize(direction)
        self.color = color
        self.ambient = ambient



