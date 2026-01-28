# ms_graph.py
import os
import time
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


def _qp_get(name: str):
    """Streamlit query params can be str or list; normalize to str or None."""
    v = st.query_params.get(name)
    if v is None:
        return None
    if isinstance(v, (list, tuple)):
        return v[0] if v else None
    return v


def logout():
    for k in ["ms_token", "ms_scopes"]:
        st.session_state.pop(k, None)
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.rerun()


def login_ui(scopes=None):
    """
    Call ONLY on app.py when NOT logged in.
    This uses acquire_token_by_authorization_code (no saved flow/state dependency).
    """
    app = _msal_app()
    cfg = _require_cfg()

    if scopes is None:
        scopes = DEFAULT_SCOPES_READONLY
    st.session_state["ms_scopes"] = scopes

    # Already logged in
    if st.session_state.get("ms_token"):
        return

    # Callback: code from Azure
    code = _qp_get("code")
    if code:
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
            st.session_state["ms_token"] = result
            try:
                st.query_params.clear()
            except Exception:
                pass

            # Important: just rerun; app.py will now show tiles
            st.rerun()
        else:
            st.error("Login failed. Check Azure app registration + redirect URI + scopes.")
            st.write(result)
        return

    # Show Sign In button
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

    # Ensure we have an expires_at
    expires_at = token.get("expires_at")
    if not expires_at:
        expires_in = int(token.get("expires_in", 3600))
        token["expires_at"] = int(time.time()) + expires_in
        expires_at = token["expires_at"]

    # If expiring soon, force re-login
    if int(expires_at) - int(time.time()) < 120:
        st.session_state.pop("ms_token", None)
        return None

    return token.get("access_token")
