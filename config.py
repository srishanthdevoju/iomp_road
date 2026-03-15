"""
Configuration settings for Road Safety Detection System
"""

# YOLO model settings
YOLO_MODEL = "yolov8n.pt"  # Use nano model for speed, can upgrade to yolov8s/m/l

# Classes to detect (COCO dataset class IDs)
TARGET_CLASSES = {
    0: "person",
    1: "bicycle",
    2: "car",
    3: "motorcycle",
    5: "bus",
    7: "truck"
}

# Detection confidence threshold
CONFIDENCE_THRESHOLD = 0.5

# Lane zones (percentage of frame width)
LANE_LEFT_MAX = 0.35      # 0-35% = left lane
LANE_CENTER_MAX = 0.65    # 35-65% = center lane
# 65-100% = right lane

# Risk assessment weights
RISK_WEIGHTS = {
    "distance": 0.35,      # Closer = higher risk
    "motion": 0.30,        # Approaching = higher risk
    "lane": 0.20,          # Center/same lane = higher risk
    "object_type": 0.15    # Pedestrians = higher risk
}

# Risk thresholds
RISK_THRESHOLDS = {
    "low": 0.25,
    "medium": 0.50,
    "high": 0.75
    # Above 0.75 = critical
}

# Object type risk multipliers
OBJECT_RISK = {
    "person": 1.0,
    "bicycle": 0.8,
    "motorcycle": 0.7,
    "car": 0.5,
    "bus": 0.6,
    "truck": 0.6
}

# Tracking settings
MAX_DISAPPEARED_FRAMES = 30
MIN_VELOCITY_THRESHOLD = 2.0  # pixels per frame

# Visualization colors (BGR format)
COLORS = {
    "LOW": (0, 255, 0),       # Green
    "MEDIUM": (0, 255, 255),  # Yellow
    "HIGH": (0, 165, 255),    # Orange
    "CRITICAL": (0, 0, 255),  # Red
    "lane_line": (255, 255, 0) # Cyan
}

# Output settings
OUTPUT_FPS = 30
DISPLAY_WINDOW = True
SAVE_OUTPUT = True
