"""
Lane Detection Module
Classifies objects by their lane position (left, center, right)
"""

from config import LANE_LEFT_MAX, LANE_CENTER_MAX


class LaneDetector:
    def __init__(self, frame_width: int = None):
        """Initialize lane detector."""
        self.frame_width = frame_width
        self.left_boundary = None
        self.right_boundary = None
        self._update_boundaries()
    
    def set_frame_width(self, width: int):
        """Set frame width and update lane boundaries."""
        self.frame_width = width
        self._update_boundaries()
    
    def _update_boundaries(self):
        """Update lane boundary positions."""
        if self.frame_width:
            self.left_boundary = int(self.frame_width * LANE_LEFT_MAX)
            self.right_boundary = int(self.frame_width * LANE_CENTER_MAX)
    
    def get_lane(self, center_x: int) -> str:
        """
        Determine which lane an object is in based on its center x position.
        
        Args:
            center_x: X coordinate of object center
            
        Returns:
            'LEFT', 'CENTER', or 'RIGHT'
        """
        if self.frame_width is None:
            return 'UNKNOWN'
        
        if center_x < self.left_boundary:
            return 'LEFT'
        elif center_x < self.right_boundary:
            return 'CENTER'
        else:
            return 'RIGHT'
    
    def get_lane_boundaries(self) -> tuple:
        """Return lane boundary x positions for visualization."""
        return (self.left_boundary, self.right_boundary)
    
    def classify_objects(self, tracked_objects: dict) -> dict:
        """
        Add lane classification to all tracked objects.
        
        Args:
            tracked_objects: Dict from tracker with object info
            
        Returns:
            Same dict with 'lane' key added to each object
        """
        for obj_id, obj_info in tracked_objects.items():
            center_x = obj_info['center'][0]
            obj_info['lane'] = self.get_lane(center_x)
        
        return tracked_objects
