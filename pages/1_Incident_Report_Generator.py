# pages/1_Incident_Report_Generator.py
import streamlit as st
import ms_graph
from ui_header import render_logo_header

render_logo_header()

token = ms_graph.get_access_token()
if not token:
    st.warning("Session expired. Please sign in again.")
    st.switch_page("app.py")

# Back/Home/Logout row
c1, c2, c3 = st.columns([2, 2, 6])
with c1:
    if st.button("← Back to Home", use_container_width=True):
        st.switch_page("app.py")
with c2:
    if st.button("Logout", use_container_width=True):
        ms_graph.logout()

st.write("")

# Import AFTER auth so it won't crash/stop on import
import IR_gen  # noqa: E402
