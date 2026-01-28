# app.py
from pathlib import Path
import streamlit as st
import ms_graph

st.set_page_config(page_title="SMCOD Tools Portal", layout="wide")

ROOT = Path(__file__).parent
LOGO_PATH = ROOT / "graphics" / "PhilSA_v4-01.png"

# Minimal layout tweaks (no colors forced)
st.markdown(
    """
<style>
header[data-testid="stHeader"] {visibility:hidden;height:0;}
.block-container {padding-top: 1rem; max-width: 1400px;}
.tile button {width: 100% !important; height: 95px !important; font-size: 18px !important; font-weight: 700 !important;}
.logout button {height: 40px !important; font-weight: 700 !important;}
</style>
""",
    unsafe_allow_html=True,
)

token = ms_graph.get_access_token()

# -------------------------
# LOGIN VIEW (left aligned)
# -------------------------
if not token:
    c1, c2 = st.columns([1, 6])
    with c1:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=220)  # ✅ BIG logo (reverted simple)
        else:
            st.write("LOGO")
    with c2:
        st.title("SMCOD Tools Portal")
        st.caption("Sign in to access internal tools.")
        st.write("")
        ms_graph.login_ui(scopes=ms_graph.DEFAULT_SCOPES_WRITE)

    st.stop()

# -------------------------
# DASHBOARD VIEW (tiles)
# -------------------------
top_l, top_r = st.columns([6, 1])
with top_l:
    st.title("Tools")
with top_r:
    st.markdown("<div class='logout'>", unsafe_allow_html=True)
    if st.button("Logout"):
        ms_graph.logout()
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")

r1c1, r1c2, r1c3 = st.columns(3, gap="large")
r2c1, r2c2, r2c3 = st.columns(3, gap="large")

with r1c1:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    if st.button("Incident Report Generator"):
        st.switch_page("pages/1_Incident_Report_Generator.py")
    st.markdown("</div>", unsafe_allow_html=True)

with r1c2:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    st.button("Tool 2 (Coming soon)", disabled=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r1c3:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    st.button("Tool 3 (Coming soon)", disabled=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r2c1:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    st.button("Tool 4 (Coming soon)", disabled=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r2c2:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    st.button("Tool 5 (Coming soon)", disabled=True)
    st.markdown("</div>", unsafe_allow_html=True)

with r2c3:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    st.button("Tool 6 (Coming soon)", disabled=True)
    st.markdown("</div>", unsafe_allow_html=True)
