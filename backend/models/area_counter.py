import numpy as np
import cv2

class AreaVehicleCounter:
    def __init__(self):
        self.lane_rois = {
            'north': None,
            'south': None,
            'east': None,
            'west': None
        }
        self.lane_counts = {lane: 0 for lane in self.lane_rois}
        self.lane_densities = {lane: 0.0 for lane in self.lane_rois}
        self.density_percentage = 0.0
        self.avg_vehicle_area = 800  # Can be fine-tuned based on observation
        self.rois_initialized = False

    def reset(self):
        """Reset counters and densities to initial state."""
        self.lane_counts = {lane: 0 for lane in self.lane_rois}
        self.lane_densities = {lane: 0.0 for lane in self.lane_rois}
        self.density_percentage = 0.0
        return self.lane_counts, self.lane_densities

    def set_lane_roi(self, lane, points):
        """Set ROI for a specific lane with validation."""
        if lane not in self.lane_rois:
            raise ValueError(f"Invalid lane: {lane}")
        if len(points) < 3:
            raise ValueError("ROI must have at least 3 points")
        self.lane_rois[lane] = np.array(points, dtype=np.int32)
        self.rois_initialized = True

    def calculate_roi_area(self, lane):
        """Calculate the area of a lane ROI."""
        if lane not in self.lane_rois:
            raise ValueError(f"Invalid lane: {lane}")
        roi = self.lane_rois[lane]
        return cv2.contourArea(roi) if roi is not None else 0

    def update(self, detections, frame_shape=None):
        """Update vehicle counts and densities based on detections, with improved accuracy."""
        self.lane_counts = {lane: 0 for lane in self.lane_rois}
        vehicle_centers = []
        
        if frame_shape and not self.rois_initialized:
            self._set_default_rois(frame_shape)
            
        if not detections.size:
            self.lane_densities = {lane: 0.0 for lane in self.lane_rois}
            self.density_percentage = 0.0
            return self.lane_counts, self.lane_densities
            
        for det in detections:
            if len(det) < 5:
                continue
            try:
                x1, y1, x2, y2, track_id = map(int, det[:5])
                center = ((x1 + x2) // 2, (y1 + y2) // 2)
                
                # Avoid double-counting by checking proximity to existing centers
                if any(np.linalg.norm(np.array(center) - np.array(c)) < 30 for c in vehicle_centers):
                    continue
                vehicle_centers.append(center)
                
                # Assign to lane with highest containment, considering boundary overlap
                best_lane = None
                max_containment = -float('inf')  # Use negative infinity for initial max
                for lane, roi in self.lane_rois.items():
                    if roi is not None:
                        containment = cv2.pointPolygonTest(roi, center, False)
                        if containment >= 0 and containment > max_containment:
                            max_containment = containment
                            best_lane = lane
                if best_lane:
                    self.lane_counts[best_lane] += 1
            except (ValueError, TypeError) as e:
                print(f"Warning: Invalid detection format - {e}")
                continue
        
        # Calculate densities with refined overlap handling
        total_density = 0.0
        valid_lanes = 0
        for lane in self.lane_rois:
            area = self.calculate_roi_area(lane)
            if area > 0:
                vehicle_area = self.lane_counts[lane] * self.avg_vehicle_area
                # Apply non-linear scaling for congestion, with boundary adjustment
                density = min(100.0, (vehicle_area / area) * 100 * (1 + self.lane_counts[lane] * 0.05))
                self.lane_densities[lane] = density if density < 100 else 99.9  # Cap at 99.9 to avoid 100% saturation
                total_density += self.lane_densities[lane]
                valid_lanes += 1
        
        self.density_percentage = total_density / valid_lanes if valid_lanes > 0 else 0.0
        return self.lane_counts, self.lane_densities

    def _set_default_rois(self, shape):
        """Set default ROIs to match the wider road layout (200-600 for NS, 150-450 for EW)."""
        h, w = shape[:2]
        # Continuous lane ROIs, adjusted for wider roads and intersection alignment
        self.set_lane_roi('north', [
            (w//2-60, 0),        # Top-left, narrower for better fit
            (w//2+60, 0),        # Top-right
            (w//2+60, h//2-100), # Bottom-right, before intersection
            (w//2-60, h//2-100)  # Bottom-left
        ])
        self.set_lane_roi('south', [
            (w//2-60, h//2+100), # Top-left, after intersection
            (w//2+60, h//2+100), # Top-right
            (w//2+60, h),        # Bottom-right
            (w//2-60, h)         # Bottom-left
        ])
        self.set_lane_roi('east', [
            (w//2+50, h//2-60),  # Top-left, fits EW road
            (w, h//2-60),        # Top-right
            (w, h//2+60),        # Bottom-right
            (w//2+50, h//2+60)   # Bottom-left
        ])
        self.set_lane_roi('west', [
            (0, h//2-60),        # Top-left
            (w//2-50, h//2-60),  # Top-right, fits EW road
            (w//2-50, h//2+60),  # Bottom-right
            (0, h//2+60)         # Bottom-left
        ])

    def draw_visualization(self, frame):
        """Draw lane ROIs, stop lines, and lane-wise densities on the frame."""
        if frame is None:
            raise ValueError("Frame cannot be None")
            
        colors = {
            'north': (0, 255, 0),  # Green for North-South
            'south': (0, 255, 0),  # Green for North-South
            'east': (0, 0, 255),   # Red for East-West
            'west': (0, 0, 255)    # Red for East-West
        }
        
        # Draw lane ROIs
        for lane, roi in self.lane_rois.items():
            if roi is not None:
                cv2.polylines(frame, [roi], True, colors[lane], 2)
        
        # Draw stop lines (yellow) using frame dimensions
        h, w = frame.shape[:2]
        center_x, center_y = w//2, h//2  # Use frame shape for dynamic sizing
        cv2.line(frame, 
                 (center_x-80, center_y-20),  # North stop line
                 (center_x+80, center_y-20),  # North stop line
                 (0, 255, 255), 2)  # Yellow
        cv2.line(frame, 
                 (center_x-80, center_y+20),  # South stop line
                 (center_x+80, center_y+20),  # South stop line
                 (0, 255, 255), 2)  # Yellow
        
        # Draw lane-wise densities
        y_pos = 30
        for lane, density in self.lane_densities.items():
            cv2.putText(frame, f"{lane.capitalize()}: {density:.1f}%", 
                       (10, y_pos), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)
            y_pos += 30
            
        return frame