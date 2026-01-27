# app.py
from pathlib import Path
import streamlit as st
import ms_graph

st.set_page_config(page_title="PhilSA Tools Portal", layout="wide")

ROOT = Path(__file__).parent
LOGO_PATH = ROOT / "graphics" / "PhilSA_v4-01.png"

# -----------------------------
# Minimal, neutral styling
# -----------------------------
st.markdown(
    """
<style>
header[data-testid="stHeader"] {visibility:hidden;height:0;}
.block-container {padding-top: 1.2rem; padding-bottom: 2rem; max-width: 1200px;}
/* Make buttons look like tiles without enforcing a color scheme */
div[data-testid="stButton"] > button {
  width: 100%;
  height: 90px;
  border-radius: 10px;
  border: 1px solid rgba(0,0,0,0.18);
  background: white;
  color: #111;
  font-size: 18px;
  font-weight: 600;
}
div[data-testid="stButton"] > button:hover {
  border-color: rgba(0,0,0,0.35);
  background: rgba(0,0,0,0.02);
}
.small-btn div[data-testid="stButton"] > button {
  height: 42px;
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
}
.center {display:flex; justify-content:center;}
.muted {color:#666; font-size:14px;}
.title {font-size:28px; font-weight:800; text-align:center; margin-top: 10px;}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Shared header (logo only)
# -----------------------------
st.markdown("<div class='center'>", unsafe_allow_html=True)
if LOGO_PATH.exists():
    st.image(str(LOGO_PATH), width=170)
else:
    st.write("LOGO")
st.markdown("</div>", unsafe_allow_html=True)

# -----------------------------
# Decide which view to show
# -----------------------------
token = ms_graph.get_access_token()

# =============================
# VIEW 1: LOGIN LANDING PAGE
# =============================
if not token:
    st.markdown("<div class='title'>PhilSA Tools Portal</div>", unsafe_allow_html=True)
    st.markdown("<p class='muted' style='text-align:center;'>Sign in to access internal tools.</p>", unsafe_allow_html=True)
    st.write("")

    # Login button only appears here
    st.markdown("<div class='center'>", unsafe_allow_html=True)
    st.markdown("<div style='width:340px;'>", unsafe_allow_html=True)
    ms_graph.login_ui(scopes=ms_graph.DEFAULT_SCOPES_WRITE)
    st.markdown("</div></div>", unsafe_allow_html=True)

    st.stop()

# =============================
# VIEW 2: DASHBOARD AFTER LOGIN
# =============================
top_l, top_r = st.columns([6, 1])
with top_l:
    st.markdown("<div class='title' style='text-align:left;'>Tools</div>", unsafe_allow_html=True)
with top_r:
    st.markdown("<div class='small-btn'>", unsafe_allow_html=True)
    if st.button("Logout"):
        ms_graph.logout()
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

# 2 rows x 3 columns
r1c1, r1c2, r1c3 = st.columns(3, gap="large")
r2c1, r2c2, r2c3 = st.columns(3, gap="large")

with r1c1:
    if st.button("Incident Report Generator"):
        st.switch_page("pages/1_Incident_Report_Generator.py")

with r1c2:
    if st.button("Tool 2"):
        st.info("Wire your script here.")

with r1c3:
    if st.button("Tool 3"):
        st.info("Wire your script here.")

with r2c1:
    if st.button("Tool 4"):
        st.info("Wire your script here.")

with r2c2:
    if st.button("Tool 5"):
        st.info("Wire your script here.")

with r2c3:
    if st.button("Tool 6"):
        st.info("Wire your script here.")
