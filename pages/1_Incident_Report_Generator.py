import runpy
from pathlib import Path
import streamlit as st
import ms_graph

APP_TITLE = "SMCOD Tools Portal"
ROOT = Path(__file__).resolve().parents[1]
LOGO_BASENAME = "PhilSA_v4-01"


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


def render_header(title: str):
    logo_path = _find_logo_path()

    st.markdown(
        """
        <style>
          .block-container { padding-top: 1.0rem; }
        </style>
        """,
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns([0.20, 0.80], gap="small")
    with c1:
        if logo_path:
            st.image(str(logo_path), width=120)
    with c2:
        st.markdown(f"## {title}")


def main():
    st.set_page_config(page_title="Incident Report Generator", page_icon="📝", layout="wide")

    # Require login (shared session across pages)
    if not ms_graph.get_access_token():
        st.switch_page("app.py")

    render_header("Incident Report Generator")

    # Navigation row (below header)
    nav = st.columns([0.20, 0.15, 0.65])
    with nav[0]:
        if st.button("← Back to Home", use_container_width=True):
            st.switch_page("app.py")
    with nav[1]:
        if st.button("Logout", use_container_width=True):
            ms_graph.logout()

    st.divider()

    # IMPORTANT:
    # - DO NOT `import IR_gen` here, because imports are cached and the app can appear blank
    #   after reruns (e.g., refresh, radio changes).
    # - runpy re-executes IR_gen.py on each rerun.
    runpy.run_path(str(ROOT / "IR_gen.py"), run_name="__main__")


if __name__ == "__main__":
    main()
