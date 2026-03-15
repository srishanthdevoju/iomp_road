"""
Risk Assessment Module
Calculates collision risk based on proximity, motion, lane, and object type
"""

from config import RISK_WEIGHTS, RISK_THRESHOLDS, OBJECT_RISK


class RiskAssessor:
    def __init__(self, frame_height: int = None):
        """Initialize risk assessor."""
        self.frame_height = frame_height
        self.weights = RISK_WEIGHTS
        self.thresholds = RISK_THRESHOLDS
        self.object_risk = OBJECT_RISK
    
    def set_frame_height(self, height: int):
        """Set frame height for distance calculations."""
        self.frame_height = height
    
    def calculate_risk(self, obj_info: dict) -> dict:
        """
        Calculate risk score for a detected object.
        
        Args:
            obj_info: Detection info with bbox, motion, lane, class_name
            
        Returns:
            Dict with 'score' (0-1), 'level' (LOW/MEDIUM/HIGH/CRITICAL),
            and 'factors' breakdown
        """
        factors = {}
        
        # 1. Distance risk (based on position in frame - lower = closer = higher risk)
        if self.frame_height:
            y_bottom = obj_info['bbox'][3]
            # Objects at bottom of frame are closer
            distance_score = y_bottom / self.frame_height
            factors['distance'] = distance_score
        else:
            factors['distance'] = 0.5
        
        # 2. Motion risk
        motion = obj_info.get('motion', 'UNKNOWN')
        if motion == 'APPROACHING':
            factors['motion'] = 1.0
        elif motion == 'STATIONARY':
            factors['motion'] = 0.5
        elif motion == 'DEPARTING':
            factors['motion'] = 0.1
        else:
            factors['motion'] = 0.3
        
        # 3. Lane risk (center lane = highest risk)
        lane = obj_info.get('lane', 'UNKNOWN')
        if lane == 'CENTER':
            factors['lane'] = 1.0
        elif lane == 'LEFT':
            factors['lane'] = 0.5
        elif lane == 'RIGHT':
            factors['lane'] = 0.5
        else:
            factors['lane'] = 0.3
        
        # 4. Object type risk
        class_name = obj_info.get('class_name', 'car')
        factors['object_type'] = self.object_risk.get(class_name, 0.5)
        
        # Calculate weighted score
        score = (
            factors['distance'] * self.weights['distance'] +
            factors['motion'] * self.weights['motion'] +
            factors['lane'] * self.weights['lane'] +
            factors['object_type'] * self.weights['object_type']
        )
        
        # Determine risk level
        if score < self.thresholds['low']:
            level = 'LOW'
        elif score < self.thresholds['medium']:
            level = 'MEDIUM'
        elif score < self.thresholds['high']:
            level = 'HIGH'
        else:
            level = 'CRITICAL'
        
        return {
            'score': round(score, 2),
            'level': level,
            'factors': factors
        }
    
    def assess_all(self, tracked_objects: dict) -> dict:
        """
        Calculate risk for all tracked objects.
        
        Args:
            tracked_objects: Dict from tracker/lane detector
            
        Returns:
            Same dict with 'risk' key added to each object
        """
        for obj_id, obj_info in tracked_objects.items():
            obj_info['risk'] = self.calculate_risk(obj_info)
        
        return tracked_objects
