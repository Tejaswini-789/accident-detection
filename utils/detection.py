"""
utils/detection.py - Core YOLO inference wrapper
"""
import numpy as np
from pathlib import Path
from typing import List, Dict, Optional
import sys, os

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from config import (
    MODEL_PATH, FALLBACK_MODEL, CONF_THRESHOLD, IOU_THRESHOLD,
    ACCIDENT_CLASS_NAMES, VEHICLE_CLASSES,
)

_model = None
_model_type = None


def _load_model():
    global _model, _model_type
    if _model is not None:
        return _model, _model_type
    from ultralytics import YOLO
    if MODEL_PATH.exists():
        try:
            _model = YOLO(str(MODEL_PATH))
            _model_type = "custom"
            return _model, _model_type
        except Exception as e:
            print(f"[WARN] Custom model failed ({e}), falling back.")
    _model = YOLO(FALLBACK_MODEL)
    _model_type = "fallback"
    return _model, _model_type


def model_info() -> str:
    _, mt = _load_model()
    if mt == "custom":
        return "✅ Custom accident-detection model loaded."
    return (
        "⚠️ **Fallback mode**: YOLOv8 general model is active. "
        "Accident detection is inferred from vehicle proximity/overlap. "
        "For higher accuracy, place a trained `accident_detector.pt` in the `models/` folder."
    )


def _boxes_overlap(b1, b2, threshold=0.15) -> bool:
    x1 = max(b1[0], b2[0]); y1 = max(b1[1], b2[1])
    x2 = min(b1[2], b2[2]); y2 = min(b1[3], b2[3])
    inter = max(0, x2 - x1) * max(0, y2 - y1)
    if inter == 0:
        return False
    a1 = (b1[2]-b1[0]) * (b1[3]-b1[1])
    a2 = (b2[2]-b2[0]) * (b2[3]-b2[1])
    iou = inter / (a1 + a2 - inter + 1e-6)
    return iou >= threshold


def _infer_accident_from_vehicles(detections: list) -> Optional[Dict]:
    vehicles = [d for d in detections if d["class_id"] in VEHICLE_CLASSES]
    if len(vehicles) < 2:
        return None
    for i in range(len(vehicles)):
        for j in range(i + 1, len(vehicles)):
            if _boxes_overlap(vehicles[i]["bbox"], vehicles[j]["bbox"]):
                b1, b2 = vehicles[i]["bbox"], vehicles[j]["bbox"]
                merged = (
                    min(b1[0], b2[0]), min(b1[1], b2[1]),
                    max(b1[2], b2[2]), max(b1[3], b2[3]),
                )
                conf = round((vehicles[i]["confidence"] + vehicles[j]["confidence"]) / 2, 3)
                return {
                    "class_id": -1,
                    "class_name": "accident (inferred)",
                    "confidence": conf,
                    "bbox": merged,
                    "severity": "Unknown",
                }
    return None


def _severity_from_class(class_name: str) -> str:
    from config import SEVERITY_KEYWORDS
    cl = class_name.lower()
    for sev, kws in SEVERITY_KEYWORDS.items():
        if any(kw in cl for kw in kws):
            return sev.capitalize()
    return "Unknown"


def run_inference(frame: np.ndarray) -> List[Dict]:
    model, mt = _load_model()
    results = model(frame, conf=CONF_THRESHOLD, iou=IOU_THRESHOLD, verbose=False)
    detections = []
    for r in results:
        for box in r.boxes:
            cid  = int(box.cls[0])
            name = model.names[cid]
            conf = float(box.conf[0])
            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
            detections.append({
                "class_id":   cid,
                "class_name": name,
                "confidence": round(conf, 3),
                "bbox":       (x1, y1, x2, y2),
                "severity":   _severity_from_class(name),
            })
    if mt == "custom":
        return [d for d in detections if any(a in d["class_name"].lower() for a in ACCIDENT_CLASS_NAMES)]
    acc = _infer_accident_from_vehicles(detections)
    return [acc] if acc else []


def annotate_frame(frame: np.ndarray, detections: List[Dict]) -> np.ndarray:
    import cv2
    out = frame.copy()
    sev_colors = {
        "High":    (0, 0, 255),
        "Medium":  (0, 165, 255),
        "Low":     (0, 255, 0),
        "Unknown": (255, 0, 255),
    }
    for d in detections:
        x1, y1, x2, y2 = d["bbox"]
        sev   = d.get("severity", "Unknown")
        color = sev_colors.get(sev, (255, 0, 255))
        label = f"{d['class_name']} {d['confidence']:.2f}"
        if sev != "Unknown":
            label += f" [{sev}]"
        cv2.rectangle(out, (x1, y1), (x2, y2), color, 2)
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.55, 1)
        cv2.rectangle(out, (x1, y1 - th - 6), (x1 + tw + 4, y1), color, -1)
        cv2.putText(out, label, (x1 + 2, y1 - 4),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
    return out
