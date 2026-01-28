from __future__ import annotations

import runpy
from pathlib import Path
import streamlit as st
import ms_graph

APP_TITLE = "Incident Report Generator"
LOGO_BASENAME = "PhilSA_v4-01"

ROOT = Path(__file__).resolve().parents[1]


st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit header so it never overlaps your logo
st.markdown(
    """
    <style>
      header[data-testid="stHeader"] { display: none; }
      div[data-testid="stToolbar"] { display: none; }
      #MainMenu { visibility: hidden; }
      footer { visibility: hidden; }

      .block-container { padding-top: 1.3rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


def _find_logo_path() -> Path | None:
    gfx = ROOT / "graphics"
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        p = gfx / f"{LOGO_BASENAME}{ext}"
        if p.exists():
            return p
    for p in gfx.glob(f"{LOGO_BASENAME}*"):
        if p.is_file():
            return p
    return None


def render_logo_header():
    """Universal logo header. Everything else goes below."""
    logo_path = _find_logo_path()
    if logo_path:
        st.image(str(logo_path), width=120)
    st.divider()


def main():
    # Must be logged in; otherwise go back to login/home
    if not ms_graph.get_access_token():
        st.switch_page("app.py")

    render_logo_header()

    st.markdown(f"## {APP_TITLE}")

    nav = st.columns([0.22, 0.14, 0.64])
    with nav[0]:
        if st.button("← Back to Home", use_container_width=True):
            st.switch_page("app.py")
    with nav[1]:
        if st.button("Logout", use_container_width=True):
            ms_graph.logout()

    st.divider()

    # IMPORTANT: do NOT `import IR_gen` (it gets cached and becomes blank on reruns)
    runpy.run_path(str(ROOT / "IR_gen.py"), run_name="__main__")


if __name__ == "__main__":
    main()
