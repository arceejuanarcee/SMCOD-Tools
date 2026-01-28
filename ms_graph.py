# ms_graph.py
import os
import time
import json
import streamlit as st
import msal

DEFAULT_SCOPES_READONLY = ["User.Read", "Sites.Read.All"]
DEFAULT_SCOPES_WRITE = ["User.Read", "Sites.ReadWrite.All"]  # requires admin consent in most tenants


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


def _get_cache() -> msal.SerializableTokenCache:
    if "msal_cache" not in st.session_state:
        st.session_state["msal_cache"] = ""
    cache = msal.SerializableTokenCache()
    if st.session_state["msal_cache"]:
        try:
            cache.deserialize(st.session_state["msal_cache"])
        except Exception:
            # corrupted cache, reset
            st.session_state["msal_cache"] = ""
    return cache


def _save_cache(cache: msal.SerializableTokenCache):
    if cache.has_state_changed:
        st.session_state["msal_cache"] = cache.serialize()


def _msal_app(cache: msal.SerializableTokenCache) -> msal.ConfidentialClientApplication:
    cfg = _require_cfg()
    return msal.ConfidentialClientApplication(
        client_id=cfg["client_id"],
        client_credential=cfg["client_secret"],
        authority=cfg["authority"],
        token_cache=cache,
    )


def _qp_get(name: str):
    v = st.query_params.get(name)
    if v is None:
        return None
    if isinstance(v, (list, tuple)):
        return v[0] if v else None
    return v


def logout():
    for k in ["ms_scopes", "ms_token", "ms_account_home_id", "msal_cache"]:
        st.session_state.pop(k, None)
    try:
        st.query_params.clear()
    except Exception:
        pass
    st.rerun()


def login_ui(scopes=None):
    """
    Call on the login page when NOT logged in.
    Uses auth-code flow (no flow/state persistence needed).
    """
    cfg = _require_cfg()
    if scopes is None:
        scopes = DEFAULT_SCOPES_READONLY

    st.session_state["ms_scopes"] = scopes

    cache = _get_cache()
    app = _msal_app(cache)

    # If callback returned with code
    code = _qp_get("code")
    if code:
        result = None
        try:
            result = app.acquire_token_by_authorization_code(
                code=code,
                scopes=scopes,
                redirect_uri=cfg["redirect_uri"],
            )
        except Exception as e:
            st.error(f"Login failed: {e}")
            st.stop()

        _save_cache(cache)

        if result and "access_token" in result:
            st.session_state["ms_token"] = result

            # Store which account to use for silent token
            accounts = app.get_accounts()
            if accounts:
                st.session_state["ms_account_home_id"] = accounts[0].get("home_account_id")

            try:
                st.query_params.clear()
            except Exception:
                pass

            st.rerun()
        else:
            # This is where "Need admin approval" often shows up (AAD error)
            st.error("Login did not return an access token.")
            if result:
                st.write(result)
            st.stop()

    # Otherwise show Sign In button
    auth_url = app.get_authorization_request_url(
        scopes=scopes,
        redirect_uri=cfg["redirect_uri"],
        prompt="select_account",
    )
    st.link_button("Sign In", auth_url)


def get_access_token():
    """
    Returns a valid access token string or None.
    Attempts silent refresh using MSAL cache.
    """
    scopes = st.session_state.get("ms_scopes") or DEFAULT_SCOPES_READONLY

    cache = _get_cache()
    app = _msal_app(cache)

    # 1) If we have an existing token in session, use it if still valid
    tok = st.session_state.get("ms_token")
    if tok:
        expires_at = tok.get("expires_at")
        if not expires_at:
            expires_in = int(tok.get("expires_in", 3600))
            tok["expires_at"] = int(time.time()) + expires_in
            expires_at = tok["expires_at"]

        # if token is good for at least 2 minutes, return it
        if int(expires_at) - int(time.time()) >= 120 and tok.get("access_token"):
            return tok["access_token"]

    # 2) Try silent token (this fixes “it won’t render after refresh / radio change”)
    accounts = app.get_accounts()
    if accounts:
        # if we previously stored a preferred account, try it first
        pref = st.session_state.get("ms_account_home_id")
        if pref:
            accounts = sorted(accounts, key=lambda a: 0 if a.get("home_account_id") == pref else 1)

        result = app.acquire_token_silent(scopes=scopes, account=accounts[0])
        _save_cache(cache)

        if result and "access_token" in result:
            st.session_state["ms_token"] = result
            st.session_state["ms_account_home_id"] = accounts[0].get("home_account_id")
            return result["access_token"]

    return None
