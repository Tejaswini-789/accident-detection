"""
modules/reports.py - Report generation (CSV + PDF)
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import io
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from database.db import get_accidents, get_severity_counts, get_daily_counts


def show_reports():
    user_id = st.session_state["user_id"]

    st.markdown("## 📊 Reports & Analytics")

    period = st.selectbox("Report Period", ["Last 7 Days", "Last 30 Days", "Last 90 Days", "All Time"])
    days_map = {"Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90, "All Time": 36500}
    days = days_map[period]

    records = get_accidents(user_id, limit=5000)
    if not records:
        st.info("No accident data found.")
        return

    df = pd.DataFrame(records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    if days < 36500:
        cutoff = pd.Timestamp.now() - pd.Timedelta(days=days)
        df     = df[df["timestamp"] >= cutoff]

    if df.empty:
        st.info(f"No data for {period}.")
        return

    # ── Summary Stats ─────────────────────────────────────────────────────────
    total  = len(df)
    high   = (df["severity"] == "High").sum()
    medium = (df["severity"] == "Medium").sum()
    low    = (df["severity"] == "Low").sum()
    alerted= df["notified"].sum()

    c1, c2, c3, c4, c5 = st.columns(5)
    c1.metric("Total Accidents", total)
    c2.metric("High Severity",   int(high))
    c3.metric("Medium Severity", int(medium))
    c4.metric("Low Severity",    int(low))
    c5.metric("Alerts Sent",     int(alerted))

    st.markdown("---")

    col_l, col_r = st.columns(2)

    # Severity distribution
    with col_l:
        st.markdown("### Severity Distribution")
        sev_df = df["severity"].value_counts().reset_index()
        sev_df.columns = ["Severity", "Count"]
        fig1 = px.pie(sev_df, names="Severity", values="Count",
                      color_discrete_sequence=["#e74c3c","#e67e22","#2ecc71","#9b59b6"])
        fig1.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#eee"))
        st.plotly_chart(fig1, use_container_width=True)

    # Source type breakdown
    with col_r:
        st.markdown("### Accidents by Source Type")
        src_df = df["source_type"].value_counts().reset_index()
        src_df.columns = ["Source", "Count"]
        fig2 = px.bar(src_df, x="Source", y="Count", color="Source",
                      color_discrete_sequence=["#3498db","#e94560","#2ecc71","#9b59b6"])
        fig2.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#eee"))
        st.plotly_chart(fig2, use_container_width=True)

    # Daily trend
    st.markdown("### 📅 Daily Accident Trend")
    df["date"] = df["timestamp"].dt.date
    daily = df.groupby("date").size().reset_index(name="count")
    fig3 = px.line(daily, x="date", y="count", markers=True,
                   color_discrete_sequence=["#e94560"])
    fig3.update_layout(paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#eee"),
                       xaxis_title="Date", yaxis_title="Accidents")
    st.plotly_chart(fig3, use_container_width=True)

    # ── Exports ───────────────────────────────────────────────────────────────
    st.markdown("### 📥 Export Report")
    col_csv, col_pdf = st.columns(2)

    with col_csv:
        csv_data = df.to_csv(index=False)
        st.download_button(
            "📄 Download CSV Report",
            data=csv_data,
            file_name=f"accident_report_{period.replace(' ','_')}.csv",
            mime="text/csv",
        )

    with col_pdf:
        pdf_bytes = _generate_pdf(df, period, total, int(high), int(medium), int(low))
        st.download_button(
            "📑 Download PDF Report",
            data=pdf_bytes,
            file_name=f"accident_report_{period.replace(' ','_')}.pdf",
            mime="application/pdf",
        )


def _generate_pdf(df: pd.DataFrame, period: str, total: int,
                  high: int, medium: int, low: int) -> bytes:
    try:
        from fpdf import FPDF
        from datetime import datetime

        pdf = FPDF()
        pdf.add_page()

        # Title
        pdf.set_font("Helvetica", "B", 20)
        pdf.set_text_color(233, 69, 96)
        pdf.cell(0, 12, "AI Road Accident Detection Report", ln=True, align="C")

        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 8, f"Period: {period}  |  Generated: {datetime.now().strftime('%d %b %Y %H:%M')}", ln=True, align="C")
        pdf.ln(6)

        # Summary
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(0, 10, "Summary Statistics", ln=True)
        pdf.set_font("Helvetica", "", 11)
        for label, val in [
            ("Total Accidents", total),
            ("High Severity", high),
            ("Medium Severity", medium),
            ("Low Severity", low),
            ("Alerts Sent", int(df["notified"].sum())),
        ]:
            pdf.cell(80, 8, label + ":", ln=False)
            pdf.cell(0,  8, str(val), ln=True)
        pdf.ln(4)

        # Recent records table
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 10, "Recent Accident Records (up to 50)", ln=True)
        pdf.set_font("Helvetica", "B", 9)
        headers = ["ID", "Source", "Type", "Timestamp", "Confidence", "Severity"]
        widths  = [12,   50,      22,     45,          25,            25]
        for h, w in zip(headers, widths):
            pdf.cell(w, 7, h, border=1)
        pdf.ln()

        pdf.set_font("Helvetica", "", 8)
        for _, row in df.head(50).iterrows():
            vals = [
                str(row["id"]),
                str(row["source_name"])[:25],
                str(row["source_type"]),
                str(row["timestamp"])[:19],
                f"{row['confidence']:.1%}",
                str(row["severity"]),
            ]
            for v, w in zip(vals, widths):
                pdf.cell(w, 6, v, border=1)
            pdf.ln()

        return pdf.output(dest="S").encode("latin-1")

    except ImportError:
        # fpdf2 not installed — return a plain-text PDF substitute
        txt = f"Accident Report — {period}\n\nTotal: {total}\nHigh: {high}\nMedium: {medium}\nLow: {low}"
        return txt.encode()
