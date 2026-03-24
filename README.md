# 🚗 ROAD — Real-time Object Analysis for Driving Safety

[![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python&logoColor=white)](https://python.org)
[![YOLOv8](https://img.shields.io/badge/YOLOv8-Ultralytics-purple?logo=ultralytics)](https://docs.ultralytics.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![OpenCV](https://img.shields.io/badge/OpenCV-4.8%2B-red?logo=opencv)](https://opencv.org)

An intelligent, vision-only road safety detection system that processes dashcam footage in real time using **YOLOv8** deep learning, **centroid-based tracking**, **lane classification**, and a **weighted risk-assessment algorithm** — no LiDAR or radar required.

---

## ✨ Features

| Capability | How it Works |
|---|---|
| **Object Detection** | YOLOv8 nano (COCO-trained, filtered to 6 road-relevant classes) |
| **Motion Tracking** | Centroid tracker with bounding-box area-change analysis |
| **Lane Classification** | Zone-based frame division (Left 35 % · Center 30 % · Right 35 %) |
| **Risk Assessment** | Weighted multi-factor scoring — Distance 35 %, Motion 30 %, Lane 20 %, Object type 15 % |
| **Visualization** | Color-coded bounding boxes, motion labels, lane lines, real-time dashboard |
| **Web Viewer** | Standalone HTML/CSS/JS website to view the analyzed video with pipeline details |

### Risk Levels

| Level | Score | Color | Suggested Action |
|---|---|---|---|
| LOW | 0 – 25 % | 🟢 Green | Normal driving |
| MEDIUM | 25 – 50 % | 🟡 Yellow | Monitor closely |
| HIGH | 50 – 75 % | 🟠 Orange | Prepare to brake |
| CRITICAL | 75 – 100 % | 🔴 Red | Immediate hazard warning |

---

## 📂 Project Structure

```
road_project/
├── main.py                # Pipeline orchestrator & CLI entry point
├── detector.py            # YOLOv8 object detection
├── tracker.py             # Centroid tracking & motion analysis
├── lane_detector.py       # Lane position classification
├── risk_assessor.py       # Weighted risk scoring
├── visualizer.py          # Annotation & rendering
├── config.py              # All tunable parameters
├── run_and_update_website.py  # Analyse video → re-encode → launch website
├── requirements.txt       # Python dependencies
├── yolov8n.pt             # YOLOv8 nano weights (auto-downloaded)
├── input.mp4              # Your dashcam footage (user-provided)
│── index.html         # Web viewer
│── styles.css         # Styling
│── script.js          # Interactivity
│── input_analyzed_h264.mp4  # H.264 web-compatible output
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🚀 Quick Start

### Prerequisites

- **Python 3.9+**
- **pip 21+**
- (Optional) NVIDIA GPU + CUDA for real-time performance

### Installation

```bash
# 1. Clone the repository
git clone https://github.com/<your-username>/road_project.git
cd road_project

# 2. Create a virtual environment (recommended)
python -m venv venv
source venv/bin/activate   # Linux / macOS
venv\Scripts\activate      # Windows

# 3. Install dependencies
pip install -r requirements.txt
```

### Running the Analysis

```bash
# Default – processes input.mp4
python main.py

# Custom input / output
python main.py --video path/to/dashcam.mp4 --output result.mp4

# Headless mode (no display window)
python main.py --no-display

# Skip saving annotated video
python main.py --no-save
```

### Launching the Website

```bash
# Analyses video, re-encodes for web, and opens the website
python run_and_update_website.py
```

---

## ⚙️ Configuration

All parameters live in **`config.py`** — no need to touch core modules:

| Parameter | Default | Description |
|---|---|---|
| `YOLO_MODEL` | `yolov8n.pt` | Model variant (nano/small/medium/large) |
| `CONFIDENCE_THRESHOLD` | `0.5` | Minimum detection confidence |
| `LANE_LEFT_MAX` | `0.35` | Left-lane boundary (fraction of frame width) |
| `RISK_WEIGHTS` | distance 0.35, motion 0.30, lane 0.20, obj 0.15 | Factor weights for risk scoring |
| `OUTPUT_FPS` | `30` | Frames per second for output video |

---

## 🏗️ System Architecture

```
Input Video ──▶ Frame Extraction ──▶ Object Detection (YOLOv8)
                                         │
                                         ▼
                                   Object Tracking (Centroid)
                                         │
                                         ▼
                                   Lane Classification (Zone-based)
                                         │
                                         ▼
                                   Risk Assessment (Weighted Scoring)
                                         │
                                         ▼
                                   Visualization & Output
                                     ┌────┴────┐
                                  Display    Video File
```

### Risk Scoring Formula

```
Risk = (0.35 × Distance) + (0.30 × Motion) + (0.20 × Lane) + (0.15 × ObjectType)
```

- **Distance** — vertical position in frame (lower = closer = riskier)
- **Motion** — Approaching 1.0 · Stationary 0.5 · Departing 0.1
- **Lane** — Center 1.0 · Side lanes 0.5
- **Object type** — Pedestrian 1.0 · Bicycle 0.8 · Motorcycle 0.7 · Bus/Truck 0.6 · Car 0.5

---

## 💻 System Requirements

| | Minimum | Recommended |
|---|---|---|
| **CPU** | Intel i5 8th Gen / Ryzen 5 | Intel i7 10th Gen+ / Ryzen 7 |
| **RAM** | 8 GB | 16 GB |
| **GPU** | Not required (CPU mode) | NVIDIA GTX 1650+ with CUDA |
| **Storage** | 2 GB free | 5 GB free |
| **OS** | Windows 10 / Ubuntu 18.04+ / macOS | — |

> **Note:** GPU + CUDA enables near-real-time speeds. CPU-only mode runs at ~3–5 FPS.

---

## 🔮 Future Enhancements

- Deep-learning lane detection (SCNN / LaneNet)
- DeepSORT tracking with appearance features
- Speed estimation via camera calibration
- Time-to-Collision (TTC) calculation
- Audio hazard alerts
- Real-time web dashboard (Flask / Streamlit)
- Multi-camera surround-view support

---

## 📚 References

1. Redmon, J. et al. (2016). *You Only Look Once: Unified, Real-Time Object Detection.* CVPR.
2. Ultralytics YOLOv8 — <https://docs.ultralytics.com>
3. Geiger, A. et al. (2012). *The KITTI Vision Benchmark Suite.* CVPR.
4. Yu, F. et al. (2020). *BDD100K: A Diverse Driving Dataset.* CVPR.
5. Bewley, A. et al. (2016). *Simple Online and Realtime Tracking.* ICIP.
6. Wojke, N. et al. (2017). *Deep Association Metric for Tracking.* ICIP.
7. Pan, X. et al. (2018). *Spatial CNN for Traffic Scene Understanding.* AAAI.
8. WHO (2023). *Global Status Report on Road Safety.*

---

## 📄 License

This project is licensed under the **MIT License** — see [LICENSE](LICENSE) for details.

---

<p align="center">
  <i>Developed as part of an Autonomous Driving Research Project</i>
</p>
