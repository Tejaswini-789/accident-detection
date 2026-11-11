"""
modules/video_detection.py - Video upload & frame-by-frame detection
"""
import streamlit as st
import cv2
import numpy as np
import os, sys, tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import UPLOADS_DIR, OUTPUTS_DIR, FRAME_SKIP
from utils.detection import run_inference, annotate_frame
from utils.helpers import save_snapshot
from utils.video_utils import get_video_info, save_upload, write_annotated_video
from modules.alert_system import maybe_send_alert
from database.db import start_session, end_session, save_accident


def show_video_detection():
    user_id = st.session_state["user_id"]

    st.markdown("## 🎬 Video Accident Detection")
    st.info("Upload an MP4, AVI, or MOV video. Frames are sampled for efficiency on CPU.")

    uploaded = st.file_uploader("Choose a video", type=["mp4", "avi", "mov"])

    if uploaded:
        vid_path   = save_upload(uploaded, UPLOADS_DIR)
        info       = get_video_info(vid_path)
        total_f    = info["total_frames"]
        fps        = info["fps"]
        processed  = max(1, total_f // FRAME_SKIP)

        st.markdown(f"""
        **Video Info** — {info['width']}×{info['height']} px | 
        {fps:.1f} FPS | {total_f} frames | 
        ~{info['duration_s']:.1f} s | 
        Will sample **{processed}** frames
        """)

        if st.button("▶️ Start Detection", type="primary"):
            session_id    = start_session(user_id, uploaded.name, "video")
            progress_bar  = st.progress(0, text="Initialising…")
            status_text   = st.empty()
            accident_log  = []
            annotated_frames = {}
            snap_placeholder = st.empty()

            cap = cv2.VideoCapture(vid_path)
            frame_idx = 0
            accidents_found = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                if frame_idx % FRAME_SKIP == 0:
                    detections = run_inference(frame)
                    if detections:
                        ann = annotate_frame(frame, detections)
                        annotated_frames[frame_idx] = ann
                        accidents_found += len(detections)

                        for d in detections:
                            ts_s = round(frame_idx / max(fps, 1), 2)
                            snap = save_snapshot(ann, prefix="video_accident")
                            record_id = save_accident(
                                session_id, uploaded.name, "video",
                                d["confidence"], d.get("severity", "Unknown"),
                                snap, d["class_name"], d["bbox"], user_id,
                            )
                            maybe_send_alert(
                                record_id, uploaded.name, "video",
                                d["confidence"], d.get("severity","Unknown"), snap,
                            )
                            accident_log.append({
                                "Frame": frame_idx,
                                "Time (s)": ts_s,
                                "Class": d["class_name"],
                                "Conf": f"{d['confidence']:.1%}",
                                "Severity": d.get("severity","Unknown"),
                            })

                        # Show latest snapshot
                        snap_placeholder.image(
                            cv2.cvtColor(ann, cv2.COLOR_BGR2RGB),
                            caption=f"🚨 Accident at frame {frame_idx} | t={round(frame_idx/max(fps,1),1)}s",
                            use_column_width=True,
                        )

                prog = min(frame_idx / max(total_f, 1), 1.0)
                progress_bar.progress(prog, text=f"Frame {frame_idx}/{total_f}")
                status_text.text(f"🚨 Accidents found so far: {accidents_found}")
                frame_idx += 1

            cap.release()
            end_session(session_id, frame_idx, accidents_found)
            progress_bar.progress(1.0, text="✅ Processing complete!")

            # Accident timeline
            if accident_log:
                import pandas as pd
                st.error(f"⚠️ **{accidents_found} accident event(s) detected!**")
                st.markdown("### 📋 Accident Timeline")
                st.dataframe(pd.DataFrame(accident_log), use_container_width=True, hide_index=True)

                # Write output video
                out_name = f"annotated_{uploaded.name}"
                out_path = write_annotated_video(
                    vid_path, out_name, annotated_frames,
                    fps, info["width"], info["height"],
                )
                with open(out_path, "rb") as vf:
                    st.download_button(
                        "📥 Download Annotated Video",
                        data=vf.read(),
                        file_name=out_name,
                        mime="video/mp4",
                    )
            else:
                st.success("✅ No accidents detected in this video.")
