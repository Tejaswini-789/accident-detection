"""
utils/video_utils.py - Video file processing utilities
"""
import cv2
import os
import tempfile
import numpy as np
from pathlib import Path
from typing import Generator, Tuple
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import FRAME_SKIP, OUTPUTS_DIR


def get_video_info(video_path: str) -> dict:
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


def frame_generator(
    video_path: str, skip: int = FRAME_SKIP
) -> Generator[Tuple[int, np.ndarray], None, None]:
    """Yield (frame_index, frame) every `skip` frames."""
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


def write_annotated_video(
    input_path: str,
    output_name: str,
    annotated_frames: dict,   # {frame_idx: annotated_frame}
    fps: float,
    width: int,
    height: int,
) -> str:
    """
    Write an output video with annotated frames merged back in.
    Returns the output file path.
    """
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
    """Save a Streamlit UploadedFile to dest_dir and return its path."""
    dest = dest_dir / uploaded_file.name
    with open(str(dest), "wb") as f:
        f.write(uploaded_file.getbuffer())
    return str(dest)
