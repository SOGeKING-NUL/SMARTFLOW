import cv2
import numpy as np
import time
from models.area_counter import AreaVehicleCounter
import torch
from ultralytics import YOLO

class WebcamVideoProcessor:
    def __init__(self, source=1, frame_width=800, frame_height=600):
        """
        Initialize with an external webcam (source=1) or video file (source='path/to/video.mp4').
        """
        self.frame_width = frame_width
        self.frame_height = frame_height
        self.cap = cv2.VideoCapture(source)  # Use 1 for external webcam, or path to video file
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, frame_width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, frame_height)
        if not self.cap.isOpened():
            raise RuntimeError(f"Could not open {'external webcam' if source == 1 else 'video file'}")

        # Load YOLOv8n model for vehicle detection
        self.model = YOLO('yolov8n.pt')  # Pre-trained YOLOv8 Nano model
        self.class_names = self.model.names
        # Expand vehicle classes to include more types (e.g., bicycles, trucks, etc.)
        self.vehicle_classes = [0, 1, 2, 3, 5, 7]  # person, bicycle, car, motorcycle, bus, truck

    def detect_vehicles(self, frame):
        """
        Detect vehicles using YOLOv8n with improved settings and return detections in [x1, y1, x2, y2, track_id] format.
        """
        # Preprocess frame for better detection (adjust brightness/contrast if needed)
        frame = cv2.convertScaleAbs(frame, alpha=1.2, beta=10)  # Increase brightness and contrast slightly

        # Perform inference with lower confidence threshold and higher image quality
        results = self.model(frame, conf=0.3, iou=0.7)  # Lower confidence (0.3), higher IoU (0.7) for small objects
        detections = []
        track_id_counter = 0  # Simple tracking (can be enhanced with DeepSORT for persistent IDs)

        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                conf = box.conf[0].item()
                cls = int(box.cls[0].item())

                # Check if the detected object is a vehicle or related object
                if cls in self.vehicle_classes and conf > 0.3:
                    # Ensure detections fit within frame to avoid out-of-bounds errors
                    x1 = max(0, min(x1, self.frame_width - 1))
                    y1 = max(0, min(y1, self.frame_height - 1))
                    x2 = max(0, min(x2, self.frame_width - 1))
                    y2 = max(0, min(y2, self.frame_height - 1))
                    
                    # Use a simple frame-based tracking (incremental track_id for this frame)
                    track_id = track_id_counter
                    track_id_counter += 1
                    detections.append([x1, y1, x2, y2, track_id])

                    # Optional: Draw bounding boxes for debugging (remove in final version)
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                    cv2.putText(frame, f"{self.class_names[cls]} {conf:.2f}", (x1, y1-10),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

        return np.array(detections) if detections else np.array([])

    def generate_frame(self):
        """
        Capture and process a frame from the external webcam, returning the frame and vehicle detections.
        """
        ret, frame = self.cap.read()
        if not ret:
            raise RuntimeError("Failed to capture frame from external webcam")
        
        # Resize frame to match desired dimensions (800x600)
        frame = cv2.resize(frame, (self.frame_width, self.frame_height))
        
        detections = self.detect_vehicles(frame)
        return frame, detections

    def release(self):
        """Release the video capture resource."""
        self.cap.release()

def draw_traffic_lights(frame, phase):
    """
    Draw traffic light indicators on the frame (for visualization only, no control here).
    """
    ns_color = (0, 255, 0) if phase in [0, 3] else (0, 0, 255)  # Green for NS, Red for EW
    cv2.circle(frame, (400, 100), 20, ns_color, -1)  # North-South light (top)
    ew_color = (0, 255, 0) if phase in [1, 2] else (0, 0, 255)  # Green for EW, Red for NS
    cv2.circle(frame, (700, 300), 20, ew_color, -1)  # East-West light (right)



def main(source=1):
    """
    Main function to process external webcam input, detect vehicles, calculate density, and display results.
    Use source=1 for external webcam, or provide a video file path (e.g., 'path/to/video.mp4').
    """
    print(f"Initializing traffic monitoring with external webcam...")
    processor = WebcamVideoProcessor(source=source)
    area_counter = AreaVehicleCounter()
    phase = 0  # Simulated phase (0-3) for visualization; in RL, this would come from TrafficSignalEnv

    # Set default ROIs for the 800x600 frame (adjust based on your road layout)
    frame_shape = (600, 800)  # Height, Width
    area_counter.update(np.array([]), frame_shape)  # Initialize ROIs

    episode_duration = 300  # 5 minutes
    frame_delay = 50  # ms (adjust for real-time performance)
    frame_count = 0

    cv2.namedWindow(f'Traffic Monitoring from External Webcam', cv2.WINDOW_NORMAL)
    
    try:
        start_time = time.time()
        
        while (time.time() - start_time) < episode_duration:
            frame, detections = processor.generate_frame()
            counts, densities = area_counter.update(detections, frame.shape)
            
            # Simulate phase change (for visualization; RL would handle this)
            phase_time = time.time() - start_time
            if phase_time > 30:  # Change phase every 30 seconds (simplified logic)
                phase = (phase + 1) % 4
                start_time = time.time()

            frame = area_counter.draw_visualization(frame)
            draw_traffic_lights(frame, phase)
            
            # Display improved metrics (phase, vehicles, and lane-wise densities)
            metrics = [
                f"Phase {phase}: {phase_time:.1f}s",
                f"Vehicles: {len(detections)}"
            ]
            
            # Enhanced text display with better background and formatting
            text_color = (255, 255, 255)  # White text
            bg_color = (0, 0, 0, 150)     # Darker black background with higher opacity
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 1.0              # Larger font for better readability
            thickness = 2
            
            # Calculate text sizes for background box
            max_width = 0
            total_height = 0
            for text in metrics:
                (text_w, text_h), _ = cv2.getTextSize(text, font, font_scale, thickness)
                max_width = max(max_width, text_w)
                total_height += text_h + 15  # Increased spacing for readability
            
            x, y = 10, 10
            box_w, box_h = max_width + 30, total_height + 20  # Larger padding for better contrast
            
            # Draw semi-transparent background box
            overlay = frame.copy()
            cv2.rectangle(overlay, (x, y), (x + box_w, y + box_h), (0, 0, 0), -1)
            cv2.addWeighted(overlay, 0.8, frame, 0.2, 0, frame)  # Higher opacity for better contrast
            
            # Draw metrics with improved positioning
            y_pos = 30
            for text in metrics + [f"North: {densities['north']:.1f}%", 
                                 f"South: {densities['south']:.1f}%", 
                                 f"East: {densities['east']:.1f}%", 
                                 f"West: {densities['west']:.1f}%"]:
                cv2.putText(frame, text, (x + 15, y_pos), font, font_scale, text_color, thickness)
                y_pos += 40  # Larger spacing for lane densities

            cv2.imshow(f'Traffic Monitoring from External Webcam', frame)
            frame_count += 1

            if cv2.waitKey(frame_delay) & 0xFF == ord('q'):
                break

    except Exception as e:
        print(f"Error occurred: {str(e)}")
        raise
    finally:
        processor.release()
        cv2.destroyAllWindows()
        print(f"Monitoring completed\nTotal frames rendered: {frame_count}")

if __name__ == "__main__":
    # Use source=1 for external webcam, or provide a video file path (e.g., 'path/to/video.mp4')
    main(source=1)  # Default to external webcam; change to video path for stock video