import random
import glm
import glfw
from framework.objects.skybox import Skybox
from framework.objects.cloud import Cloud
from framework.utils.holograms_3d import Holograms3D, HologramConfig

class CityVisuals:
    """
    Manages decorative visual effects for the city simulation.
    
    Handles skybox (day/night cycle), procedural clouds, and holographic
    displays. Manages visibility toggling and updates for all visual effects.
    Note: Cloud objects self-register with renderer in their constructor.
    """
    
    # City bounds for random placement
    CITY_MIN_X = -180
    CITY_MAX_X = 180
    CITY_MIN_Z = -180
    CITY_MAX_Z = 180
    
    # Cloud settings
    CLOUD_HEIGHT_MIN = 80
    CLOUD_HEIGHT_MAX = 120
    CLOUD_SCALE_MIN = 2.0
    CLOUD_SCALE_MAX = 5.0
    
    # Hologram settings
    HOLOGRAM_HEIGHT = 40.0
    HOLOGRAM_SPACING = 80.0
    HOLOGRAM_PLACEMENT_ATTEMPTS = 10
    HOLOGRAM_SIZE_MIN = 3
    HOLOGRAM_SIZE_MAX = 15

    def __init__(self, renderer):
        """
        Initialize visual effects manager.
        
        Args:
            renderer: GLRenderer instance for object registration
        """
        self.renderer = renderer
        self.skybox = Skybox(time_scale=1.0)
        self.clouds = []
        self.holograms = []
        self.hologram_configs = []
        
        # Track previous visibility states for efficient toggling
        self._prev_show_skybox = None
        self._prev_show_clouds = None
        self._prev_show_holograms = None
        
    def regenerate_clouds(self, count=15):
        # Cleanup existing clouds from renderer
        for cloud in self.clouds:
             if cloud.inst in self.renderer.objects:
                 self.renderer.objects.remove(cloud.inst)
        
        self.clouds = []
        print("Scattering Clouds...")
        for _ in range(count):
            cx = random.uniform(self.CITY_MIN_X, self.CITY_MAX_X)
            cz = random.uniform(self.CITY_MIN_Z, self.CITY_MAX_Z)
            cy = random.uniform(self.CLOUD_HEIGHT_MIN, self.CLOUD_HEIGHT_MAX)
            c_scale = random.uniform(self.CLOUD_SCALE_MIN, self.CLOUD_SCALE_MAX)
            cloud = Cloud(self.renderer, glm.vec3(cx, cy, cz), scale=c_scale)
            # Note: Cloud self-registers with renderer in its constructor
            self.clouds.append(cloud)

    def regenerate_holograms(self, count=5):
        # Cleanup existing holograms
        for holo in self.holograms:
            for obj in holo.objects:
                if obj in self.renderer.objects:
                    self.renderer.objects.remove(obj)

        self.holograms = []
        self.hologram_configs = []
        print(f"Generating {count} holograms...")
        
        for i in range(count):
             pos = glm.vec3(0, self.HOLOGRAM_HEIGHT, 0)
             valid = False
             for attempt in range(self.HOLOGRAM_PLACEMENT_ATTEMPTS):
                 rx = random.uniform(self.CITY_MIN_X, self.CITY_MAX_X)
                 rz = random.uniform(self.CITY_MIN_Z, self.CITY_MAX_Z)
                 candidate = glm.vec3(rx, self.HOLOGRAM_HEIGHT, rz)
                 too_close = False
                 for h in self.holograms:
                     if glm.distance(candidate, h.root_position) < self.HOLOGRAM_SPACING:
                         too_close = True
                         break
                 if not too_close:
                     pos = candidate
                     valid = True
                     break
             if not valid:
                 pos = glm.vec3(random.uniform(self.CITY_MIN_X, self.CITY_MAX_X), 
                                self.HOLOGRAM_HEIGHT, 
                                random.uniform(self.CITY_MIN_Z, self.CITY_MAX_Z))
             
             cfg = HologramConfig()
             cfg.L_ITERATIONS = 2
             cfg.L_SIZE_LIMIT = random.randint(self.HOLOGRAM_SIZE_MIN, self.HOLOGRAM_SIZE_MAX)
             palette = [(0, 240, 255), (116, 238, 21), (255, 231, 0), (240, 0, 255), (245, 39, 137)]
             choice = random.choice(palette)
             rgb = [(c / 255.0) * 3.0 for c in choice]
             cfg.POINT_CLOUD_COLOR = list(rgb)
             if random.random() < 0.5:
                 cfg.USE_POINT_CLOUD = True
             else:
                 cfg.USE_POINT_CLOUD = False
                 cfg.SLICE_NORMAL = [random.random(), random.random(), random.random()]
                 cfg.SLICE_SPEED = random.uniform(0.05, 0.2)
             
             holo = Holograms3D(root_position=pos, scale=5.0)
             holo.regenerate(cfg)
             self.holograms.append(holo)
             self.hologram_configs.append(cfg)

    def update(self, dt, time, config):
        self.skybox.update(dt)
        for i, holo in enumerate(self.holograms):
            holo.update(dt)
            holo.update_uniforms(self.hologram_configs[i], time)
            
        # Visibility Sync - Only update when toggles change
        
        # Skybox
        if config.show_skybox != self._prev_show_skybox:
            if config.show_skybox:
                if self.skybox not in self.renderer.objects:
                    self.renderer.addObject(self.skybox)
            else:
                if self.skybox in self.renderer.objects:
                    self.renderer.objects.remove(self.skybox)
            self._prev_show_skybox = config.show_skybox
                
        # Clouds
        if config.show_clouds != self._prev_show_clouds:
            for cloud in self.clouds:
                if config.show_clouds:
                    if cloud.inst not in self.renderer.objects:
                        self.renderer.addObject(cloud.inst)
                else:
                    if cloud.inst in self.renderer.objects:
                        self.renderer.objects.remove(cloud.inst)
            self._prev_show_clouds = config.show_clouds
    
        # Holograms
        if config.show_holograms != self._prev_show_holograms:
            for holo in self.holograms:
                for obj in holo.objects:
                    if config.show_holograms:
                        if obj not in self.renderer.objects:
                            self.renderer.addObject(obj)
                    else:
                        if obj in self.renderer.objects:
                            self.renderer.objects.remove(obj)
            self._prev_show_holograms = config.show_holograms

    def get_objects(self):
        """Returns flat list of all renderable objects."""
        objs = [self.skybox]
        for c in self.clouds:
            objs.append(c.inst)
        for h in self.holograms:
            objs.extend(h.objects)
        return objs
