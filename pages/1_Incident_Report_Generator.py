# pages/1_Incident_Report_Generator.py
import sys
from pathlib import Path
import traceback

import streamlit as st
import ms_graph
from ui_header import render_logo_header

# IMPORTANT: do NOT call st.set_page_config here (app.py already did)

token = ms_graph.get_access_token()
if not token:
    st.switch_page("app.py")
    st.stop()

render_logo_header()

# Everything BELOW logo
st.markdown("# Incident Report Generator")

b1, b2, _ = st.columns([1.2, 1.0, 6])
with b1:
    if st.button("⬅ Back to Home", use_container_width=True):
        st.switch_page("app.py")
with b2:
    if st.button("Logout", use_container_width=True):
        ms_graph.logout()

st.write("")

# Ensure repo root import path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# Prevent IR_gen from crashing due to set_page_config being called after UI
_original_set_page_config = st.set_page_config
try:
    st.set_page_config = lambda *args, **kwargs: None  # no-op during import

    # Import tool. If it fails, show FULL error here.
    try:
        import IR_gen  # noqa: F401
    except Exception:
        st.error("IR_gen failed to load. Here is the full traceback (for debugging):")
        st.code(traceback.format_exc())
finally:
    st.set_page_config = _original_set_page_config
