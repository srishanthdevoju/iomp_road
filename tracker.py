"""
Object Tracker with Motion Detection
Tracks objects across frames and determines if they are approaching or departing
Uses bounding box size changes for more accurate motion detection
"""

import numpy as np
from collections import OrderedDict
from config import MAX_DISAPPEARED_FRAMES, MIN_VELOCITY_THRESHOLD


class CentroidTracker:
    def __init__(self, max_disappeared: int = MAX_DISAPPEARED_FRAMES):
        """Initialize centroid tracker."""
        self.next_object_id = 0
        self.objects = OrderedDict()      # id -> centroid
        self.disappeared = OrderedDict()   # id -> frames disappeared
        self.history = OrderedDict()       # id -> list of past centroids
        self.area_history = OrderedDict()  # id -> list of past bbox areas
        self.max_disappeared = max_disappeared
    
    def register(self, centroid: tuple, area: int = 0):
        """Register a new object."""
        self.objects[self.next_object_id] = centroid
        self.disappeared[self.next_object_id] = 0
        self.history[self.next_object_id] = [centroid]
        self.area_history[self.next_object_id] = [area]
        self.next_object_id += 1
    
    def deregister(self, object_id: int):
        """Deregister an object that has disappeared."""
        del self.objects[object_id]
        del self.disappeared[object_id]
        del self.history[object_id]
        if object_id in self.area_history:
            del self.area_history[object_id]
    
    def update(self, detections: list) -> dict:
        """
        Update tracker with new detections.
        
        Args:
            detections: List of detection dicts with 'center' and 'area' keys
            
        Returns:
            Dict mapping object IDs to their detection info + motion state
        """
        # If no detections, mark all as disappeared
        if len(detections) == 0:
            for object_id in list(self.disappeared.keys()):
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
            return {}
        
        input_centroids = [d['center'] for d in detections]
        
        # If no existing objects, register all
        if len(self.objects) == 0:
            for i, detection in enumerate(detections):
                self.register(detection['center'], detection.get('area', 0))
            return self._build_result(detections, list(range(len(detections))))
        
        # Match existing objects to new detections
        object_ids = list(self.objects.keys())
        object_centroids = list(self.objects.values())
        
        # Calculate distance matrix
        D = np.zeros((len(object_centroids), len(input_centroids)))
        for i, oc in enumerate(object_centroids):
            for j, ic in enumerate(input_centroids):
                D[i, j] = np.sqrt((oc[0] - ic[0])**2 + (oc[1] - ic[1])**2)
        
        # Match using greedy approach
        rows = D.min(axis=1).argsort()
        cols = D.argmin(axis=1)[rows]
        
        used_rows = set()
        used_cols = set()
        matched_ids = [-1] * len(detections)
        
        for row, col in zip(rows, cols):
            if row in used_rows or col in used_cols:
                continue
            if D[row, col] > 100:  # Max distance threshold
                continue
                
            object_id = object_ids[row]
            self.objects[object_id] = input_centroids[col]
            self.history[object_id].append(input_centroids[col])
            # Also track area
            area = detections[col].get('area', 0)
            self.area_history[object_id].append(area)
            if len(self.history[object_id]) > 30:  # Keep last 30 frames
                self.history[object_id].pop(0)
                self.area_history[object_id].pop(0)
            self.disappeared[object_id] = 0
            matched_ids[col] = object_id
            
            used_rows.add(row)
            used_cols.add(col)
        
        # Handle unmatched existing objects
        for row in range(len(object_centroids)):
            if row not in used_rows:
                object_id = object_ids[row]
                self.disappeared[object_id] += 1
                if self.disappeared[object_id] > self.max_disappeared:
                    self.deregister(object_id)
        
        # Register new objects
        for col in range(len(input_centroids)):
            if col not in used_cols:
                area = detections[col].get('area', 0)
                self.register(input_centroids[col], area)
                matched_ids[col] = self.next_object_id - 1
        
        return self._build_result(detections, matched_ids)
    
    def _build_result(self, detections: list, matched_ids: list) -> dict:
        """Build result dict with motion information."""
        result = {}
        
        for i, detection in enumerate(detections):
            object_id = matched_ids[i]
            if object_id == -1:
                continue
                
            motion = self._calculate_motion(object_id)
            
            result[object_id] = {
                **detection,
                'motion': motion['state'],
                'velocity': motion['velocity']
            }
        
        return result
    
    def _calculate_motion(self, object_id: int) -> dict:
        """Calculate motion state using bounding box size changes."""
        area_history = self.area_history.get(object_id, [])
        history = self.history.get(object_id, [])
        
        if len(area_history) < 5:
            return {'state': 'UNKNOWN', 'velocity': (0, 0)}
        
        # Calculate velocity for reference
        recent_pos = history[-5:]
        dx = (recent_pos[-1][0] - recent_pos[0][0]) / len(recent_pos)
        dy = (recent_pos[-1][1] - recent_pos[0][1]) / len(recent_pos)
        
        # Use area change for motion direction (more reliable)
        recent_areas = area_history[-10:] if len(area_history) >= 10 else area_history[-5:]
        if len(recent_areas) < 2:
            return {'state': 'UNKNOWN', 'velocity': (dx, dy)}
        
        # Calculate area change rate
        area_start = np.mean(recent_areas[:len(recent_areas)//2])
        area_end = np.mean(recent_areas[len(recent_areas)//2:])
        
        if area_start == 0:
            area_change = 0
        else:
            area_change = (area_end - area_start) / area_start
        
        # Determine motion based on area change
        # Growing bbox = approaching, shrinking = departing
        if abs(area_change) < 0.02:  # Less than 2% change = stationary
            state = 'STATIONARY'
        elif area_change > 0:  # Bbox getting bigger = approaching
            state = 'APPROACHING'
        else:  # Bbox getting smaller = departing
            state = 'DEPARTING'
        
        return {'state': state, 'velocity': (dx, dy), 'area_change': area_change}
