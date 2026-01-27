# app.py
from pathlib import Path
import streamlit as st
import ms_graph

st.set_page_config(page_title="SMCOD Tools Portal", layout="wide")

ROOT = Path(__file__).parent
LOGO_PATH = ROOT / "graphics" / "PhilSA_v4-01.png"

# -----------------------------
# Minimal CSS: left-aligned login + tile dashboard
# -----------------------------
st.markdown(
    """
<style>
header[data-testid="stHeader"] {visibility:hidden;height:0;}
.block-container {padding-top: 0.6rem; padding-bottom: 2rem; max-width: 1400px;}

/* Left header area */
.top-row {
  display: flex;
  align-items: center;
  gap: 14px;
  margin-top: 4px;
  margin-bottom: 8px;
}
.brand-text .brand-title {
  font-size: 20px;
  font-weight: 800;
  margin: 0;
  line-height: 1.1;
}
.brand-text .brand-sub {
  font-size: 13px;
  color: #6b7280;
  margin: 2px 0 0 0;
}

/* Make login button not huge */
.login-btn div[data-testid="stButton"] > button {
  height: 44px;
  width: 160px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 700;
}

/* Tile buttons (neutral, no forced theme) */
.tile div[data-testid="stButton"] > button {
  width: 100%;
  height: 92px;
  border-radius: 10px;
  border: 1px solid rgba(0,0,0,0.18);
  background: white;
  color: #111;
  font-size: 18px;
  font-weight: 650;
  text-align: center;
}
.tile div[data-testid="stButton"] > button:hover {
  border-color: rgba(0,0,0,0.35);
  background: rgba(0,0,0,0.02);
}

/* Small logout button */
.small-btn div[data-testid="stButton"] > button {
  height: 38px;
  border-radius: 8px;
  font-size: 13px;
  font-weight: 700;
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Helper: brand header (left)
# -----------------------------
def render_brand_header():
    cols = st.columns([0.08, 0.92])
    with cols[0]:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=56)
        else:
            st.write("LOGO")
    with cols[1]:
        st.markdown(
            """
<div class="brand-text">
  <p class="brand-title">SMCOD Tools Portal</p>
  <p class="brand-sub">Sign in to access internal tools.</p>
</div>
""",
            unsafe_allow_html=True,
        )


# -----------------------------
# Decide view by token
# -----------------------------
token = ms_graph.get_access_token()

# =============================
# VIEW 1: LOGIN (left aligned)
# =============================
if not token:
    render_brand_header()
    st.write("")

    # login button aligned to left as well
    st.markdown("<div class='login-btn'>", unsafe_allow_html=True)
    ms_graph.login_ui(scopes=ms_graph.DEFAULT_SCOPES_WRITE)
    st.markdown("</div>", unsafe_allow_html=True)

    st.stop()

# =============================
# VIEW 2: DASHBOARD AFTER LOGIN
# =============================
# Header row with logo + title on left, logout on right
left, right = st.columns([0.85, 0.15])
with left:
    render_brand_header()
with right:
    st.markdown("<div class='small-btn'>", unsafe_allow_html=True)
    if st.button("Logout"):
        ms_graph.logout()
    st.markdown("</div>", unsafe_allow_html=True)

st.write("")
st.write("")

# Tiles (2 rows x 3)
r1c1, r1c2, r1c3 = st.columns(3, gap="large")
r2c1, r2c2, r2c3 = st.columns(3, gap="large")

with r1c1:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    if st.button("Incident Report Generator"):
        st.switch_page("pages/1_Incident_Report_Generator.py")
    st.markdown("</div>", unsafe_allow_html=True)

with r1c2:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    if st.button("Tool 2 (Coming soon)"):
        st.info("Placeholder. Wire your script later.")
    st.markdown("</div>", unsafe_allow_html=True)

with r1c3:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    if st.button("Tool 3 (Coming soon)"):
        st.info("Placeholder. Wire your script later.")
    st.markdown("</div>", unsafe_allow_html=True)

with r2c1:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    if st.button("Tool 4 (Coming soon)"):
        st.info("Placeholder. Wire your script later.")
    st.markdown("</div>", unsafe_allow_html=True)

with r2c2:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    if st.button("Tool 5 (Coming soon)"):
        st.info("Placeholder. Wire your script later.")
    st.markdown("</div>", unsafe_allow_html=True)

with r2c3:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    if st.button("Tool 6 (Coming soon)"):
        st.info("Placeholder. Wire your script later.")
    st.markdown("</div>", unsafe_allow_html=True)
