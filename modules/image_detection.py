"""
modules/image_detection.py - Image upload & accident detection
"""
import streamlit as st
import numpy as np
import cv2
from PIL import Image
import io
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.detection import run_inference, annotate_frame
from utils.helpers import save_snapshot
from modules.alert_system import maybe_send_alert
from database.db import start_session, end_session, save_accident


def show_image_detection():
    user_id = st.session_state["user_id"]

    st.markdown("## 🖼️ Image Accident Detection")
    st.info("Upload a JPG / JPEG / PNG image to detect road accidents.")

    uploaded = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    if uploaded:
        # Decode image
        file_bytes = np.frombuffer(uploaded.read(), np.uint8)
        frame      = cv2.imdecode(file_bytes, cv2.IMREAD_COLOR)

        if frame is None:
            st.error("Could not read the image. Please try another file.")
            return

        col_orig, col_det = st.columns(2)
        with col_orig:
            st.markdown("**📷 Original Image**")
            st.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_column_width=True)

        with st.spinner("🔍 Running YOLO inference…"):
            session_id = start_session(user_id, uploaded.name, "image")
            detections = run_inference(frame)
            annotated  = annotate_frame(frame, detections)
            end_session(session_id, total_frames=1, accidents_found=len(detections))

        with col_det:
            st.markdown("**🚨 Detection Result**")
            st.image(cv2.cvtColor(annotated, cv2.COLOR_BGR2RGB), use_column_width=True)

        # Results
        if detections:
            st.error(f"⚠️ **{len(detections)} accident(s) detected!**")
            for i, d in enumerate(detections, 1):
                sev = d.get("severity", "Unknown")
                col_a, col_b, col_c = st.columns(3)
                col_a.metric(f"Detection #{i} Class", d["class_name"])
                col_b.metric("Confidence", f"{d['confidence']:.1%}")
                col_c.metric("Severity", sev if sev != "Unknown" else "N/A (see note)")

                snap = save_snapshot(annotated, prefix="image_accident")
                record_id = save_accident(
                    session_id, uploaded.name, "image",
                    d["confidence"], sev, snap, d["class_name"],
                    d["bbox"], user_id,
                )
                maybe_send_alert(record_id, uploaded.name, "image", d["confidence"], sev, snap)

            # Download annotated image
            _, buf = cv2.imencode(".jpg", annotated)
            st.download_button(
                "📥 Download Annotated Image",
                data=buf.tobytes(),
                file_name=f"annotated_{uploaded.name}",
                mime="image/jpeg",
            )
        else:
            st.success("✅ No accident detected in this image.")

        # Severity note
        if any(d.get("severity") == "Unknown" for d in detections):
            st.caption(
                "ℹ️ **Severity note**: Severity classification requires a custom-trained "
                "multi-class model. The current model does not output severity labels."
            )
