"""
modules/dashboard.py - Main dashboard with statistics and charts
"""
import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import sys, os

_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _root not in sys.path:
    sys.path.insert(0, _root)

from database.db import get_session_stats, get_severity_counts, get_daily_counts, get_accidents
from utils.helpers import format_timestamp, severity_badge
from utils.detection import model_info


def metric_card(label: str, value, icon: str = "📊", color: str = "#e94560"):
    st.markdown(f"""
    <div style="background:#1e2a3a;border-radius:12px;padding:20px;text-align:center;
                border-left:4px solid {color};margin-bottom:10px;">
      <div style="font-size:2rem;">{icon}</div>
      <div style="font-size:1.8rem;font-weight:800;color:{color};">{value}</div>
      <div style="color:#aaa;font-size:0.85rem;">{label}</div>
    </div>""", unsafe_allow_html=True)


def show_dashboard():
    user_id = st.session_state["user_id"]

    st.markdown("## 📊 Dashboard")

    # Model status
    info = model_info()
    if "✅" in info:
        st.success(info)
    else:
        st.warning(info)

    # Stats
    stats    = get_session_stats(user_id)
    sev_cnts = get_severity_counts(user_id)
    total_sessions  = stats.get("total_sessions") or 0
    total_accidents = stats.get("total_accidents") or 0

    c1, c2, c3, c4 = st.columns(4)
    with c1: metric_card("Total Sessions",         total_sessions,  "🎬", "#3498db")
    with c2: metric_card("Accidents Detected",     total_accidents, "🚗", "#e94560")
    with c3: metric_card("High Severity",          sev_cnts.get("High", 0),   "🔴", "#e74c3c")
    with c4: metric_card("Medium Severity",        sev_cnts.get("Medium", 0), "🟠", "#e67e22")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    # Severity pie chart
    with col_left:
        st.markdown("### 🥧 Accidents by Severity")
        if sev_cnts:
            fig = go.Figure(go.Pie(
                labels=list(sev_cnts.keys()),
                values=list(sev_cnts.values()),
                hole=0.4,
                marker=dict(colors=["#e74c3c", "#e67e22", "#2ecc71", "#9b59b6"]),
            ))
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#eee"),
                margin=dict(t=20, b=20),
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No accident data yet. Run a detection to populate stats.")

    # Daily accidents bar chart
    with col_right:
        st.markdown("### 📅 Daily Accident Trend (30 days)")
        daily = get_daily_counts(user_id, days=30)
        if daily:
            df = pd.DataFrame(daily)
            fig2 = px.bar(df, x="day", y="cnt", color_discrete_sequence=["#e94560"])
            fig2.update_layout(
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                font=dict(color="#eee"),
                xaxis_title="Date", yaxis_title="Accidents",
                margin=dict(t=20, b=20),
            )
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.info("No daily data yet.")

    # Recent accidents table
    st.markdown("### 🕒 Recent Accident Events")
    records = get_accidents(user_id, limit=10)
    if records:
        df_rec = pd.DataFrame(records)[["id","source_name","source_type","timestamp","confidence","severity","notified"]]
        df_rec["timestamp"] = df_rec["timestamp"].apply(format_timestamp)
        df_rec["confidence"] = df_rec["confidence"].apply(lambda x: f"{x:.1%}")
        df_rec["severity"]   = df_rec["severity"].apply(severity_badge)
        df_rec["notified"]   = df_rec["notified"].apply(lambda x: "✅" if x else "❌")
        df_rec.columns = ["ID","Source","Type","Time","Confidence","Severity","Alerted"]
        st.dataframe(df_rec, use_container_width=True, hide_index=True)
    else:
        st.info("No accidents recorded yet.")
