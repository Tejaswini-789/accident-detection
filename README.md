# 🚨 AI-Based Real-Time Road Accident Detection and Emergency Alert System

> **B.Tech Final Year Project — Computer Science & Engineering**  
> Built with YOLOv8 · OpenCV · Streamlit · SQLite · PyTorch

[![Streamlit App](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app.streamlit.app)

---

## 📌 Project Overview

This system uses **deep learning (YOLOv8)** to automatically detect road accidents from:
- 📸 Uploaded images
- 🎬 Uploaded videos
- 📷 Live webcam feed
- 📡 CCTV / RTSP streams

When an accident is detected, the system:
- Records the event with timestamp and confidence score
- Saves a snapshot
- Sends an email alert (if configured)
- Logs everything to a SQLite database

---

## 🏗️ Project Architecture

```
accident_detection/
├── app.py                  ← Main Streamlit app (entry point)
├── config.py               ← All configuration constants
├── requirements.txt        ← Python dependencies
├── .streamlit/
│   └── config.toml         ← Streamlit theme & server settings
├── database/
│   ├── db.py               ← SQLite connection + queries
│   └── schema.py           ← Table definitions (DDL)
├── models/
│   └── accident_detector.pt  ← Place custom YOLO weights here
├── modules/
│   ├── authentication.py   ← Login / Register / Logout
│   ├── dashboard.py        ← Stats, charts, recent events
│   ├── image_detection.py  ← Image upload detection
│   ├── video_detection.py  ← Video frame-by-frame detection
│   ├── webcam_detection.py ← Webcam (snapshot + live stream)
│   ├── cctv_detection.py   ← RTSP CCTV stream monitoring
│   ├── severity.py         ← Severity info & classification docs
│   ├── alert_system.py     ← Email alert dispatcher
│   ├── accident_history.py ← Searchable accident records table
│   ├── reports.py          ← CSV + PDF report generation
│   └── settings.py         ← Configuration & account settings
└── utils/
    ├── detection.py        ← YOLO inference wrapper + annotator
    ├── helpers.py          ← Snapshots, frame encoding, badges
    ├── video_utils.py      ← Video I/O utilities
    └── email_utils.py      ← SMTP email sending
```

---

## ⚙️ Technology Stack

| Component | Technology |
|---|---|
| Object Detection | YOLOv8 (Ultralytics) |
| Deep Learning | PyTorch |
| Computer Vision | OpenCV |
| Web Framework | Streamlit |
| Database | SQLite |
| Visualisation | Plotly, Matplotlib |
| Email Alerts | Python `smtplib` (SMTP) |
| PDF Reports | fpdf2 |
| Auth | bcrypt |

---

## 🚀 Live Deployment (Streamlit Cloud)

### Step 1 — Push to GitHub

```bash
cd /home/rguktrkvalley/Downloads/Teju/accident_detection
git init
git add .
git commit -m "Initial commit: AI Road Accident Detection System"
# Create a repo on GitHub (https://github.com/new), then:
git remote add origin https://github.com/YOUR_USERNAME/accident-detection.git
git push -u origin main
```

### Step 2 — Deploy on Streamlit Cloud (FREE)

1. Go to **https://share.streamlit.io**
2. Sign in with GitHub
3. Click **"New app"**
4. Select your repository and set:
   - **Main file path:** `accident_detection/app.py`
   - **Python version:** 3.10
5. Click **Deploy**

Your app will be live at: `https://YOUR_USERNAME-accident-detection.streamlit.app`

### Step 3 — Configure Email Alerts (optional)

In Streamlit Cloud dashboard → **Secrets** tab, add:
```toml
ALERT_EMAIL_SENDER   = "your_gmail@gmail.com"
ALERT_EMAIL_PASSWORD = "your_16char_app_password"
ALERT_EMAIL_RECEIVER = "emergency@example.com"
```

---

## 💻 Local Installation

### Prerequisites
- Ubuntu 20.04+ or Windows WSL2
- Python 3.8+ (3.10 recommended)
- 4 GB RAM minimum

### Install

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/accident-detection.git
cd accident-detection/accident_detection

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate       # On Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. (Optional) Set email credentials
export ALERT_EMAIL_SENDER="your@gmail.com"
export ALERT_EMAIL_PASSWORD="app_password"
export ALERT_EMAIL_RECEIVER="receiver@email.com"

# 5. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## 🤖 Model Configuration

### Option A — Use the YOLOv8 Fallback (works immediately, no download needed)

If no custom model is placed in `models/`, the system automatically uses **YOLOv8n** (general model). It detects vehicles and infers an accident from overlapping vehicle bounding boxes.

> ⚠️ This is a heuristic, not a trained accident detector. Expect false positives and false negatives.

### Option B — Custom Accident Detection Model (recommended)

1. **Download a pre-trained accident model from Roboflow:**
   - Visit: https://universe.roboflow.com/search?q=road+accident+detection
   - Download YOLOv8 weights (`.pt` format)
   - Place at: `models/accident_detector.pt`

2. **Or train your own:**
```bash
# Install ultralytics
pip install ultralytics

# Train
yolo detect train \
  data=path/to/your/data.yaml \
  model=yolov8n.pt \
  epochs=100 \
  imgsz=640 \
  batch=16

# Copy best weights
cp runs/detect/train/weights/best.pt models/accident_detector.pt
```

**Data YAML example:**
```yaml
path: /path/to/dataset
train: images/train
val:   images/val
nc: 1
names: ['accident']
```

### Option C — Severity Classification Model

For severity (Low/Medium/High), train with 3 classes:
```yaml
nc: 3
names: ['accident_low', 'accident_medium', 'accident_high']
```

---

## 🗄️ Database Tables

| Table | Purpose |
|---|---|
| `users` | User accounts with hashed passwords |
| `detection_sessions` | Each detection run (image/video/webcam/cctv) |
| `accident_records` | Individual accident events with metadata |
| `notifications` | Email alert history (sent/failed) |
| `camera_sources` | Saved CCTV camera URLs |

---

## 📧 Email Alert Setup

1. Enable Gmail **2-Step Verification**: https://myaccount.google.com/security
2. Generate an **App Password**: https://myaccount.google.com/apppasswords
3. Set environment variables:
```bash
export ALERT_EMAIL_SENDER="yourgmail@gmail.com"
export ALERT_EMAIL_PASSWORD="xxxx xxxx xxxx xxxx"   # 16-char app password
export ALERT_EMAIL_RECEIVER="alerts@yourdomain.com"
```

---

## 📸 Screenshots

| Login | Dashboard | Detection |
|---|---|---|
| (Add screenshots here) | (Add screenshots here) | (Add screenshots here) |

---

## 🎓 Project Details

| Item | Details |
|---|---|
| Project Title | AI-Based Real-Time Road Accident Detection and Emergency Alert System Using Deep Learning |
| Academic Year | 2024–2025 |
| Branch | B.Tech CSE |
| Technology | YOLOv8 + Streamlit + SQLite |
| Deployment | Streamlit Community Cloud (live website) |

---

## 🙋 FAQ

**Q: Why does severity show "Unknown"?**  
A: Severity requires a model trained with severity-labelled classes. The fallback YOLOv8 model outputs general vehicle classes with no severity label. See Settings → Severity Info.

**Q: Can I use it without a webcam?**  
A: Yes! Image and video detection work without a camera. Webcam mode uses `st.camera_input` on cloud.

**Q: Does it work on CPU?**  
A: Yes. Frame skip (`FRAME_SKIP=3`) ensures reasonable speed on CPU-only systems.

**Q: How do I test without a real accident video?**  
A: Search Kaggle or YouTube for "road accident footage" (CC-licensed). Or use the vehicle overlap heuristic with any traffic video.

---

## 📄 License

This project is for academic and educational use only.

---

*Built with ❤️ using Python, YOLOv8, and Streamlit*
