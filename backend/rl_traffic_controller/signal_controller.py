import time

class TrafficSignalController:
    def __init__(self, phases=4):
        self.phases = phases
        self.current_phase = 0
        self.last_change = time.time()
        self.emergency_mode = False
        
    def change_phase(self, new_phase):
        if self._validate_phase_change(new_phase):
            print(f"Changing to phase {new_phase}")
            self.current_phase = new_phase
            self.last_change = time.time()
            return True
        return False
    
    def emergency_override(self):
        print("Activating emergency override!")
        self.emergency_mode = True
        self.current_phase = 3  # Special emergency phase
        self.last_change = time.time()
        
    def _validate_phase_change(self, new_phase):
        min_green = 15 if not self.emergency_mode else 5
        elapsed = time.time() - self.last_change
        return (
            new_phase in range(self.phases) and
            elapsed >= min_green and
            not self.emergency_mode
        )