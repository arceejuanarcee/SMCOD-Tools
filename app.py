# app.py
from pathlib import Path
import streamlit as st
import ms_graph

st.set_page_config(layout="wide", page_title="SMCOD Tools Portal")

ROOT = Path(__file__).parent
LOGO = ROOT / "graphics" / "PhilSA_v4-01.png"

# ------------------ STYLE ------------------
st.markdown("""
<style>
header {visibility:hidden;}
.block-container {max-width:1400px;}

.header {
  display:flex;
  align-items:center;
  gap:24px;
  padding:20px 0;
}

.title h1 {
  margin:0;
  font-size:32px;
  font-weight:800;
}

.title p {
  margin:4px 0 0 0;
  color:#6b7280;
}

.login button {
  width:260px;
  height:64px;
  font-size:18px;
  font-weight:700;
}

.tile button {
  height:100px;
  font-size:20px;
  font-weight:700;
}
</style>
""", unsafe_allow_html=True)

# ------------------ HEADER ------------------
st.markdown("<div class='header'>", unsafe_allow_html=True)

if LOGO.exists():
    st.image(str(LOGO), width=160)  # ✅ BIG LOGO
else:
    st.write("LOGO")

st.markdown("""
<div class='title'>
  <h1>SMCOD Tools Portal</h1>
  <p>Access internal tools</p>
</div>
</div>
""", unsafe_allow_html=True)

# ------------------ LOGIN VIEW ------------------
if not ms_graph.is_authenticated():
    st.markdown("<div class='login'>", unsafe_allow_html=True)
    ms_graph.login_ui()
    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# ------------------ DASHBOARD ------------------
left, right = st.columns([6,1])
with right:
    if st.button("Logout"):
        ms_graph.logout()

st.write("")
st.write("")

# ------------------ TILES ------------------
r1c1, r1c2, r1c3 = st.columns(3)
r2c1, r2c2, r2c3 = st.columns(3)

with r1c1:
    if st.button("Incident Report Generator", key="ir"):
        st.switch_page("pages/1_Incident_Report_Generator.py")

with r1c2:
    st.button("Tool 2", disabled=True)

with r1c3:
    st.button("Tool 3", disabled=True)

with r2c1:
    st.button("Tool 4", disabled=True)

with r2c2:
    st.button("Tool 5", disabled=True)

with r2c3:
    st.button("Tool 6", disabled=True)
