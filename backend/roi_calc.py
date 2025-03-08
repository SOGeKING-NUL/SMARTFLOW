import cv2
import numpy as np
from ultralytics import YOLO

# Load YOLOv8 model
model = YOLO("yolov8n.pt")  # You can use a different YOLOv8 model

# Define the source (video file or webcam)
source = "backend\data\dayROI.mp4"  # Change to 0 for webcam
cap = cv2.VideoCapture(source)

roi = None  # Region of Interest (to be set manually)

# Mouse callback function to select ROI
def select_roi(event, x, y, flags, param):
    global roi
    if event == cv2.EVENT_LBUTTONDOWN:
        roi = [(x, y)]
    elif event == cv2.EVENT_LBUTTONUP:
        roi.append((x, y))

# Create a window and set mouse callback
cv2.namedWindow("Frame")
cv2.setMouseCallback("Frame", select_roi)

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break
    
    # Resize frame for faster processing
    frame = cv2.resize(frame, (640, 480))
    
    # Run YOLO inference
    results = model(frame, stream=True)
    
    vehicle_count = 0
    
    for result in results:
        for box in result.boxes.xyxy:
            x1, y1, x2, y2 = map(int, box)
            label = result.names[int(result.boxes.cls[0])]
            
            # Check if detected object is a vehicle
            if label in ["car", "bus", "truck", "motorbike"]:
                vehicle_count += 1
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                cv2.putText(frame, label, (x1, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    
    # Draw the ROI if selected
    if roi and len(roi) == 2:
        cv2.rectangle(frame, roi[0], roi[1], (0, 0, 255), 2)
        
        # Count vehicles inside ROI
        x_min, y_min = roi[0]
        x_max, y_max = roi[1]
        
        vehicles_in_roi = 0
        for result in results:
            for box in result.boxes.xyxy:
                x1, y1, x2, y2 = map(int, box)
                if x_min < x1 < x_max and y_min < y1 < y_max:
                    vehicles_in_roi += 1
        
        # Display vehicle count inside ROI
        cv2.putText(frame, f"Vehicles in ROI: {vehicles_in_roi}", (x_min, y_min - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    
    # Display total vehicle count
    cv2.putText(frame, f"Total Vehicles: {vehicle_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
    
    # Show the frame
    cv2.imshow("Frame", frame)
    
    # Press 'q' to exit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
