from dataclasses import dataclass

@dataclass
class SimulationState:
    # Simulation Settings
    target_agent_count: int = 1
    reckless_chance: float = 0.2
    num_cars_to_brake: int = 5
    
    # Visual Toggles
    show_buildings: bool = True
    show_clouds: bool = False
    show_holograms: bool = False
    show_skybox: bool = True
    
    # Debug Flags
    crash_debug: bool = False
    crash_report_debug: bool = False # [NEW] Detailed N-way crash reports
    print_stuck_debug: bool = False
    print_despawn_debug: bool = False
    
    # Hologram Settings
    target_hologram_count: int = 5
    
    # Metrics (Mutable state tracked by simulation)
    total_crashes: int = 0
