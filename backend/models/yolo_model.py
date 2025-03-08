# No actual YOLO needed for simulation
class VehicleCounter:
    def __init__(self):
        # Empty for simulation
        pass
    
    def process_frame(self, frame):
        # Detection data comes from simulator
        return []  # Not used in simulation version