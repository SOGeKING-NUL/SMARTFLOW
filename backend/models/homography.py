import numpy as np
import cv2

class VirtualLineCounter:
    def __init__(self, line_y):
        self.line_y = line_y
        self.counts = {'north': 0, 'south': 0}
        self.track_history = {}
        self.max_history = 20
    
    def update(self, tracks):
        for track in tracks:
            if len(track) < 5:
                continue
            try:
                x1, y1, x2, y2, track_id = map(int, track[:5])
                y_center = (y1 + y2) // 2
                if track_id not in self.track_history:
                    self.track_history[track_id] = [y_center]
                    continue
                prev_y = self.track_history[track_id][-1]
                self.track_history[track_id].append(y_center)
                if prev_y <= self.line_y < y_center:
                    self.counts['south'] += 1
                elif prev_y >= self.line_y > y_center:
                    self.counts['north'] += 1
                if len(self.track_history[track_id]) > self.max_history:
                    self.track_history[track_id] = self.track_history[track_id][-self.max_history:]
            except ValueError:
                continue

class TrafficDensityCounter:
    def __init__(self, roi_points=None):
        self.roi_points = roi_points
        self.current_vehicles = set()
        self.density_history = []
        self.max_history = 100
    
    def set_roi(self, roi_points):
        self.roi_points = roi_points
    
    def point_in_roi(self, point):
        if self.roi_points is None:
            return True
        roi_np = np.array(self.roi_points, dtype=np.int32)
        return cv2.pointPolygonTest(roi_np, point, False) >= 0
    
    def update(self, tracks, frame_shape=None):
        self.current_vehicles.clear()
        if self.roi_points is None and frame_shape is not None:
            height, width = frame_shape[:2]
            self.roi_points = [(0, 0), (width, 0), (width, height), (0, height)]
        for track in tracks:
            if len(track) < 5:
                continue
            try:
                x1, y1, x2, y2, track_id = map(int, track[:5])
                center_x, center_y = (x1 + x2) // 2, (y1 + y2) // 2
                if self.point_in_roi((center_x, center_y)):
                    self.current_vehicles.add(track_id)
            except ValueError:
                continue
        
        current_density = len(self.current_vehicles)
        self.density_history.append(current_density)
        if len(self.density_history) > self.max_history:
            self.density_history = self.density_history[-self.max_history:]
        
        density_percentage = 0
        if self.roi_points is not None:
            roi_area = cv2.contourArea(np.array(self.roi_points, dtype=np.int32))
            avg_vehicle_area = 5000
            occupied_area = current_density * avg_vehicle_area
            density_percentage = min(100, (occupied_area / roi_area) * 100)
        
        return current_density, density_percentage
    
    def draw_roi(self, frame):
        if self.roi_points is not None:
            roi_np = np.array(self.roi_points, dtype=np.int32)
            cv2.polylines(frame, [roi_np], True, (0, 255, 255), 2)
            cv2.putText(frame, f"Vehicles in area: {len(self.current_vehicles)}", (10, 120), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        return frame
