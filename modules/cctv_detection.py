"""
modules/cctv_detection.py - RTSP / IP-Camera stream detection
"""
import streamlit as st
import cv2
import time
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from utils.detection import run_inference, annotate_frame
from utils.helpers import save_snapshot
from modules.alert_system import maybe_send_alert
from database.db import start_session, end_session, save_accident, save_camera, get_cameras


def show_cctv_detection():
    user_id = st.session_state["user_id"]

    st.markdown("## 📡 CCTV / IP-Camera Monitoring")
    st.info(
        "Enter an RTSP stream URL (e.g. `rtsp://user:pass@192.168.1.100:554/stream`). "
        "The camera must be reachable from the server running this app."
    )

    with st.expander("➕ Add / Manage Camera Sources"):
        with st.form("add_camera"):
            cam_name  = st.text_input("Camera Name", placeholder="Main Gate CCTV")
            cam_url   = st.text_input("RTSP URL",    placeholder="rtsp://...")
            cam_loc   = st.text_input("Location",    placeholder="Building A, Floor 1")
            if st.form_submit_button("💾 Save Camera"):
                if cam_name and cam_url:
                    save_camera(user_id, cam_name, cam_url, cam_loc)
                    st.success(f"Camera '{cam_name}' saved.")
                else:
                    st.error("Name and URL are required.")

        saved = get_cameras(user_id)
        if saved:
            import pandas as pd
            st.dataframe(pd.DataFrame(saved)[["id","name","url","location"]], use_container_width=True, hide_index=True)

    st.markdown("---")
    stream_url  = st.text_input("🔗 Stream URL to monitor now", placeholder="rtsp://...")
    cam_label   = st.text_input("Camera Label", value="CCTV Stream")
    frame_limit = st.number_input("Max frames to process (0 = unlimited)", min_value=0, value=300)

    if "cctv_running" not in st.session_state:
        st.session_state.cctv_running = False

    c1, c2 = st.columns(2)
    with c1:
        if st.button("▶️ Start Monitoring", disabled=st.session_state.cctv_running):
            if not stream_url:
                st.error("Please enter a stream URL.")
            else:
                st.session_state.cctv_running = True
                st.rerun()
    with c2:
        if st.button("⏹️ Stop Monitoring", disabled=not st.session_state.cctv_running):
            st.session_state.cctv_running = False
            st.rerun()

    if st.session_state.cctv_running and stream_url:
        stframe   = st.empty()
        info_text = st.empty()
        err_text  = st.empty()

        cap = cv2.VideoCapture(stream_url)
        cap.set(cv2.CAP_PROP_BUFFERSIZE, 2)

        if not cap.isOpened():
            st.error(f"❌ Cannot connect to: {stream_url}\n\nCheck the URL and network reachability.")
            st.session_state.cctv_running = False
            return

        session_id = start_session(user_id, cam_label, "cctv")
        frame_cnt  = acc_cnt = 0
        limit      = int(frame_limit) if frame_limit > 0 else float("inf")

        while st.session_state.cctv_running and frame_cnt < limit:
            ret, frame = cap.read()
            if not ret:
                # Try to reconnect once
                cap.release()
                time.sleep(2)
                cap = cv2.VideoCapture(stream_url)
                if not cap.isOpened():
                    err_text.error("Stream lost. Could not reconnect.")
                    break
                continue

            frame_cnt += 1
            if frame_cnt % 5 == 0:
                detections = run_inference(frame)
                frame = annotate_frame(frame, detections)
                if detections:
                    acc_cnt += len(detections)
                    for d in detections:
                        snap = save_snapshot(frame, "cctv")
                        rid  = save_accident(session_id, cam_label, "cctv",
                                             d["confidence"], d.get("severity","Unknown"),
                                             snap, d["class_name"], d["bbox"], user_id)
                        maybe_send_alert(rid, cam_label, "cctv",
                                         d["confidence"], d.get("severity","Unknown"), snap)

            stframe.image(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB), use_column_width=True)
            info_text.info(f"📡 Frames: {frame_cnt} | 🚨 Accidents: {acc_cnt}")
            time.sleep(0.04)

        cap.release()
        end_session(session_id, frame_cnt, acc_cnt)
        st.session_state.cctv_running = False
