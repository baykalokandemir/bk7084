import imgui
import random

class CityUI:
    def __init__(self, config, manager, visuals, renderer, camera_ctrl):
        self.config = config
        self.manager = manager
        self.visuals = visuals
        self.renderer = renderer
        self.camera_ctrl = camera_ctrl

    def draw(self):
        """
        Draws the City Control UI with organized collapsible sections.
        """
        imgui.begin("City Controls")
        
        # === CITY SETTINGS ===
        if imgui.collapsing_header("City Settings", imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            _, self.config.show_buildings = imgui.checkbox("Show Buildings", self.config.show_buildings)
            
            if imgui.button("Regenerate City"):
                self.manager.regenerate_world(self.visuals, self.config)
        
        # === TRAFFIC CONTROLS ===
        if imgui.collapsing_header("Traffic Controls", imgui.TREE_NODE_DEFAULT_OPEN)[0]:
            _, self.config.num_cars_to_brake = imgui.input_int("Num to Brake", self.config.num_cars_to_brake)
            
            if imgui.button("Brake Random Cars"):
                count = self.manager.brake_random_agents(self.config.num_cars_to_brake)
                print(f"[USER] Manually braked {count} cars.")
            
            imgui.same_line()
            if imgui.button("Release All"):
                self.manager.release_all_brakes()
                print("[USER] Released all manual brakes.")
            
            _, self.config.reckless_chance = imgui.slider_float("Reckless %", self.config.reckless_chance, 0.0, 1.0)
            _, self.config.target_agent_count = imgui.slider_int("Car Count", self.config.target_agent_count, 0, 50)
            
            imgui.text(f"Total Crashes: {self.config.total_crashes}")
            
            if imgui.button("Clear Wrecks"):
                self.manager.clear_crashes()
        
        # === HOLOGRAMS ===
        if imgui.collapsing_header("Holograms")[0]:
            _, self.config.show_holograms = imgui.checkbox("Show Holograms", self.config.show_holograms)
            
            changed, self.config.target_hologram_count = imgui.slider_int("Num Holograms", self.config.target_hologram_count, 0, 20)
            if changed or imgui.button("Regenerate Holograms"):
                self.visuals.regenerate_holograms(self.config.target_hologram_count)
        
        # === SKYBOX ===
        if imgui.collapsing_header("Skybox")[0]:
            h = int(self.visuals.skybox.current_time)
            m = int((self.visuals.skybox.current_time - h) * 60)
            imgui.text(f"Clock: {h:02d}:{m:02d}")
            
            _, self.config.show_skybox = imgui.checkbox("Show Skybox", self.config.show_skybox)
            _, self.visuals.skybox.time_scale = imgui.slider_float("Time Scale", self.visuals.skybox.time_scale, 0.0, 50.0)
            _, self.visuals.skybox.current_time = imgui.slider_float("Time of Day", self.visuals.skybox.current_time, 0.0, 24.0)
        
        # === CLOUDS ===
        if imgui.collapsing_header("Clouds")[0]:
            _, self.config.show_clouds = imgui.checkbox("Show Clouds", self.config.show_clouds)
        
        # === CAMERA ===
        if imgui.collapsing_header("Camera")[0]:
            _, self.camera_ctrl.target_id = imgui.input_int("Car ID", self.camera_ctrl.target_id)
            
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
        
        # === DEBUG ===
        if imgui.collapsing_header("Debug")[0]:
            _, self.config.crash_debug = imgui.checkbox("Crash Debug (Technical)", self.config.crash_debug)
            _, self.config.crash_report_debug = imgui.checkbox("Crash Report (N-Way)", self.config.crash_report_debug)
            _, self.config.print_stuck_debug = imgui.checkbox("Print Stuck Debug", self.config.print_stuck_debug)
            _, self.config.print_despawn_debug = imgui.checkbox("Print Despawn Debug", self.config.print_despawn_debug)
            
            imgui.separator()
            imgui.text(f"Nodes: {len(self.manager.city_gen.graph.nodes)}")
            imgui.text(f"Edges: {len(self.manager.city_gen.graph.edges)}")
        
        imgui.end()
