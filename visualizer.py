"""
Visualization Module
Draws annotations, bounding boxes, and risk information on video frames
"""

import cv2
import numpy as np
from config import COLORS


class Visualizer:
    def __init__(self):
        """Initialize visualizer."""
        self.colors = COLORS
        self.font = cv2.FONT_HERSHEY_SIMPLEX
    
    def draw_frame(self, frame: np.ndarray, tracked_objects: dict, 
                   lane_boundaries: tuple = None) -> np.ndarray:
        """
        Draw all annotations on a frame.
        
        Args:
            frame: Original BGR frame
            tracked_objects: Dict with detected objects and their info
            lane_boundaries: Tuple of (left_x, right_x) for lane lines
            
        Returns:
            Annotated frame
        """
        annotated = frame.copy()
        
        # Draw lane boundaries
        if lane_boundaries:
            self._draw_lane_lines(annotated, lane_boundaries)
        
        # Draw each tracked object
        for obj_id, obj_info in tracked_objects.items():
            self._draw_object(annotated, obj_id, obj_info)
        
        # Draw summary overlay
        self._draw_summary(annotated, tracked_objects)
        
        return annotated
    
    def _draw_lane_lines(self, frame: np.ndarray, boundaries: tuple):
        """Draw lane boundary lines."""
        h = frame.shape[0]
        left_x, right_x = boundaries
        
        # Draw semi-transparent lane lines
        cv2.line(frame, (left_x, 0), (left_x, h), self.colors['lane_line'], 2)
        cv2.line(frame, (right_x, 0), (right_x, h), self.colors['lane_line'], 2)
        
        # Add lane labels at top
        cv2.putText(frame, "LEFT", (10, 25), self.font, 0.6, self.colors['lane_line'], 2)
        cv2.putText(frame, "CENTER", (left_x + 10, 25), self.font, 0.6, self.colors['lane_line'], 2)
        cv2.putText(frame, "RIGHT", (right_x + 10, 25), self.font, 0.6, self.colors['lane_line'], 2)
    
    def _draw_object(self, frame: np.ndarray, obj_id: int, obj_info: dict):
        """Draw bounding box and info for one object."""
        bbox = obj_info['bbox']
        risk = obj_info.get('risk', {})
        risk_level = risk.get('level', 'LOW')
        color = self.colors.get(risk_level, (0, 255, 0))
        
        x1, y1, x2, y2 = bbox
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
        
        # Build label text
        class_name = obj_info.get('class_name', 'object')
        motion = obj_info.get('motion', '')
        lane = obj_info.get('lane', '')
        risk_score = risk.get('score', 0)
        
        # Motion indicator (using ASCII-compatible text)
        if motion == 'APPROACHING':
            direction = "[COMING->]"
        elif motion == 'DEPARTING':
            direction = "[<-GOING]"
        elif motion == 'STATIONARY':
            direction = "[STOPPED]"
        else:
            direction = "[...]"
        
        label = f"{class_name} {direction}"
        info = f"{lane} | Risk: {risk_score:.0%}"
        
        # Draw label background
        (w1, h1), _ = cv2.getTextSize(label, self.font, 0.5, 1)
        (w2, h2), _ = cv2.getTextSize(info, self.font, 0.4, 1)
        max_w = max(w1, w2)
        
        cv2.rectangle(frame, (x1, y1 - 35), (x1 + max_w + 10, y1), color, -1)
        
        # Draw text
        cv2.putText(frame, label, (x1 + 5, y1 - 20), self.font, 0.5, (0, 0, 0), 1)
        cv2.putText(frame, info, (x1 + 5, y1 - 5), self.font, 0.4, (0, 0, 0), 1)
    
    def _draw_summary(self, frame: np.ndarray, tracked_objects: dict):
        """Draw summary statistics overlay."""
        h, w = frame.shape[:2]
        
        # Count objects and risk levels
        total = len(tracked_objects)
        critical = sum(1 for o in tracked_objects.values() 
                       if o.get('risk', {}).get('level') == 'CRITICAL')
        high = sum(1 for o in tracked_objects.values() 
                   if o.get('risk', {}).get('level') == 'HIGH')
        approaching = sum(1 for o in tracked_objects.values() 
                          if o.get('motion') == 'APPROACHING')
        
        # Draw summary box
        cv2.rectangle(frame, (w - 200, 10), (w - 10, 100), (0, 0, 0), -1)
        cv2.rectangle(frame, (w - 200, 10), (w - 10, 100), (255, 255, 255), 1)
        
        cv2.putText(frame, f"Objects: {total}", (w - 190, 35), 
                    self.font, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Approaching: {approaching}", (w - 190, 55), 
                    self.font, 0.5, (255, 255, 0), 1)
        cv2.putText(frame, f"High Risk: {high}", (w - 190, 75), 
                    self.font, 0.5, self.colors['HIGH'], 1)
        cv2.putText(frame, f"Critical: {critical}", (w - 190, 95), 
                    self.font, 0.5, self.colors['CRITICAL'], 1)
        
        # Flash warning if critical detected
        if critical > 0:
            cv2.rectangle(frame, (0, h - 40), (w, h), (0, 0, 200), -1)
            cv2.putText(frame, "⚠ CRITICAL RISK DETECTED ⚠", 
                        (w // 2 - 150, h - 12), self.font, 0.8, (255, 255, 255), 2)
