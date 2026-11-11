"""
utils/helpers.py - Miscellaneous utility functions
"""
import cv2
import numpy as np
from datetime import datetime
from pathlib import Path
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import SNAPSHOTS_DIR


def save_snapshot(frame: np.ndarray, prefix: str = "accident") -> str:
    """Save a frame as a JPEG snapshot. Returns the file path string."""
    ts   = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    name = f"{prefix}_{ts}.jpg"
    path = SNAPSHOTS_DIR / name
    cv2.imwrite(str(path), frame)
    return str(path)


def frame_to_bytes(frame: np.ndarray) -> bytes:
    """Encode an OpenCV frame to JPEG bytes for Streamlit display."""
    _, buf = cv2.imencode(".jpg", frame)
    return buf.tobytes()


def resize_frame(frame: np.ndarray, max_width: int = 960) -> np.ndarray:
    h, w = frame.shape[:2]
    if w <= max_width:
        return frame
    scale = max_width / w
    return cv2.resize(frame, (max_width, int(h * scale)))


def format_timestamp(ts_str: str) -> str:
    try:
        dt = datetime.strptime(ts_str, "%Y-%m-%d %H:%M:%S")
        return dt.strftime("%d %b %Y, %I:%M %p")
    except Exception:
        return ts_str


def severity_badge(sev: str) -> str:
    colors = {"High": "🔴", "Medium": "🟠", "Low": "🟢", "Unknown": "⚪"}
    return f"{colors.get(sev, '⚪')} {sev}"
