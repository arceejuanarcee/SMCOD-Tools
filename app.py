# app.py
import streamlit as st
import ms_graph
from ui_header import render_logo_header

st.set_page_config(page_title="SMCOD Tools Portal", layout="wide")

render_logo_header()

token = ms_graph.get_access_token()

if not token:
    # --- Sign-in page (ALL BELOW LOGO) ---
    st.markdown("# SMCOD Tools Portal")
    st.caption("Sign in to access internal tools.")
    st.write("")

    c = st.columns([1, 4, 6])[0]  # left aligned column
    with c:
        if st.button("Sign In", use_container_width=False):
            ms_graph.login()

    st.stop()

# --- Dashboard (ALL BELOW LOGO) ---
top_l, top_r = st.columns([6, 1])
with top_l:
    st.markdown("# Tools")
with top_r:
    if st.button("Logout", use_container_width=True):
        ms_graph.logout()

st.write("")

# 2 rows x 3 columns tiles
rows = [
    [
        ("Incident Report Generator", "pages/1_Incident_Report_Generator.py", True),
        ("Tool 2 (Coming soon)", None, False),
        ("Tool 3 (Coming soon)", None, False),
    ],
    [
        ("Tool 4 (Coming soon)", None, False),
        ("Tool 5 (Coming soon)", None, False),
        ("Tool 6 (Coming soon)", None, False),
    ],
]

for row in rows:
    cols = st.columns(3)
    for col, (label, page, enabled) in zip(cols, row):
        with col:
            if enabled:
                if st.button(label, use_container_width=True):
                    st.switch_page(page)
            else:
                st.button(label, use_container_width=True, disabled=True)
    st.write("")
