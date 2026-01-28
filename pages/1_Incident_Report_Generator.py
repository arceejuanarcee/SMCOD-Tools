# pages/1_Incident_Report_Generator.py
import sys
from pathlib import Path

import streamlit as st
import ms_graph

# --- Auth guard ---
token = ms_graph.get_access_token()
if not token:
    st.switch_page("app.py")
    st.stop()

# --- Top bar: Back to Home ---
top_l, top_r = st.columns([0.85, 0.15])
with top_l:
    if st.button("⬅ Back to Home"):
        st.switch_page("app.py")
with top_r:
    if st.button("Logout"):
        ms_graph.logout()

st.divider()

# --- Ensure repo root import path ---
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# --- Import the tool (executes on import) ---
import IR_gen  # noqa: F401
