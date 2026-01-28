import streamlit as st
from pathlib import Path
import ms_graph

APP_TITLE = "SMCOD Tools Portal"
LOGO_BASENAME = "PhilSA_v4-01"  # located inside ./graphics/

ROOT = Path(__file__).parent


def _find_logo_path() -> Path | None:
    gfx = ROOT / "graphics"
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        p = gfx / f"{LOGO_BASENAME}{ext}"
        if p.exists():
            return p
    # also allow exact filename if user forgot extension
    for p in gfx.glob(f"{LOGO_BASENAME}*"):
        if p.is_file():
            return p
    return None


def render_header():
    """Universal header used on ALL pages."""
    logo_path = _find_logo_path()

    st.markdown(
        """
        <style>
          /* Tighten overall top padding so header feels like a real app bar */
          .block-container { padding-top: 1.0rem; }

          /* Make our buttons look like tiles */
          div[data-testid="stButton"] > button.tile {
            height: 110px;
            width: 100%;
            font-size: 1.1rem;
            border-radius: 14px;
            border: 1px solid rgba(255,255,255,0.14);
            background: rgba(255,255,255,0.03);
          }
          div[data-testid="stButton"] > button.tile:hover {
            border-color: rgba(255,255,255,0.28);
            background: rgba(255,255,255,0.06);
          }

          /* Bigger Sign In button */
          div[data-testid="stLinkButton"] a {
            border-radius: 12px !important;
            padding: 12px 18px !important;
            font-size: 1.05rem !important;
            font-weight: 600 !important;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )

    c1, c2 = st.columns([0.20, 0.80], gap="small")
    with c1:
        if logo_path:
            st.image(str(logo_path), width=120)
        else:
            st.write("")  # keep spacing if missing
    with c2:
        # Intentionally NO extra text next to logo (user request)
        st.write("")


def require_login(scopes=None) -> bool:
    """Return True if logged in, otherwise renders login UI and returns False."""
    token = ms_graph.get_access_token()
    if token:
        return True

    render_header()

    st.markdown(f"## {APP_TITLE}")
    st.caption("Sign in to access internal tools.")
    ms_graph.login_ui(scopes=scopes)
    return False


def dashboard():
    render_header()

    top = st.columns([0.85, 0.15])
    with top[0]:
        st.markdown("## Tools")
        st.caption("Choose a tool to open.")
    with top[1]:
        if st.button("Logout", use_container_width=True):
            ms_graph.logout()

    st.write("")

    # 2 rows x 3 columns tiles
    r1 = st.columns(3, gap="large")
    r2 = st.columns(3, gap="large")

    with r1[0]:
        if st.button("Incident Report Generator", key="tile_ir", use_container_width=True, type="secondary"):
            st.switch_page("pages/1_Incident_Report_Generator.py")
        # add CSS class after render (Streamlit uses same DOM)
        st.markdown(
            "<script>document.querySelector('button[kind=\"secondary\"][data-testid=\"baseButton-secondary\"][aria-label=\"Incident Report Generator\"]').classList.add('tile');</script>",
            unsafe_allow_html=True,
        )
    with r1[1]:
        st.button("Tool 2 (Coming soon)", key="tile2", use_container_width=True, disabled=True)
    with r1[2]:
        st.button("Tool 3 (Coming soon)", key="tile3", use_container_width=True, disabled=True)

    with r2[0]:
        st.button("Tool 4 (Coming soon)", key="tile4", use_container_width=True, disabled=True)
    with r2[1]:
        st.button("Tool 5 (Coming soon)", key="tile5", use_container_width=True, disabled=True)
    with r2[2]:
        st.button("Tool 6 (Coming soon)", key="tile6", use_container_width=True, disabled=True)


def main():
    st.set_page_config(page_title=APP_TITLE, page_icon="🛰️", layout="wide")

    # One login for all pages: token lives in st.session_state
    if not require_login(scopes=ms_graph.DEFAULT_SCOPES_WRITE):
        return

    dashboard()


if __name__ == "__main__":
    main()
