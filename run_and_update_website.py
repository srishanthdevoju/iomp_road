"""
One-click script: Analyze video + Update website + Open browser
Usage: python run_and_update_website.py
       python run_and_update_website.py --video myvideo.mp4
"""
import cv2
import os
import sys
import subprocess
import webbrowser

def get_video_path():
    """Get video path from command line or use default."""
    for i, arg in enumerate(sys.argv):
        if arg in ('--video', '-v') and i + 1 < len(sys.argv):
            return sys.argv[i + 1]
    return 'input.mp4'

def run_analysis(video_path):
    """Step 1: Run main.py to analyze the video."""
    print("=" * 60)
    print("STEP 1: Running road safety analysis...")
    print("=" * 60)
    result = subprocess.run(
        [sys.executable, 'main.py', '--video', video_path, '--no-display'],
        cwd=os.path.dirname(os.path.abspath(__file__))
    )
    if result.returncode != 0:
        print("ERROR: Analysis failed!")
        sys.exit(1)

def reencode_for_website(video_path):
    """Step 2: Re-encode analyzed video to H.264 for browser playback."""
    print("\n" + "=" * 60)
    print("STEP 2: Re-encoding video for website...")
    print("=" * 60)

    base = os.path.splitext(video_path)[0]
    analyzed_path = f"{base}_analyzed.mp4"
    output_path = os.path.join("website", "input_analyzed_h264.mp4")

    if not os.path.exists(analyzed_path):
        print(f"ERROR: Analyzed video not found: {analyzed_path}")
        sys.exit(1)

    os.makedirs("website", exist_ok=True)

    # Get properties from analyzed video
    cap_analyzed = cv2.VideoCapture(analyzed_path)
    analyzed_frames = int(cap_analyzed.get(cv2.CAP_PROP_FRAME_COUNT))
    w = int(cap_analyzed.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap_analyzed.get(cv2.CAP_PROP_FRAME_HEIGHT))
    cap_analyzed.release()

    # Get original video duration to calculate correct FPS
    cap_input = cv2.VideoCapture(video_path)
    input_frames = int(cap_input.get(cv2.CAP_PROP_FRAME_COUNT))
    input_fps = cap_input.get(cv2.CAP_PROP_FPS)
    input_duration = input_frames / input_fps if input_fps > 0 else 60
    cap_input.release()

    # Calculate correct FPS so duration matches original
    correct_fps = analyzed_frames / input_duration if input_duration > 0 else 16
    correct_fps = max(1, min(correct_fps, 60))  # Clamp to reasonable range

    print(f"  Analyzed video: {analyzed_frames} frames, {w}x{h}")
    print(f"  Original duration: {input_duration:.1f}s")
    print(f"  Using FPS: {correct_fps:.1f}")

    # Re-encode to H.264
    cap = cv2.VideoCapture(analyzed_path)
    fourcc = cv2.VideoWriter_fourcc(*'avc1')
    writer = cv2.VideoWriter(output_path, fourcc, correct_fps, (w, h))

    if not writer.isOpened():
        # Fallback codec
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
        output_path = os.path.join("website", "input_analyzed_h264.avi")
        writer = cv2.VideoWriter(output_path, fourcc, correct_fps, (w, h))

    count = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        writer.write(frame)
        count += 1
        if count % 200 == 0:
            print(f"  {count}/{analyzed_frames} frames...")

    cap.release()
    writer.release()

    duration = count / correct_fps
    size_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  Done! {count} frames → {duration:.1f}s ({size_mb:.1f} MB)")
    print(f"  Saved to: {output_path}")

def open_website():
    """Step 3: Open the website in default browser."""
    print("\n" + "=" * 60)
    print("STEP 3: Opening website...")
    print("=" * 60)
    html_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "website", "index.html")
    webbrowser.open(f"file:///{html_path}")
    print(f"  Opened: {html_path}")

if __name__ == "__main__":
    video_path = get_video_path()
    print(f"\n🚗 ROAD - Website Updater")
    print(f"   Input video: {video_path}\n")

    run_analysis(video_path)
    reencode_for_website(video_path)
    open_website()

    print("\n✅ All done! Your website is ready with the new video.\n")
