"""
modules/severity.py - Severity classification documentation & UI helper
"""
import streamlit as st


def show_severity_info():
    """Explain severity classification to the user."""
    st.markdown("## ⚠️ Accident Severity Classification")

    st.info("""
    **How Severity Works in This System**

    Severity is classified only when the loaded model explicitly outputs a severity-labelled class name:
    - `accident_high` → **High** severity
    - `accident_medium` → **Medium** severity
    - `accident_low` → **Low** severity

    If the model outputs a generic `accident` class (or the fallback vehicle-overlap heuristic is used),
    severity is marked as **Unknown** — the system will **not** invent a severity label from confidence scores.
    """)

    st.markdown("""
    ### How to Get Severity Classification

    **Option A — Use a Pre-trained Severity Model**
    - Search Roboflow Universe or Kaggle for datasets labelled with accident severity (e.g., 
      [RTA Dataset](https://universe.roboflow.com)).
    - Download weights fine-tuned on a 3-class severity dataset and place them in `models/accident_detector.pt`.

    **Option B — Train Your Own Model**
    1. Collect accident images.
    2. Annotate with 3 classes: `accident_low`, `accident_medium`, `accident_high`.
    3. Train with YOLOv8:
    ```bash
    yolo detect train data=your_data.yaml model=yolov8n.pt epochs=100 imgsz=640
    ```
    4. Copy `runs/detect/train/weights/best.pt` → `models/accident_detector.pt`.
    """)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div style="background:#2c0a0a;border-left:4px solid #e74c3c;padding:16px;border-radius:8px;">
        <h3 style="color:#e74c3c;">🔴 High</h3>
        <p style="color:#eee;">Multi-vehicle collision, rollover, or fire involved. Immediate emergency services required.</p>
        </div>""", unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div style="background:#2c1a0a;border-left:4px solid #e67e22;padding:16px;border-radius:8px;">
        <h3 style="color:#e67e22;">🟠 Medium</h3>
        <p style="color:#eee;">Minor collision with vehicle damage. Medical attention may be needed.</p>
        </div>""", unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div style="background:#0a2c0a;border-left:4px solid #2ecc71;padding:16px;border-radius:8px;">
        <h3 style="color:#2ecc71;">🟢 Low</h3>
        <p style="color:#eee;">Fender bender or minor incident. No serious injuries expected.</p>
        </div>""", unsafe_allow_html=True)
