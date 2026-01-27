# app.py
from pathlib import Path
import base64
import streamlit as st
import ms_graph

st.set_page_config(page_title="SMCOD Tools Portal", layout="wide")

ROOT = Path(__file__).parent
LOGO_PATH = ROOT / "graphics" / "PhilSA_v4-01.png"

def _img_to_data_uri(path: Path) -> str | None:
    if not path.exists():
        return None
    ext = path.suffix.lower().lstrip(".")
    mime = "image/png" if ext == "png" else "image/jpeg"
    b64 = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:{mime};base64,{b64}"

logo_uri = _img_to_data_uri(LOGO_PATH)

st.markdown(
    """
<style>
header[data-testid="stHeader"] {visibility:hidden;height:0;}
.block-container {padding-top:0; max-width: 1400px;}

.topbar{
  height:120px;
  border-bottom: 2px solid rgba(0,0,0,0.15);
  display:flex;
  align-items:center;
  padding: 18px 28px;
}
.logo-circle{
  width:96px; height:96px;
  border-radius:999px;
  border:2px solid rgba(0,0,0,0.25);
  display:grid; place-items:center;
  overflow:hidden;
  background: rgba(0,0,0,0.02);
}
.logo-circle img{ width:90px; height:90px; object-fit:contain; }

.page{
  padding: 26px 28px;
}

.h1{ font-size:26px; font-weight:800; margin: 0 0 6px 0; }
.sub{ font-size:14px; color:#6b7280; margin: 0 0 18px 0; }

.login-area{ margin-top: 10px; }
.login-area a, .login-area button{ font-size:16px; }

.login-btn button{
  width: 240px !important;
  height: 64px !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
}

/* Tiles */
.tile button{
  width:100% !important;
  height: 92px !important;
  border-radius: 10px !important;
  border: 1px solid rgba(0,0,0,0.18) !important;
  background: white !important;
  color: #111 !important;
  font-size: 18px !important;
  font-weight: 650 !important;
}
.tile button:hover{
  border-color: rgba(0,0,0,0.35) !important;
  background: rgba(0,0,0,0.02) !important;
}

/* Logout */
.logout button{
  height: 40px !important;
  border-radius: 10px !important;
  font-weight: 700 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# Header bar (logo left)
if logo_uri:
    st.markdown(
        f"""
<div class="topbar">
  <div class="logo-circle">
    <img src="{logo_uri}" alt="PhilSA logo"/>
  </div>
</div>
""",
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
<div class="topbar">
  <div class="logo-circle">LOGO</div>
</div>
""",
        unsafe_allow_html=True,
    )

token = ms_graph.get_access_token()

# -----------------------------
# LOGIN VIEW
# -----------------------------
if not token:
    st.markdown("<div class='page'>", unsafe_allow_html=True)
    st.markdown("<div class='h1'>SMCOD Tools Portal</div>", unsafe_allow_html=True)
    st.markdown("<div class='sub'>Sign in to access internal tools.</div>", unsafe_allow_html=True)

    st.markdown("<div class='login-area login-btn'>", unsafe_allow_html=True)
    ms_graph.login_ui(scopes=ms_graph.DEFAULT_SCOPES_WRITE)
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.stop()

# -----------------------------
# DASHBOARD VIEW (AFTER LOGIN)
# -----------------------------
st.markdown("<div class='page'>", unsafe_allow_html=True)

top_l, top_r = st.columns([0.85, 0.15])
with top_l:
    st.markdown("<div class='h1'>Tools</div>", unsafe_allow_html=True)
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
    st.button("Tool 2 (Coming soon)")
    st.markdown("</div>", unsafe_allow_html=True)

with r1c3:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    st.button("Tool 3 (Coming soon)")
    st.markdown("</div>", unsafe_allow_html=True)

with r2c1:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    st.button("Tool 4 (Coming soon)")
    st.markdown("</div>", unsafe_allow_html=True)

with r2c2:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    st.button("Tool 5 (Coming soon)")
    st.markdown("</div>", unsafe_allow_html=True)

with r2c3:
    st.markdown("<div class='tile'>", unsafe_allow_html=True)
    st.button("Tool 6 (Coming soon)")
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)
