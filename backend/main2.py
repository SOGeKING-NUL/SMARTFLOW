import cv2
import numpy as np
from collections import defaultdict, deque
from ultralytics import YOLO

class VehicleCounter:
    def __init__(self, model_path='yolov8n.pt'):
        """Initialize the VehicleCounter with YOLO model and configurations."""
        try:
            self.model = YOLO(model_path)
        except Exception as e:
            raise RuntimeError(f"Failed to load YOLO model: {e}")
            
        self.vehicle_classes = {
            2: 'car',
            3: 'motorcycle',
            5: 'bus',
            7: 'truck'
        }
        self.tracks = {}
        self.next_id = 0
        self.direction_counts = defaultdict(lambda: defaultdict(int))
        self.min_displacement = 50  # Minimum movement to count direction
        self.max_distance = 100     # Max pixel distance for ID matching
        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def _calculate_direction(self, old_center, new_center):
        """Calculate movement direction based on center points."""
        dx = new_center[0] - old_center[0]
        dy = new_center[1] - old_center[1]
        
        if abs(dx) + abs(dy) < self.min_displacement:
            return None
        
        angle = np.degrees(np.arctan2(dy, dx))
        
        if -45 <= angle < 45:
            return 'east'
        elif 45 <= angle < 135:
            return 'south'
        elif -135 <= angle < -45:
            return 'north'
        return 'west'

    def _match_tracks(self, current_detections):
        """Match existing tracks with new detections and update tracking data."""
        updated_tracks = {}
        used_detections = set()

        # Match existing tracks
        for track_id, track_data in self.tracks.items():
            last_center = track_data['centroid_history'][-1]
            best_match_idx = None
            min_dist = self.max_distance

            for i, (center, cls_id, bbox) in enumerate(current_detections):
                if i in used_detections:
                    continue
                dist = np.linalg.norm(np.array(center) - np.array(last_center))
                if dist < min_dist:
                    min_dist = dist
                    best_match_idx = i

            if best_match_idx is not None:
                center, cls_id, bbox = current_detections[best_match_idx]
                used_detections.add(best_match_idx)
                track_data['centroid_history'].appendleft(center)
                track_data['class_id'] = cls_id
                track_data['bbox'] = bbox
                updated_tracks[track_id] = track_data

        # Add new detections as new tracks
        for i, (center, cls_id, bbox) in enumerate(current_detections):
            if i not in used_detections:
                updated_tracks[self.next_id] = {
                    'centroid_history': deque([center], maxlen=10),
                    'class_id': cls_id,
                    'bbox': bbox
                }
                self.next_id += 1

        self.tracks = updated_tracks

    def process_frame(self, frame):
        """Process a single frame and return annotated frame."""
        if frame is None or frame.size == 0:
            return frame

        # Detect objects
        results = self.model(frame, verbose=False)
        current_detections = []
        
        # Extract vehicle detections
        for box in results[0].boxes:
            cls_id = int(box.cls[0])
            if cls_id in self.vehicle_classes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                center = ((x1 + x2) // 2, (y1 + y2) // 2)
                current_detections.append((center, cls_id, (x1, y1, x2, y2)))

        # Update tracking
        self._match_tracks(current_detections)

        # Draw annotations and update counts
        for track_id, track_data in self.tracks.items():
            x1, y1, x2, y2 = track_data['bbox']
            class_name = self.vehicle_classes[track_data['class_id']]
            
            # Draw bbox and label
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            label = f"{class_name} {track_id}"
            cv2.putText(frame, label, (x1, y1 - 10), self.font, 0.5, (0, 255, 0), 2)

            # Update direction counts for stable tracks
            if len(track_data['centroid_history']) >= 5:
                old_center = track_data['centroid_history'][-1]
                new_center = track_data['centroid_history'][0]
                direction = self._calculate_direction(old_center, new_center)
                
                if direction:
                    self.direction_counts[direction][class_name] += 1
                    track_data['centroid_history'] = deque([new_center], maxlen=10)

        return frame

    def get_counts(self):
        """Return current direction counts."""
        return dict(self.direction_counts)

def process_video(video_path):
    """Process video file and display results."""
    try:
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video file: {video_path}")

        counter = VehicleCounter()
        
        while True:
            ret, frame = cap.read()
            if not ret:
                break
                
            annotated_frame = counter.process_frame(frame)
            counts = counter.get_counts()
            
            # Display counts on frame
            y_pos = 30
            for direction, types in counts.items():
                text = f"{direction}: " + ", ".join(f"{k}:{v}" for k, v in types.items())
                cv2.putText(annotated_frame, text, (10, y_pos), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                y_pos += 30
            
            cv2.imshow('Vehicle Counter', annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
                
    except Exception as e:
        print(f"Error processing video: {e}")
    finally:
        cap.release()
        cv2.destroyAllWindows()

if __name__ == "__main__":
    video_path = 'C:/Users/Piyush/Desktop/Personal Work/DEKHO/backend/data/test2.mp4'
    process_video(video_path)