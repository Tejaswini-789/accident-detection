"""
modules/accident_history.py - View, filter, and export accident records
"""
import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database.db import get_accidents
from utils.helpers import format_timestamp, severity_badge


def show_accident_history():
    user_id = st.session_state["user_id"]

    st.markdown("## 📋 Accident History")

    records = get_accidents(user_id, limit=1000)
    if not records:
        st.info("No accident records found. Run a detection to populate history.")
        return

    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])

    # ── Filters ──────────────────────────────────────────────────────────────
    with st.expander("🔍 Filter Records"):
        col1, col2, col3 = st.columns(3)
        with col1:
            severities = ["All"] + sorted(df["severity"].unique().tolist())
            sel_sev    = st.selectbox("Severity", severities)
        with col2:
            src_types  = ["All"] + sorted(df["source_type"].unique().tolist())
            sel_type   = st.selectbox("Source Type", src_types)
        with col3:
            date_range = st.date_input(
                "Date Range",
                value=(df["timestamp"].min().date(), df["timestamp"].max().date()),
            )

    # Apply filters
    mask = pd.Series([True] * len(df))
    if sel_sev  != "All": mask &= df["severity"]    == sel_sev
    if sel_type != "All": mask &= df["source_type"] == sel_type
    if isinstance(date_range, tuple) and len(date_range) == 2:
        d1, d2 = pd.Timestamp(date_range[0]), pd.Timestamp(date_range[1])
        mask &= (df["timestamp"] >= d1) & (df["timestamp"] <= d2 + pd.Timedelta(days=1))
    df_filtered = df[mask].copy()

    st.markdown(f"**Showing {len(df_filtered)} record(s)**")

    # Display columns
    display_cols = ["id","source_name","source_type","timestamp","confidence","severity","notified"]
    df_disp = df_filtered[display_cols].copy()
    df_disp["timestamp"]  = df_disp["timestamp"].dt.strftime("%d %b %Y %H:%M:%S")
    df_disp["confidence"] = df_disp["confidence"].apply(lambda x: f"{x:.1%}")
    df_disp["severity"]   = df_disp["severity"].apply(severity_badge)
    df_disp["notified"]   = df_disp["notified"].apply(lambda x: "✅" if x else "❌")
    df_disp.columns       = ["ID","Source","Type","Timestamp","Confidence","Severity","Alerted"]

    st.dataframe(df_disp, use_container_width=True, hide_index=True)

    # CSV export
    csv = df_filtered.to_csv(index=False)
    st.download_button(
        "📥 Export to CSV",
        data=csv,
        file_name="accident_history.csv",
        mime="text/csv",
    )

    # Snapshot viewer
    st.markdown("### 🖼️ Snapshot Viewer")
    snaps = df_filtered[df_filtered["snapshot_path"].notna()]["snapshot_path"].tolist()
    if snaps:
        sel_snap = st.selectbox("Select snapshot to view", snaps)
        if sel_snap and os.path.exists(sel_snap):
            st.image(sel_snap, caption=os.path.basename(sel_snap), use_column_width=True)
        else:
            st.caption("Snapshot file not found on disk.")
    else:
        st.caption("No snapshots saved for filtered records.")
