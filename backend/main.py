import cv2
import numpy as np
import time
from models.area_counter import AreaVehicleCounter
from rl_traffic_controller.traffic_env import TrafficSignalEnv
from rl_traffic_controller.agent import TrafficRLAgent
from rl_traffic_controller.signal_controller import TrafficSignalController

class TrafficSimulator:
    def __init__(self):
        self.frame_width = 800
        self.frame_height = 600
        self.vehicles = []
        self.next_id = 0
        self.colors = {
            "north": (0, 255, 0),
            "south": (0, 255, 0),
            "east": (0, 0, 255),
            "west": (0, 0, 255)
        }
        self.traffic_env = None

    def set_traffic_env(self, env):
        self.traffic_env = env

    def generate_frame(self):
        frame = np.zeros((self.frame_height, self.frame_width, 3), dtype=np.uint8)
        
        cv2.rectangle(frame, (200, 0), (600, 600), (50, 50, 50), -1)  # Wider NS road
        cv2.rectangle(frame, (0, 150), (800, 450), (50, 50, 50), -1)  # Wider EW road
        
        if np.random.rand() < 0.1:
            self._add_vehicle()
            
        self._move_vehicles()
        
        for vehicle in self.vehicles:
            x, y, w, h, vid, direction = vehicle
            color = self.colors[direction]
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, -1)
        
        return frame, np.array([[x, y, x+w, y+h, vid] for x, y, w, h, vid, _ in self.vehicles])

    def _add_vehicle(self):
        w, h = 40, 20
        direction = np.random.choice(["north", "south", "east", "west"])
        
        if direction == "north":
            x = np.random.randint(350, 450)
            y = -h
        elif direction == "south":
            x = np.random.randint(350, 450)
            y = self.frame_height
        elif direction == "east":
            x = self.frame_width
            y = np.random.randint(250, 350)
        else:
            x = -w
            y = np.random.randint(250, 350)
            
        self.vehicles.append([x, y, w, h, self.next_id, direction])
        self.next_id += 1

    def _move_vehicles(self):
        stop_line = {
            "north": self.frame_height//2 - 20,
            "south": self.frame_height//2 + 20,
            "east": self.frame_width//2 - 20,
            "west": self.frame_width//2 + 20
        }

        intersection_start = {
            "north": self.frame_height//2 - 150,
            "south": self.frame_height//2 + 150,
            "east": self.frame_width//2 - 150,
            "west": self.frame_width//2 + 150
        }

        for i in range(len(self.vehicles) - 1, -1, -1):
            x, y, w, h, vid, direction = self.vehicles[i]
            
            current_allowed = self.traffic_env.allowed_directions if self.traffic_env else []
            
            if direction in current_allowed:
                current_speed = 5  # Full speed when green
            else:
                axis = y if direction in ["north", "south"] else x
                dist = abs(axis - stop_line[direction])
                current_speed = min(5, max(0, dist//5))  # Gradual stopping

            # Update position, ensuring vehicles stay in their lanes and don’t enter intersection unless green
            if direction == "north":
                if y < intersection_start["north"] or direction in current_allowed:
                    y += current_speed
                if y > stop_line["north"] + h and direction not in current_allowed:
                    y = stop_line["north"] + h  # Stop just past stop line
            elif direction == "south":
                if y > intersection_start["south"] or direction in current_allowed:
                    y -= current_speed
                if y < stop_line["south"] - h and direction not in current_allowed:
                    y = stop_line["south"] - h  # Stop just past stop line
            elif direction == "east":
                if x > intersection_start["east"] or direction in current_allowed:
                    x -= current_speed
                if x < stop_line["east"] + w and direction not in current_allowed:
                    x = stop_line["east"] + w  # Stop just past stop line
            else:  # west
                if x < intersection_start["west"] or direction in current_allowed:
                    x += current_speed
                if x > stop_line["west"] - w and direction not in current_allowed:
                    x = stop_line["west"] - w  # Stop just past stop line

            # Check if vehicle is off-screen (remove if outside bounds with buffer)
            if x < -100 or x > self.frame_width + 100 or y < -100 or y > self.frame_height + 100:
                del self.vehicles[i]
            else:
                self.vehicles[i] = [x, y, w, h, vid, direction]

def draw_traffic_lights(frame, phase):
    ns_color = (0, 255, 0) if phase in [0, 3] else (0, 0, 255)
    cv2.circle(frame, (400, 100), 20, ns_color, -1)
    
    ew_color = (0, 255, 0) if phase in [1, 2] else (0, 0, 255)
    cv2.circle(frame, (700, 300), 20, ew_color, -1)


def main():
    print("Initializing traffic simulation...")
    simulator = TrafficSimulator()
    area_counter = AreaVehicleCounter()
    signal_controller = TrafficSignalController(phases=4)
    traffic_env = TrafficSignalEnv(area_counter, signal_controller)
    simulator.set_traffic_env(traffic_env)
    agent = TrafficRLAgent(traffic_env)

    episode_duration = 300
    frame_delay = 50
    frame_count = 0

    cv2.namedWindow('Traffic Control Simulation', cv2.WINDOW_NORMAL)
    
    try:
        start_time = time.time()
        obs, _ = traffic_env.reset()
        
        while (time.time() - start_time) < episode_duration:
            frame, detections = simulator.generate_frame()
            counts, densities = area_counter.update(detections, frame.shape)
            
            action = agent.predict_action(obs)
            obs, reward, done, _, _ = traffic_env.step(action)

            frame = area_counter.draw_visualization(frame)
            draw_traffic_lights(frame, traffic_env.current_phase)
            
            phase_time = time.time() - traffic_env.phase_start_time
            
            metrics = [
                f"Phase {traffic_env.current_phase}: {phase_time:.1f}s",
                f"Vehicles: {len(detections)}"
            ]
            
            text_color = (255, 255, 255)
            bg_color = (0, 0, 0, 100)
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.8
            thickness = 2
            
            max_width = 0
            total_height = 0
            for text in metrics:
                (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
                max_width = max(max_width, text_w)
                total_height += text_h + 10
            
            x, y = 10, 10
            box_w, box_h = max_width + 20, total_height + 10
            
            overlay = frame.copy()
            cv2.rectangle(overlay, (x, y), (x + box_w, y + box_h), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)
            
            y_pos = 20
            for text in metrics:
                cv2.putText(frame, text, (x + 10, y_pos), font, font_scale, text_color, thickness)
                y_pos += 30

            cv2.imshow('Traffic Control Simulation', frame)
            frame_count += 1

            if cv2.waitKey(frame_delay) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        cv2.destroyAllWindows()
        print(f"Simulation completed\nTotal frames rendered: {frame_count}")

if __name__ == "__main__":
    main()