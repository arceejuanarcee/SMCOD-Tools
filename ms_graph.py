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


def _qp_get(name: str):
    v = st.query_params.get(name)
    if v is None:
        return None
    if isinstance(v, (list, tuple)):
        return v[0] if v else None
    return v


def _get_cache() -> msal.SerializableTokenCache:
    """
    Keep MSAL token cache in session_state so MSAL can do silent refresh (when possible).
    """
    cache = msal.SerializableTokenCache()
    if "msal_cache" in st.session_state and st.session_state["msal_cache"]:
        try:
            cache.deserialize(st.session_state["msal_cache"])
        except Exception:
            # if corrupted, ignore
            pass
    return cache


def _save_cache(cache: msal.SerializableTokenCache):
    if cache.has_state_changed:
        st.session_state["msal_cache"] = cache.serialize()


def _msal_app() -> msal.ConfidentialClientApplication:
    cfg = _require_cfg()
    cache = _get_cache()
    return msal.ConfidentialClientApplication(
        client_id=cfg["client_id"],
        client_credential=cfg["client_secret"],
        authority=cfg["authority"],
        token_cache=cache,
    )


def logout():
    for k in ["ms_token", "ms_scopes", "msal_cache"]:
        st.session_state.pop(k, None)
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.rerun()


def login(scopes=None):
    """
    Wrapper so app.py can call ms_graph.login().
    """
    login_ui(scopes=scopes)


def login_ui(scopes=None):
    """
    Renders a Sign In link button + handles Azure callback (?code=...).
    Uses MSAL cache so subsequent refreshes can stay authenticated longer.
    """
    app = _msal_app()
    cfg = _require_cfg()

    if scopes is None:
        scopes = DEFAULT_SCOPES_READONLY
    st.session_state["ms_scopes"] = scopes

    # Already logged in
    if st.session_state.get("ms_token"):
        return

    code = _qp_get("code")
    if code:
        try:
            result = app.acquire_token_by_authorization_code(
                code=code,
                scopes=scopes,
                redirect_uri=cfg["redirect_uri"],
            )
            # Save cache updates
            _save_cache(app.token_cache)
        except Exception as e:
            st.error(f"Login failed: {e}")
            return

        if "access_token" in result:
            # add expires_at for our own checks
            expires_in = int(result.get("expires_in", 3600))
            result["expires_at"] = int(time.time()) + expires_in

            st.session_state["ms_token"] = result

            try:
                st.query_params.clear()
            except Exception:
                pass

            st.rerun()
        else:
            st.error("Login failed. Check Azure app registration + redirect URI + scopes.")
            st.write(result)
        return

    auth_url = app.get_authorization_request_url(
        scopes=scopes,
        redirect_uri=cfg["redirect_uri"],
        prompt="select_account",
    )
    st.link_button("Sign In", auth_url)


def get_access_token(scopes=None):
    """
    Returns a valid access token if possible.
    If expired, attempt silent refresh via MSAL cache.
    """
    if scopes is None:
        scopes = st.session_state.get("ms_scopes") or DEFAULT_SCOPES_READONLY

    token = st.session_state.get("ms_token")
    if token:
        expires_at = token.get("expires_at")
        if not expires_at:
            expires_in = int(token.get("expires_in", 3600))
            token["expires_at"] = int(time.time()) + expires_in
            expires_at = token["expires_at"]

        # if still valid (give 30s buffer)
        if int(expires_at) - int(time.time()) > 30:
            return token.get("access_token")

        # expired -> try silent refresh
        st.session_state.pop("ms_token", None)

    # Silent refresh attempt (works if MSAL cache has refresh token/account)
    app = _msal_app()
    accounts = app.get_accounts()
    if accounts:
        result = app.acquire_token_silent(scopes=scopes, account=accounts[0])
        _save_cache(app.token_cache)
        if result and "access_token" in result:
            expires_in = int(result.get("expires_in", 3600))
            result["expires_at"] = int(time.time()) + expires_in
            st.session_state["ms_token"] = result
            return result.get("access_token")

    return None
