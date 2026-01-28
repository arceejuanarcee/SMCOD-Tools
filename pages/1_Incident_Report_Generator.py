# pages/1_Incident_Report_Generator.py
import sys
from pathlib import Path

import streamlit as st
import ms_graph
from ui_header import render_header

token = ms_graph.get_access_token()
if not token:
    st.switch_page("app.py")
    st.stop()

render_header("Incident Report Generator")

# Back/Home row (below the logo/header)
b1, b2, b3 = st.columns([1, 1, 6])
with b1:
    if st.button("⬅ Back to Home"):
        st.switch_page("app.py")
with b2:
    if st.button("Logout"):
        ms_graph.logout()

# Ensure repo root import path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Import tool
import IR_gen  # noqa: F401
