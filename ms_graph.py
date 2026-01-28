# ms_graph.py
import os
import time
import secrets
import streamlit as st
import msal

DEFAULT_SCOPES_READONLY = ["User.Read", "Sites.Read.All"]
DEFAULT_SCOPES_WRITE = ["User.Read", "Sites.ReadWrite.All"]


def _cfg() -> dict:
    s = st.secrets.get("ms_graph", {})
    tenant_id = s.get("tenant_id") or os.getenv("MS_TENANT_ID", "")
    client_id = s.get("client_id") or os.getenv("MS_CLIENT_ID", "")
    client_secret = s.get("client_secret") or os.getenv("MS_CLIENT_SECRET", "")
    redirect_uri = s.get("redirect_uri") or os.getenv("MS_REDIRECT_URI", "")
    authority = s.get("authority") or (f"https://login.microsoftonline.com/{tenant_id}" if tenant_id else "")

    return {
        "tenant_id": tenant_id,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "authority": authority,
    }


def _require_cfg() -> dict:
    cfg = _cfg()
    missing = [k for k in ["tenant_id", "client_id", "client_secret", "redirect_uri", "authority"] if not cfg.get(k)]
    if missing:
        st.error("Missing MS Graph config in secrets/env: " + ", ".join(missing))
        st.stop()
    return cfg


def _msal_app() -> msal.ConfidentialClientApplication:
    cfg = _require_cfg()
    return msal.ConfidentialClientApplication(
        client_id=cfg["client_id"],
        client_credential=cfg["client_secret"],
        authority=cfg["authority"],
    )


def logout():
    for k in ["ms_token", "ms_scopes"]:
        st.session_state.pop(k, None)
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.switch_page("app.py")


def login_ui(scopes=None):
    """
    Render sign-in button and handle callback.
    Call this ONLY in app.py (login page).
    """
    app = _msal_app()
    cfg = _require_cfg()

    if scopes is None:
        scopes = DEFAULT_SCOPES_READONLY
    st.session_state["ms_scopes"] = scopes

    # Already logged in
    if st.session_state.get("ms_token"):
        return

    qp = st.query_params

    # --------------------
    # CALLBACK (no state dependency)
    # --------------------
    if qp.get("code"):
        code = qp.get("code")
        try:
            result = app.acquire_token_by_authorization_code(
                code=code,
                scopes=scopes,
                redirect_uri=cfg["redirect_uri"],
            )
        except Exception as e:
            st.error(f"Login failed: {e}")
            return

        if "access_token" in result:
            # store token
            st.session_state["ms_token"] = result
            # clear query params
            try:
                st.query_params.clear()
            except Exception:
                pass
            # always go to portal dashboard
            st.switch_page("app.py")
        else:
            st.error("Login failed. Check Azure app registration + scopes.")
            st.write(result)
        return

    # --------------------
    # SIGN IN LINK
    # --------------------
    # We still generate a state for security, but we DO NOT require it in callback.
    _ = secrets.token_urlsafe(16)

    auth_url = app.get_authorization_request_url(
        scopes=scopes,
        redirect_uri=cfg["redirect_uri"],
        prompt="select_account",
    )

    st.link_button("Sign In", auth_url)


def get_access_token():
    token = st.session_state.get("ms_token")
    if not token:
        return None

    # compute expires_at if missing
    expires_at = token.get("expires_at")
    if not expires_at:
        expires_in = int(token.get("expires_in", 3600))
        token["expires_at"] = int(time.time()) + expires_in
        expires_at = token["expires_at"]

    # expire soon => force re-login
    if int(expires_at) - int(time.time()) < 120:
        st.session_state.pop("ms_token", None)
        return None

    return token.get("access_token")
