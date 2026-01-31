import imgui
import random

class CityUI:
    def __init__(self, config):
        self.config = config

    def draw(self, city_gen, agents, current_objects, glrenderer, crash_shape, skybox, tracking_state, on_regenerate, on_regenerate_holograms):
        """
        Draws the City Control UI.
        
        Args:
            city_gen: CityGenerator instance for graph stats.
            agents: List of active CarAgents.
            current_objects: List of renderable objects (for cleanup).
            glrenderer: Renderer definition (for cleanup).
            crash_shape: Shape used for crash visuals (for identification).
            skybox: Skybox instance for time control.
            tracking_state: Dictionary for camera tracking state.
            on_regenerate: Callback function to regenerate city.
            on_regenerate_holograms: Callback function to regenerate holograms.
        """
        imgui.begin("City Controls")
        
        if imgui.button("Regenerate"):
            on_regenerate()
            
        imgui.text(f"Total Crashes: {self.config.total_crashes}")
            
        _, self.config.num_cars_to_brake = imgui.input_int("Num to Brake", self.config.num_cars_to_brake)
        if imgui.button("Brake Random Cars"):
            count = min(self.config.num_cars_to_brake, len(agents))
            if count > 0:
                candidates = [a for a in agents if not a.manual_brake and not a.is_reckless]
                targets = candidates if len(candidates) < count else random.sample(candidates, count)
                for t in targets: t.manual_brake = True
                print(f"[USER] Manually braked {len(targets)} cars.")
        
        if imgui.button("Release All"):
            for a in agents: a.manual_brake = False
            print("[USER] Released all manual brakes.")
            
        _, self.config.reckless_chance = imgui.slider_float("Reckless %", self.config.reckless_chance, 0.0, 1.0)
        
        if imgui.button("Clear Wrecks"):
             to_remove = [obj for obj in current_objects if obj.mesh == crash_shape]
             for obj in to_remove:
                 if obj in glrenderer.objects: glrenderer.objects.remove(obj)
                 current_objects.remove(obj)
             print(f"[USER] Cleared {len(to_remove)} wrecks.")

        _, self.config.target_agent_count = imgui.slider_int("Car Count", self.config.target_agent_count, 0, 50)
        
        imgui.separator()
        imgui.text("Holograms")
        changed, self.config.target_hologram_count = imgui.slider_int("Num Holograms", self.config.target_hologram_count, 0, 20)
        if changed or imgui.button("Regenerate Holograms"):
            on_regenerate_holograms()
            
        imgui.separator()
            
        _, self.config.show_buildings = imgui.checkbox("Show Buildings", self.config.show_buildings)
        _, self.config.show_clouds = imgui.checkbox("Show Clouds", self.config.show_clouds)
        _, self.config.show_holograms = imgui.checkbox("Show Holograms", self.config.show_holograms)
        _, self.config.show_skybox = imgui.checkbox("Show Skybox", self.config.show_skybox)
        _, self.config.crash_debug = imgui.checkbox("Crash Debug", self.config.crash_debug)
        _, self.config.print_stuck_debug = imgui.checkbox("Print Stuck Debug", self.config.print_stuck_debug)
        _, self.config.print_despawn_debug = imgui.checkbox("Print Despawn Debug", self.config.print_despawn_debug)
            
        imgui.text(f"Nodes: {len(city_gen.graph.nodes)}")
        imgui.text(f"Edges: {len(city_gen.graph.edges)}")
        imgui.text("Green = Forward Lane")
        imgui.text("Red = Backward Lane")
        
        imgui.separator()
        imgui.text("Skybox Controls")
        _, skybox.time_scale = imgui.slider_float("Time Scale", skybox.time_scale, 0.0, 50.0)
        _, skybox.current_time = imgui.slider_float("Time of Day", skybox.current_time, 0.0, 24.0)
        
        # Display nicely
        h = int(skybox.current_time)
        m = int((skybox.current_time - h) * 60)
        imgui.text(f"Clock: {h:02d}:{m:02d}")

        imgui.separator()
        imgui.text("Camera Tracking")
        
        # Input Int for ID
        changed, tracking_state["target_id"] = imgui.input_int("Car ID", tracking_state["target_id"])
        
        if not tracking_state["is_tracking"]:
            if imgui.button("Track Car"):
                tracking_state["is_tracking"] = True
        else:
            if imgui.button("Stop Tracking"):
                tracking_state["is_tracking"] = False
            
            imgui.same_line()
            if tracking_state["found"]:
                imgui.text_colored("Following", 0.0, 1.0, 0.0)
            else:
                imgui.text_colored("Not Found", 1.0, 0.0, 0.0)

        imgui.end()
