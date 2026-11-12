"""
utils/video_utils.py - Video file processing utilities
"""
import os
import numpy as np
from pathlib import Path
from typing import Generator, Tuple
import sys

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from config import FRAME_SKIP, OUTPUTS_DIR


def get_video_info(video_path: str) -> dict:
    import cv2
    cap = cv2.VideoCapture(video_path)
    info = {
        "fps":    cap.get(cv2.CAP_PROP_FPS) or 25,
        "width":  int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "total_frames": int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
    }
    cap.release()
    info["duration_s"] = info["total_frames"] / max(info["fps"], 1)
    return info


def frame_generator(video_path: str, skip: int = FRAME_SKIP) -> Generator[Tuple[int, np.ndarray], None, None]:
    import cv2
    cap = cv2.VideoCapture(video_path)
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx % skip == 0:
            yield idx, frame
        idx += 1
    cap.release()


def write_annotated_video(input_path, output_name, annotated_frames, fps, width, height) -> str:
    import cv2
    out_path = str(OUTPUTS_DIR / output_name)
    fourcc   = cv2.VideoWriter_fourcc(*"mp4v")
    writer   = cv2.VideoWriter(out_path, fourcc, fps, (width, height))
    cap = cv2.VideoCapture(input_path)
    idx = 0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        if idx in annotated_frames:
            writer.write(cv2.resize(annotated_frames[idx], (width, height)))
        else:
            writer.write(frame)
        idx += 1
    cap.release()
    writer.release()
    return out_path


def save_upload(uploaded_file, dest_dir: Path) -> str:
    dest = dest_dir / uploaded_file.name
    with open(str(dest), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(dest)
