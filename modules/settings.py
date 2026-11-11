"""
modules/settings.py - App settings UI (email config, model info, account)
"""
import streamlit as st
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from config import MODEL_PATH, FALLBACK_MODEL
from utils.detection import model_info


def show_settings():
    user_id  = st.session_state["user_id"]
    username = st.session_state["username"]

    st.markdown("## ⚙️ Settings")

    # ── Account Info ──────────────────────────────────────────────────────────
    with st.expander("👤 Account Information", expanded=True):
        st.write(f"**Username:** {username}")
        st.write(f"**User ID:** {user_id}")
        st.caption("Password change is not implemented in this demo version.")

    # ── Model Info ────────────────────────────────────────────────────────────
    with st.expander("🤖 Model Configuration"):
        status = model_info()
        if "✅" in status:
            st.success(status)
        else:
            st.warning(status)

        st.markdown(f"""
        **Custom model path:** `{MODEL_PATH}`

        **To use a custom accident model:**
        1. Download or train a YOLOv8 accident detection model (`.pt` weights).
        2. Place it at: `models/accident_detector.pt`
        3. Restart the application.

        **Recommended sources:**
        - [Roboflow Universe – Road Accident datasets](https://universe.roboflow.com/search?q=road+accident)
        - [Kaggle – Accident Detection datasets](https://www.kaggle.com/search?q=accident+detection+yolo)
        """)

    # ── Email Alert Config ────────────────────────────────────────────────────
    with st.expander("📧 Emergency Email Alerts"):
        st.info("""
        Email credentials are read from **environment variables** for security.
        Set these before starting the app:
        ```bash
        export ALERT_EMAIL_SENDER="your_gmail@gmail.com"
        export ALERT_EMAIL_PASSWORD="your_app_password"
        export ALERT_EMAIL_RECEIVER="emergency@example.com"
        ```
        **For Gmail:** Enable 2FA and generate an [App Password](https://myaccount.google.com/apppasswords).
        """)

        sender   = os.getenv("ALERT_EMAIL_SENDER", "")
        receiver = os.getenv("ALERT_EMAIL_RECEIVER", "")

        if sender and receiver:
            st.success(f"✅ Alerts configured: {sender} → {receiver}")
        else:
            st.error("❌ Email not configured. Set environment variables to enable alerts.")

    # ── Detection Settings ─────────────────────────────────────────────────────
    with st.expander("🔧 Detection Parameters"):
        from config import CONF_THRESHOLD, FRAME_SKIP, ALERT_COOLDOWN_S
        st.markdown(f"""
        | Parameter | Value |
        |---|---|
        | Confidence Threshold | `{CONF_THRESHOLD}` |
        | Frame Skip (video) | Every `{FRAME_SKIP}` frames |
        | Alert Cooldown | `{ALERT_COOLDOWN_S}` seconds |

        To change these values, edit `config.py` and restart.
        """)

    # ── About ──────────────────────────────────────────────────────────────────
    with st.expander("ℹ️ About This System"):
        st.markdown("""
        **AI-Based Real-Time Road Accident Detection and Emergency Alert System**
        
        - **Version:** 1.0.0
        - **Model:** YOLOv8 (Ultralytics)
        - **Framework:** Streamlit + OpenCV + PyTorch
        - **Database:** SQLite
        - **Deployed on:** Streamlit Community Cloud
        
        *B.Tech Final Year Project — Computer Science & Engineering*
        """)
