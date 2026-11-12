"""
app.py - Main Streamlit application entry point
AI-Based Real-Time Road Accident Detection and Emergency Alert System
"""
import streamlit as st
import sys, os

# Ensure project root is always in path (critical for Streamlit Cloud)
_APP_ROOT = os.path.dirname(os.path.abspath(__file__))
if _APP_ROOT not in sys.path:
    sys.path.insert(0, _APP_ROOT)
os.chdir(_APP_ROOT)  # Set working directory to project root

# ── Page config (must be first Streamlit call) ─────────────────────────────
st.set_page_config(
    page_title="AccidentAI - Road Accident Detection",
    page_icon="🚨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
/* Dark theme override */
[data-testid="stAppViewContainer"] { background-color: #0d1117; }
[data-testid="stSidebar"]          { background-color: #161b22; }
.block-container                   { padding-top: 1.5rem; }

/* Sidebar nav buttons */
div[data-testid="stSidebar"] .stButton > button {
    width: 100%;
    text-align: left;
    background: transparent;
    color: #c9d1d9;
    border: none;
    padding: 10px 16px;
    border-radius: 8px;
    font-size: 0.95rem;
    transition: background 0.2s;
}
div[data-testid="stSidebar"] .stButton > button:hover {
    background: #21262d;
    color: #58a6ff;
}

/* Metric cards */
[data-testid="metric-container"] {
    background: #161b22;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 12px;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    color: #8b949e;
    font-weight: 600;
}
.stTabs [aria-selected="true"] {
    color: #e94560 !important;
    border-bottom-color: #e94560 !important;
}

/* Headings */
h1, h2, h3 { color: #f0f6fc; }
p, li, label { color: #c9d1d9; }

/* Upload area */
[data-testid="stFileUploader"] {
    border: 2px dashed #30363d !important;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# ── Initialise DB ─────────────────────────────────────────────────────────
from database.db import init_db
init_db()

# ── Session defaults ──────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ── Auth gate ─────────────────────────────────────────────────────────────
from modules.authentication import show_auth_page, logout

if not st.session_state.authenticated:
    show_auth_page()
    st.stop()

# ── Sidebar ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="text-align:center;padding:16px 0;">
      <div style="font-size:2.5rem;">🚨</div>
      <div style="font-size:1.1rem;font-weight:800;color:#e94560;">AccidentAI</div>
      <div style="font-size:0.75rem;color:#8b949e;">Road Accident Detection</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"👤 **{st.session_state.username}**")
    st.divider()

    NAV = {
        "Dashboard":        "📊 Dashboard",
        "Image Detection":  "🖼️ Image Detection",
        "Video Detection":  "🎬 Video Detection",
        "Live Webcam":      "📷 Live Webcam",
        "CCTV Monitoring":  "📡 CCTV Monitoring",
        "Accident History": "📋 Accident History",
        "Reports":          "📈 Reports",
        "Severity Info":    "⚠️ Severity Info",
        "Settings":         "⚙️ Settings",
    }

    for page_key, label in NAV.items():
        active = st.session_state.page == page_key
        if st.button(label, key=f"nav_{page_key}",
                     type="primary" if active else "secondary"):
            st.session_state.page = page_key
            st.rerun()

    st.divider()
    if st.button("🚪 Logout", key="nav_logout"):
        logout()

# ── Page router ───────────────────────────────────────────────────────────
page = st.session_state.page

if page == "Dashboard":
    from modules.dashboard        import show_dashboard;        show_dashboard()
elif page == "Image Detection":
    from modules.image_detection  import show_image_detection;  show_image_detection()
elif page == "Video Detection":
    from modules.video_detection  import show_video_detection;  show_video_detection()
elif page == "Live Webcam":
    from modules.webcam_detection import show_webcam_detection; show_webcam_detection()
elif page == "CCTV Monitoring":
    from modules.cctv_detection   import show_cctv_detection;   show_cctv_detection()
elif page == "Accident History":
    from modules.accident_history import show_accident_history; show_accident_history()
elif page == "Reports":
    from modules.reports          import show_reports;          show_reports()
elif page == "Severity Info":
    from modules.severity         import show_severity_info;    show_severity_info()
elif page == "Settings":
    from modules.settings         import show_settings;         show_settings()
