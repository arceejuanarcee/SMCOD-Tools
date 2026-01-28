# ui_header.py
from pathlib import Path
import streamlit as st


def render_logo_header():
    """
    Universal header: LOGO ONLY.
    Everything else (titles/buttons/text) must be rendered BELOW.
    """
    ROOT = Path(__file__).parent

    # Accept either PNG or JPG without you changing code
    logo_png = ROOT / "graphics" / "PhilSA_v4-01.png"
    logo_jpg = ROOT / "graphics" / "PhilSA_v4-01.jpg"
    logo_jpeg = ROOT / "graphics" / "PhilSA_v4-01.jpeg"

    logo_path = None
    for p in [logo_png, logo_jpg, logo_jpeg]:
        if p.exists():
            logo_path = p
            break

    st.markdown(
        """
        <style>
        header[data-testid="stHeader"] {visibility:hidden;height:0;}
        .block-container {padding-top: 0.8rem; max-width: 1400px;}
        </style>
        """,
        unsafe_allow_html=True,
    )

    if logo_path:
        st.image(str(logo_path), width=170)

    st.divider()
