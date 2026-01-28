from __future__ import annotations

import streamlit as st
from pathlib import Path
import ms_graph

APP_TITLE = "SMCOD Tools Portal"
LOGO_BASENAME = "PhilSA_v4-01"  # inside ./graphics/


# ----------------------------
# Page / Global UI settings
# ----------------------------
st.set_page_config(
    page_title=APP_TITLE,
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Hide Streamlit’s built-in header so it doesn’t cover your logo/header
st.markdown(
    """
    <style>
      header[data-testid="stHeader"] { display: none; }
      div[data-testid="stToolbar"] { display: none; }
      #MainMenu { visibility: hidden; }
      footer { visibility: hidden; }

      /* top spacing now controlled by us */
      .block-container { padding-top: 1.3rem; }

      /* Make dashboard buttons look like tiles (only affects st.button) */
      div[data-testid="stButton"] > button {
        height: 84px;
        border-radius: 14px;
        font-size: 1.05rem;
        font-weight: 600;
        border: 1px solid rgba(255,255,255,0.14);
        background: rgba(255,255,255,0.03);
      }
      div[data-testid="stButton"] > button:hover {
        border-color: rgba(255,255,255,0.26);
        background: rgba(255,255,255,0.06);
      }

      /* Make link button (Sign In) bigger */
      div[data-testid="stLinkButton"] a {
        border-radius: 12px !important;
        padding: 12px 18px !important;
        font-size: 1.05rem !important;
        font-weight: 700 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)


ROOT = Path(__file__).parent


def _find_logo_path() -> Path | None:
    gfx = ROOT / "graphics"
    for ext in [".png", ".jpg", ".jpeg", ".webp"]:
        p = gfx / f"{LOGO_BASENAME}{ext}"
        if p.exists():
            return p
    # fallback: any file that starts with LOGO_BASENAME
    for p in gfx.glob(f"{LOGO_BASENAME}*"):
        if p.is_file():
            return p
    return None


def render_logo_header():
    """Universal logo header. All texts/buttons should be BELOW this."""
    logo_path = _find_logo_path()
    if logo_path:
        st.image(str(logo_path), width=120)
    st.divider()


def require_login(scopes=None) -> bool:
    """
    One login page for the whole app.
    If not logged in, shows the login landing page and returns False.
    If logged in, returns True.
    """
    token = ms_graph.get_access_token()
    if token:
        return True

    # Landing / login page
    render_logo_header()

    st.markdown(f"## {APP_TITLE}")
    st.caption("Sign in to access internal tools.")

    # IR needs write access typically; keep scopes as you’ve used before
    ms_graph.login_ui(scopes=scopes)

    return False


def show_dashboard():
    render_logo_header()

    top = st.columns([0.84, 0.16])
    with top[0]:
        st.markdown("## Tools")
        st.caption("Choose a tool to open.")
    with top[1]:
        # This is NOT a tile – but it will inherit the button CSS. We can keep it.
        if st.button("Logout", use_container_width=True):
            ms_graph.logout()

    st.write("")

    # Dashboard tiles
    row1 = st.columns(3, gap="large")
    row2 = st.columns(3, gap="large")

    with row1[0]:
        if st.button("Incident Report Generator", use_container_width=True):
            st.switch_page("pages/1_Incident_Report_Generator.py")

    with row1[1]:
        st.button("Tool 2 (Coming soon)", use_container_width=True, disabled=True)

    with row1[2]:
        st.button("Tool 3 (Coming soon)", use_container_width=True, disabled=True)

    with row2[0]:
        st.button("Tool 4 (Coming soon)", use_container_width=True, disabled=True)

    with row2[1]:
        st.button("Tool 5 (Coming soon)", use_container_width=True, disabled=True)

    with row2[2]:
        st.button("Tool 6 (Coming soon)", use_container_width=True, disabled=True)


def main():
    # Use WRITE since IR tool needs SharePoint uploads/drive calls
    if not require_login(scopes=ms_graph.DEFAULT_SCOPES_WRITE):
        return

    show_dashboard()


if __name__ == "__main__":
    main()
