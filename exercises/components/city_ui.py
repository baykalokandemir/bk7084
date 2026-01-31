import imgui
import random

class CityUI:
    def __init__(self, config, manager, visuals, renderer, camera_ctrl, on_regenerate):
        self.config = config
        self.manager = manager
        self.visuals = visuals
        self.renderer = renderer
        self.camera_ctrl = camera_ctrl
        self.on_regenerate = on_regenerate

    def draw(self):
        """
        Draws the City Control UI using stored dependencies.
        """
        imgui.begin("City Controls")
        
        if imgui.button("Regenerate"):
            self.on_regenerate()
            
        imgui.text(f"Total Crashes: {self.config.total_crashes}")
            
        _, self.config.num_cars_to_brake = imgui.input_int("Num to Brake", self.config.num_cars_to_brake)
        if imgui.button("Brake Random Cars"):
            count = min(self.config.num_cars_to_brake, len(self.manager.agents))
            if count > 0:
                candidates = [a for a in self.manager.agents if not a.manual_brake and not a.is_reckless]
                targets = candidates if len(candidates) < count else random.sample(candidates, count)
                for t in targets: t.manual_brake = True
                print(f"[USER] Manually braked {len(targets)} cars.")
        
        if imgui.button("Release All"):
            for a in self.manager.agents: a.manual_brake = False
            print("[USER] Released all manual brakes.")
            
        _, self.config.reckless_chance = imgui.slider_float("Reckless %", self.config.reckless_chance, 0.0, 1.0)
        
        if imgui.button("Clear Wrecks"):
             # Cleanup specific to crash meshes managed by CityManager
             count = len(self.manager.crash_meshes)
             for obj in self.manager.crash_meshes:
                 if obj in self.renderer.objects:
                     self.renderer.objects.remove(obj)
             self.manager.crash_meshes.clear()
             print(f"[USER] Cleared {count} wrecks.")
 
        _, self.config.target_agent_count = imgui.slider_int("Car Count", self.config.target_agent_count, 0, 50)
        
        imgui.separator()
        imgui.text("Holograms")
        changed, self.config.target_hologram_count = imgui.slider_int("Num Holograms", self.config.target_hologram_count, 0, 20)
        if changed or imgui.button("Regenerate Holograms"):
            self.visuals.regenerate_holograms(self.config.target_hologram_count)
            
        imgui.separator()
            
        _, self.config.show_buildings = imgui.checkbox("Show Buildings", self.config.show_buildings)
        _, self.config.show_clouds = imgui.checkbox("Show Clouds", self.config.show_clouds)
        _, self.config.show_holograms = imgui.checkbox("Show Holograms", self.config.show_holograms)
        _, self.config.show_skybox = imgui.checkbox("Show Skybox", self.config.show_skybox)
        _, self.config.crash_debug = imgui.checkbox("Crash Debug", self.config.crash_debug)
        _, self.config.print_stuck_debug = imgui.checkbox("Print Stuck Debug", self.config.print_stuck_debug)
        _, self.config.print_despawn_debug = imgui.checkbox("Print Despawn Debug", self.config.print_despawn_debug)
            
        imgui.text(f"Nodes: {len(self.manager.city_gen.graph.nodes)}")
        imgui.text(f"Edges: {len(self.manager.city_gen.graph.edges)}")
        imgui.text("Green = Forward Lane")
        imgui.text("Red = Backward Lane")
        
        imgui.separator()
        imgui.text("Skybox Controls")
        _, self.visuals.skybox.time_scale = imgui.slider_float("Time Scale", self.visuals.skybox.time_scale, 0.0, 50.0)
        _, self.visuals.skybox.current_time = imgui.slider_float("Time of Day", self.visuals.skybox.current_time, 0.0, 24.0)
        
        # Display nicely
        h = int(self.visuals.skybox.current_time)
        m = int((self.visuals.skybox.current_time - h) * 60)
        imgui.text(f"Clock: {h:02d}:{m:02d}")

        imgui.separator()
        imgui.separator()
        imgui.text("Camera Tracking")
        
        # Input Int for ID
        changed, self.camera_ctrl.target_id = imgui.input_int("Car ID", self.camera_ctrl.target_id)
        
        if not self.camera_ctrl.is_tracking:
            if imgui.button("Track Car"):
                self.camera_ctrl.track_agent(self.camera_ctrl.target_id)
        else:
            if imgui.button("Stop Tracking"):
                self.camera_ctrl.stop_tracking()
            
            imgui.same_line()
            if self.camera_ctrl.found:
                imgui.text_colored("Following", 0.0, 1.0, 0.0)
            else:
                imgui.text_colored("Not Found", 1.0, 0.0, 0.0)
 
        imgui.end()
