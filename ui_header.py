# ui_header.py
from pathlib import Path
import streamlit as st

def render_header(title: str | None = None, subtitle: str | None = None):
    """
    Universal header:
    - logo on the left
    - (optional) title/subtitle beside it
    - all content below
    """
    ROOT = Path(__file__).parent
    logo = ROOT / "graphics" / "PhilSA_v4-01.png"

    st.markdown(
        """
        <style>
        header[data-testid="stHeader"] {visibility:hidden;height:0;}
        .block-container {padding-top: 0.6rem; max-width: 1400px;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([1.2, 6])
    with c1:
        if logo.exists():
            st.image(str(logo), width=170)
    with c2:
        if title:
            st.markdown(f"# {title}")
        if subtitle:
            st.caption(subtitle)

    st.divider()
