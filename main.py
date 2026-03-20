"""
Road Safety Detection System
Main entry point - processes video and detects road hazards with risk assessment
"""

import cv2
import argparse
import os
from detector import Detector
from tracker import CentroidTracker
from lane_detector import LaneDetector
from risk_assessor import RiskAssessor
from visualizer import Visualizer
from config import OUTPUT_FPS, DISPLAY_WINDOW, SAVE_OUTPUT


def process_video(video_path: str, output_path: str = None):
    """
    Process a video file for road safety detection.
    
    Args:
        video_path: Path to input video
        output_path: Path to save output video (optional)
    """
    # Initialize components
    print("Initializing Road Safety Detection System...")
    detector = Detector()
    tracker = CentroidTracker()
    lane_detector = LaneDetector()
    risk_assessor = RiskAssessor()
    visualizer = Visualizer()
    
    # Open video
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Error: Could not open video file: {video_path}")
        return
    
    # Get video properties
    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS)) or OUTPUT_FPS
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    
    print(f"Video: {frame_width}x{frame_height} @ {fps}fps, {total_frames} frames")
    
    # Configure components with frame dimensions
    lane_detector.set_frame_width(frame_width)
    risk_assessor.set_frame_height(frame_height)
    
    # Setup video writer
    writer = None
    if SAVE_OUTPUT:
        if output_path is None:
            base = os.path.splitext(video_path)[0]
            output_path = f"{base}_analyzed.mp4"
        
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        writer = cv2.VideoWriter(output_path, fourcc, fps, (frame_width, frame_height))
        print(f"Output will be saved to: {output_path}")
    
    # Process frames
    frame_count = 0
    print("\nProcessing video... (Press 'q' to quit)")
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        frame_count += 1
        
        # Step 1: Detect objects
        detections = detector.detect(frame)
        
        # Step 2: Track objects
        tracked_objects = tracker.update(detections)
        
        # Step 3: Classify lanes
        tracked_objects = lane_detector.classify_objects(tracked_objects)
        
        # Step 4: Assess risk
        tracked_objects = risk_assessor.assess_all(tracked_objects)
        
        # Step 5: Visualize
        lane_boundaries = lane_detector.get_lane_boundaries()
        annotated_frame = visualizer.draw_frame(frame, tracked_objects, lane_boundaries)
        
        # Progress indicator
        if frame_count % 30 == 0:
            progress = (frame_count / total_frames) * 100 if total_frames > 0 else 0
            print(f"  Frame {frame_count}/{total_frames} ({progress:.1f}%)")
        
        # Save frame
        if writer:
            writer.write(annotated_frame)
        
        # Display
        if DISPLAY_WINDOW:
            cv2.imshow('Road Safety Detection', annotated_frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                print("\nStopped by user.")
                break
    
    # Cleanup
    cap.release()
    if writer:
        writer.release()
    cv2.destroyAllWindows()
    
    print(f"\nProcessing complete! Analyzed {frame_count} frames.")
    if output_path and SAVE_OUTPUT:
        print(f"Output saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='Road Safety Detection System')
    parser.add_argument('--video', '-v', type=str, default='input.mp4',
                        help='Path to input video (default: input.mp4)')
    parser.add_argument('--output', '-o', type=str, default=None,
                        help='Path to output video (default: <input>_analyzed.mp4)')
    parser.add_argument('--no-display', action='store_true',
                        help='Disable display window')
    parser.add_argument('--no-save', action='store_true',
                        help='Disable saving output video')
    
    args = parser.parse_args()
    
    # Override config based on args
    import config
    if args.no_display:
        config.DISPLAY_WINDOW = False
    if args.no_save:
        config.SAVE_OUTPUT = False
    
    process_video(args.video, args.output)


if __name__ == "__main__":
    main()