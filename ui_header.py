# ui_header.py
import streamlit as st
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def render_logo_header():
    logo_path = ROOT / "graphics" / "PhilSA_v4-01.png"  # change to .jpg if needed

    col_logo, col_text = st.columns([1, 6], vertical_alignment="center")
    with col_logo:
        if logo_path.exists():
            st.image(str(logo_path), width=120)  # enlarge here
        else:
            st.write("")

    with col_text:
        # Do NOT put page titles here (prevents “Incident Report Generator beside logo” problem)
        st.write("")

    st.divider()
