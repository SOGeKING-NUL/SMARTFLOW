import cv2
import numpy as np
from ultralytics import YOLO
import time
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CarIntersectionCounter:
    def __init__(self, model_path='yolov8x.pt'):
        """Initialize the CarIntersectionCounter with YOLO model."""
        try:
            self.model = YOLO(model_path)  # Load YOLOv8 model
            logger.info("YOLOv8 model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load YOLO model: {e}")
            raise RuntimeError(f"Failed to load YOLO model: {e}")
        
        # Define car class ID (class 2 for 'car' in COCO dataset)
        self.car_class_id = 2
        self.conf_threshold = 0.3  # Lowered confidence threshold for testing
        self.class_names = self.model.names  # Get class names from the model
        
        # Define fixed rectangular region of interest (ROI) for intersection
        # Adjust these coordinates based on your webcam resolution
        self.roi = {
            'x1': 200,  # Top-left x
            'y1': 150,  # Top-left y
            'x2': 600,  # Bottom-right x
            'y2': 450   # Bottom-right y
        }
        
        # Calculate ROI area for density
        self.roi_area = (self.roi['x2'] - self.roi['x1']) * (self.roi['y2'] - self.roi['y1'])
        
        self.car_count = 0  # Counter for cars in the ROI
        self.car_details = []  # List to store details of detected cars
        self.frame_count = 0  # Track frames for debugging

    def detect_cars(self, frame):
        """Detect cars in the frame using YOLOv8 and return detections."""
        try:
            results = self.model(frame, conf=self.conf_threshold, verbose=False)
            cars = []
            
            logger.debug(f"Processing frame {self.frame_count} with YOLOv8.")
            for result in results:
                for box in result.boxes:
                    cls_id = int(box.cls[0])
                    conf = box.conf[0].item()
                    
                    # Check if the detected object is a car and meets confidence threshold
                    if cls_id == self.car_class_id and conf > self.conf_threshold:
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        cars.append([x1, y1, x2, y2, conf])
                        logger.debug(f"Detected car at ({x1}, {y1}, {x2}, {y2}) with confidence {conf:.2f}")
                    else:
                        logger.debug(f"Detected non-car object (class {cls_id}, conf {conf:.2f})")
            
            return np.array(cars) if cars else np.array([])
        except Exception as e:
            logger.error(f"Error in detect_cars: {e}")
            return np.array([])

    def is_car_in_roi(self, bbox):
        """Check if a car's bounding box is within the ROI."""
        x1, y1, x2, y2 = bbox
        roi_x1, roi_y1, roi_x2, roi_y2 = self.roi.values()
        
        # Check if any part of the bounding box overlaps with the ROI
        return (x1 < roi_x2 and x2 > roi_x1 and y1 < roi_y2 and y2 > roi_y1)

    def process_frame(self, frame):
        """Process a frame, detect cars, count those in the ROI, and display details."""
        try:
            # Detect cars
            cars = self.detect_cars(frame)
            self.car_count = 0
            self.car_details = []  # Reset details for this frame
            
            for car in cars:
                x1, y1, x2, y2, conf = car
                in_roi = self.is_car_in_roi([x1, y1, x2, y2])
                
                if in_roi:
                    self.car_count += 1
                    color = (0, 255, 0)  # Green for cars in ROI
                    # Store car details (x1, y1, x2, y2, confidence)
                    self.car_details.append({
                        'bbox': (x1, y1, x2, y2),
                        'confidence': conf
                    })
                else:
                    color = (0, 0, 255)  # Red for cars outside ROI
                
                # Draw bounding box
                cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
                
                # Add confidence and class name text
                label = f"Car {conf:.2f}"
                cv2.putText(frame, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)
            
            # Draw ROI rectangle
            cv2.rectangle(frame, (self.roi['x1'], self.roi['y1']), 
                         (self.roi['x2'], self.roi['y2']), (255, 0, 0), 2)
            
            # Calculate density (cars per unit area in ROI)
            density = (self.car_count / self.roi_area) * 1000  # Density in cars per 1000 pixels^2
            
            # Add car count and density text
            cv2.putText(frame, f"Cars in Intersection: {self.car_count}", 
                       (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
            cv2.putText(frame, f"Density: {density:.2f} cars/1000px²", 
                       (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
            
            # Display car details on frame
            y_offset = 110
            for detail in self.car_details:
                x1, y1, x2, y2 = detail['bbox']
                conf = detail['confidence']
                detail_text = f"Car: x1={x1}, y1={y1}, x2={x2}, y2={y2}, Conf={conf:.2f}"
                cv2.putText(frame, detail_text, (10, y_offset), 
                           cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)
                y_offset += 30

            self.frame_count += 1
            return frame
        except Exception as e:
            logger.error(f"Error in process_frame: {e}")
            return frame

def main():
    # Initialize the counter
    counter = CarIntersectionCounter()
    
    # Initialize webcam (use 0 for default webcam, 1 for external)
    cap = cv2.VideoCapture(1)
    if not cap.isOpened():
        logger.error("Error: Could not open webcam.")
        return

    # Get actual webcam resolution for debugging
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    logger.info(f"Webcam resolution: {width}x{height}")

    # Set desired resolution (optional, adjust based on your webcam)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 800)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 600)

    # Window settings
    cv2.namedWindow('Car Detection in Intersection', cv2.WINDOW_NORMAL)
    
    try:
        print("Starting car detection in intersection...")
        start_time = time.time()
        while True:
            ret, frame = cap.read()
            if not ret:
                logger.error("Error: Could not read frame from webcam.")
                break

            # Process frame
            processed_frame = counter.process_frame(frame)
            
            # Display frame
            cv2.imshow('Car Detection in Intersection', processed_frame)
            
            # Break on 'q' key or after 5 minutes (optional limit)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            if time.time() - start_time > 300:  # Stop after 5 minutes
                logger.info("Stopping after 5 minutes.")
                break

    except Exception as e:
        logger.error(f"Error occurred: {str(e)}")
    finally:
        cap.release()
        cv2.destroyAllWindows()
        logger.info(f"Total cars detected in intersection: {counter.car_count}")
        logger.info(f"Final car details: {counter.car_details}")
        logger.info(f"Total frames processed: {counter.frame_count}")

if __name__ == "__main__":
    main()