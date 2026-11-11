"""
modules/webcam_detection.py - Live webcam accident detection
"""
import streamlit as st
import cv2
import numpy as np
import time
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.detection import run_inference, annotate_frame
from utils.helpers import save_snapshot, frame_to_bytes
from modules.alert_system import maybe_send_alert
from database.db import start_session, end_session, save_accident


def show_webcam_detection():
    user_id = st.session_state["user_id"]

    st.markdown("## 📷 Live Webcam Detection")
    st.warning(
        "⚠️ **Cloud deployment note**: Webcam access requires the browser to grant camera "
        "permissions. If you are running on Streamlit Cloud, webcam capture is supported "
        "via `st.camera_input` (snapshot mode). Real-time streaming requires local deployment."
    )

    mode = st.radio(
        "Select webcam mode",
        ["📸 Snapshot Mode (works on cloud)", "🎥 Live Stream Mode (local only)"],
        horizontal=True,
    )

    if "📸 Snapshot" in mode:
        _snapshot_mode(user_id)
    else:
        _stream_mode(user_id)


def _snapshot_mode(user_id: int):
    """Use Streamlit's built-in camera_input for cloud-compatible webcam."""
    st.info("Click **Take Photo** below, then press **Analyse** to run detection.")

    img_data = st.camera_input("📷 Capture from webcam")

    if img_data:
        file_bytes = np.frombuffer(img_data.getvalue(), np.uint8)
        frame      = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if frame is None:
            st.error("Could not decode camera image.")
            return

        col1, col2 = st.columns(2)
        with col1:
            st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), caption="Captured Frame", use_column_width=True)

        if st.button("🔍 Analyse Frame", type="primary"):
            with st.spinner("Running YOLO inference…"):
                session_id = start_session(user_id, "Webcam Snapshot", "webcam")
                detections = run_inference(frame)
                annotated  = annotate_frame(frame, detections)
                end_session(session_id, 1, len(detections))

            with col2:
                st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), caption="Detection Result", use_column_width=True)

            if detections:
                st.error(f"🚨 **{len(detections)} accident(s) detected!**")
                for d in detections:
                    snap = save_snapshot(annotated, "webcam")
                    record_id = save_accident(
                        session_id, "Webcam Snapshot", "webcam",
                        d["confidence"], d.get("severity","Unknown"),
                        snap, d["class_name"], d["bbox"], user_id,
                    )
                    maybe_send_alert(record_id, "Webcam Snapshot", "webcam",
                                     d["confidence"], d.get("severity","Unknown"), snap)
                    st.metric(f"Class", d["class_name"])
                    st.metric("Confidence", f"{d['confidence']:.1%}")
            else:
                st.success("✅ No accident detected.")


def _stream_mode(user_id: int):
    """OpenCV-based live stream — only works on local deployments."""
    if "webcam_running" not in st.session_state:
        st.session_state.webcam_running = False

    col1, col2 = st.columns(2)
    with col1:
        if st.button("▶️ Start Webcam", disabled=st.session_state.webcam_running):
            st.session_state.webcam_running = True
            st.rerun()
    with col2:
        if st.button("⏹️ Stop Webcam", disabled=not st.session_state.webcam_running):
            st.session_state.webcam_running = False
            st.rerun()

    if st.session_state.webcam_running:
        stframe   = st.empty()
        info_text = st.empty()
        cap       = cv2.VideoCapture(0)

        if not cap.isOpened():
            st.error("❌ Cannot open webcam. Check camera permissions or use Snapshot Mode.")
            st.session_state.webcam_running = False
            return

        session_id = start_session(user_id, "Live Webcam", "webcam")
        frame_cnt  = 0
        acc_cnt    = 0

        while st.session_state.webcam_running:
            ret, frame = cap.read()
            if not ret:
                st.warning("Camera disconnected.")
                break

            frame_cnt += 1
            if frame_cnt % 3 == 0:
                detections = run_inference(frame)
                frame = annotate_frame(frame, detections)
                if detections:
                    acc_cnt += len(detections)
                    for d in detections:
                        snap = save_snapshot(frame, "webcam_live")
                        rid  = save_accident(session_id, "Live Webcam", "webcam",
                                             d["confidence"], d.get("severity","Unknown"),
                                             snap, d["class_name"], d["bbox"], user_id)
                        maybe_send_alert(rid, "Live Webcam", "webcam",
                                         d["confidence"], d.get("severity","Unknown"), snap)

            stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_column_width=True)
            info_text.info(f"🎬 Frames: {frame_cnt} | 🚨 Accidents: {acc_cnt}")
            time.sleep(0.03)

        cap.release()
        end_session(session_id, frame_cnt, acc_cnt)
