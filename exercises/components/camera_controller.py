import glm

class CameraController:
    def __init__(self, camera):
        self.camera = camera
        self.is_tracking = False
        self.target_id = 0
        self.found = False
        
    def track_agent(self, agent_id):
        self.target_id = int(agent_id)
        self.is_tracking = True
        
    def stop_tracking(self):
        self.is_tracking = False
        self.found = False
        
    def update(self, dt, agents):
        if not self.is_tracking:
            self.camera.update(dt)
        else:
            target = next((a for a in agents if a.id == self.target_id), None)
            self.found = (target is not None)
            
            if target:
                offset_dist = 15.0
                # Third person: Behind and above
                desired = target.position - (target.orientation * offset_dist) + glm.vec3(0, 6.0, 0)
                self.camera.position = desired
                
                # Look at target
                look_target = target.position + glm.vec3(0, 2.0, 0)
                self.camera.front = glm.normalize(look_target - self.camera.position)
                self.camera.updateView()
                
                # Sync Euler angles to prevent snapping when exiting tracking
                pitch_rad = glm.asin(max(min(self.camera.front.y, 1.0), -1.0)) 
                self.camera.euler_angles.x = glm.degrees(pitch_rad)
                self.camera.euler_angles.y = glm.degrees(glm.atan(self.camera.front.z, self.camera.front.x))
            else:
                # If target lost, fallback to free cam or just stay? 
                # Original logic just did nothing if target was None but kept is_tracking=True
                # But we should probably allow moving camera if target is gone?
                # For now, stick to original logic: if target not found, do nothing (camera stays put)
                pass
