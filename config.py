"""
config.py - Central configuration for Accident Detection System
"""
import os
from pathlib import Path

# ─── Base Paths ───────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
MODELS_DIR    = BASE_DIR / "models"
UPLOADS_DIR   = BASE_DIR / "uploads"
OUTPUTS_DIR   = BASE_DIR / "outputs"
SNAPSHOTS_DIR = BASE_DIR / "snapshots"
ASSETS_DIR    = BASE_DIR / "assets"
DATABASE_DIR  = BASE_DIR / "database"

# Create dirs if missing
for d in [MODELS_DIR, UPLOADS_DIR, OUTPUTS_DIR, SNAPSHOTS_DIR, ASSETS_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── Database ─────────────────────────────────────────────────────────────────
DB_PATH = DATABASE_DIR / "accident_detection.db"

# ─── Model ────────────────────────────────────────────────────────────────────
# Primary: custom accident-detection weights (place in models/ folder)
# Fallback: YOLOv8n general weights (detects vehicles; accident confirmed by logic)
MODEL_PATH = MODELS_DIR / "accident_detector.pt"
FALLBACK_MODEL = "yolov8n.pt"          # auto-downloaded from ultralytics on first run

# Classes in the custom model (update if you use a different model)
ACCIDENT_CLASS_NAMES = ["accident"]    # used only when custom model is loaded

# Vehicle classes in the YOLOv8 COCO fallback model
VEHICLE_CLASSES = [2, 3, 5, 7]        # car, motorcycle, bus, truck

# ─── Detection ────────────────────────────────────────────────────────────────
CONF_THRESHOLD    = 0.45   # minimum confidence to accept a detection
IOU_THRESHOLD     = 0.45   # NMS IoU threshold
FRAME_SKIP        = 3      # process every Nth frame for video (CPU optimisation)
ALERT_COOLDOWN_S  = 60     # seconds between repeated alerts for the same camera

# ─── Severity ─────────────────────────────────────────────────────────────────
# Severity is ONLY inferred when a custom model returns a class name that
# includes severity (e.g. "accident_high"). Otherwise it is marked "Unknown".
SEVERITY_KEYWORDS = {
    "high":   ["high", "major", "severe", "fatal"],
    "medium": ["medium", "moderate", "minor"],
    "low":    ["low", "slight", "small"],
}

# ─── Email / Alert ────────────────────────────────────────────────────────────
EMAIL_SENDER   = os.getenv("ALERT_EMAIL_SENDER", "")
EMAIL_PASSWORD = os.getenv("ALERT_EMAIL_PASSWORD", "")
EMAIL_RECEIVER = os.getenv("ALERT_EMAIL_RECEIVER", "")
SMTP_HOST      = "smtp.gmail.com"
SMTP_PORT      = 587

# ─── App ──────────────────────────────────────────────────────────────────────
APP_TITLE   = "AI Road Accident Detection System"
APP_VERSION = "1.0.0"
APP_ICON    = "🚨"
