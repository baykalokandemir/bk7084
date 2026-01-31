import random
import glm
import glfw
from framework.objects.skybox import Skybox
from framework.objects.cloud import Cloud
from framework.utils.holograms_3d import Holograms3D, HologramConfig

class CityVisuals:
    def __init__(self, renderer):
        self.renderer = renderer
        self.skybox = Skybox(time_scale=1.0)
        self.clouds = []
        self.holograms = []
        self.hologram_configs = []
        
    def regenerate_clouds(self, count=15):
        # Cleanup existing clouds from renderer
        for cloud in self.clouds:
             if cloud.inst in self.renderer.objects:
                 self.renderer.objects.remove(cloud.inst)
        
        self.clouds = []
        print("Scattering Clouds...")
        for _ in range(count):
            cx = random.uniform(-180, 180)
            cz = random.uniform(-180, 180)
            cy = random.uniform(80, 120)
            c_scale = random.uniform(2.0, 5.0)
            cloud = Cloud(self.renderer, glm.vec3(cx, cy, cz), scale=c_scale)
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
             pos = glm.vec3(0, 40.0, 0)
             valid = False
             for attempt in range(10):
                 rx = random.uniform(-180, 180)
                 rz = random.uniform(-180, 180)
                 candidate = glm.vec3(rx, 40.0, rz)
                 too_close = False
                 for h in self.holograms:
                     if glm.distance(candidate, h.root_position) < 80.0:
                         too_close = True
                         break
                 if not too_close:
                     pos = candidate
                     valid = True
                     break
             if not valid:
                 pos = glm.vec3(random.uniform(-180, 180), 40.0, random.uniform(-180, 180))
             
             cfg = HologramConfig()
             cfg.L_ITERATIONS = 2
             cfg.L_SIZE_LIMIT = random.randint(3, 15)
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
            
        # Visibility Sync
        # Skybox
        is_skybox_in = self.skybox in self.renderer.objects
        if config.show_skybox and not is_skybox_in:
            self.renderer.addObject(self.skybox)
        elif not config.show_skybox and is_skybox_in:
            self.renderer.objects.remove(self.skybox)
            
        # Clouds
        for cloud in self.clouds:
             is_in = cloud.inst in self.renderer.objects
             if config.show_clouds and not is_in:
                 self.renderer.addObject(cloud.inst)
             elif not config.show_clouds and is_in:
                 self.renderer.objects.remove(cloud.inst)

        # Holograms
        for holo in self.holograms:
            for obj in holo.objects:
                is_in = obj in self.renderer.objects
                if config.show_holograms and not is_in:
                    self.renderer.addObject(obj)
                elif not config.show_holograms and is_in:
                    self.renderer.objects.remove(obj)

    def get_objects(self):
        """Returns flat list of all renderable objects."""
        objs = [self.skybox]
        for c in self.clouds:
            objs.append(c.inst)
        for h in self.holograms:
            objs.extend(h.objects)
        return objs
