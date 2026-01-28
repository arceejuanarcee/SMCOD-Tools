# pages/1_Incident_Report_Generator.py
import sys
from pathlib import Path

import streamlit as st
import ms_graph
from ui_header import render_header

# --- Auth guard ---
token = ms_graph.get_access_token()
if not token:
    st.switch_page("app.py")
    st.stop()

# --- Universal header (logo on top; everything below it) ---
render_header("Incident Report Generator")

# --- Buttons BELOW the header ---
b1, b2, _ = st.columns([1.2, 1.0, 6])
with b1:
    if st.button("⬅ Back to Home", use_container_width=True):
        st.switch_page("app.py")
with b2:
    if st.button("Logout", use_container_width=True):
        ms_graph.logout()

st.write("")  # spacing

# --- Ensure repo root import path ---
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# -------------------------------------------------------------------
# CRITICAL FIX:
# IR_gen.py calls st.set_page_config() at import-time.
# But we already rendered UI (header), so Streamlit would crash.
# We temporarily override set_page_config to a no-op during import.
# -------------------------------------------------------------------
_original_set_page_config = st.set_page_config
try:
    st.set_page_config = lambda *args, **kwargs: None  # no-op
    import IR_gen  # noqa: F401
finally:
    st.set_page_config = _original_set_page_config
