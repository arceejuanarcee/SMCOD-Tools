# pages/1_Incident_Report_Generator.py
import sys
from pathlib import Path

import streamlit as st
import ms_graph

# --- Auth guard: NEVER login here; always return to app.py ---
token = ms_graph.get_access_token()
if not token:
    st.switch_page("app.py")
    st.stop()

# --- Ensure repo root is importable (important in Streamlit Cloud) ---
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# --- Import the tool normally (do NOT runpy) ---
# IR_gen currently executes on import; that's fine.
import IR_gen  # noqa: F401
