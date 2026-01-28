# pages/1_Incident_Report_Generator.py
import streamlit as st
import ms_graph
import runpy
from pathlib import Path

# Never do login here.
# If not logged in, always go back to portal.
if not ms_graph.get_access_token():
    st.switch_page("app.py")
    st.stop()

ROOT = Path(__file__).resolve().parents[1]
runpy.run_path(str(ROOT / "IR_gen.py"), run_name="__main__")
