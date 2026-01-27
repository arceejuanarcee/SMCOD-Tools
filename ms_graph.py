# ms_graph.py
import os
import time
import streamlit as st
import msal

DEFAULT_SCOPES = ["User.Read"]

def _cfg():
    s = st.secrets["ms_graph"]
    return {
        "client_id": s["client_id"],
        "client_secret": s["client_secret"],
        "tenant_id": s["tenant_id"],
        "authority": f"https://login.microsoftonline.com/{s['tenant_id']}",
        "redirect_uri": s["redirect_uri"],
    }

def _app():
    c = _cfg()
    return msal.ConfidentialClientApplication(
        c["client_id"],
        authority=c["authority"],
        client_credential=c["client_secret"],
    )

def login_ui():
    if st.session_state.get("authenticated"):
        return

    app = _app()
    cfg = _cfg()

    # CALLBACK
    if "code" in st.query_params:
        result = app.acquire_token_by_authorization_code(
            st.query_params["code"],
            scopes=DEFAULT_SCOPES,
            redirect_uri=cfg["redirect_uri"],
        )

        if "access_token" in result:
            st.session_state["authenticated"] = True
            st.session_state["token"] = result
            st.query_params.clear()
            st.switch_page("app.py")
        else:
            st.error("Login failed")
        st.stop()

    # LOGIN BUTTON
    auth_url = app.get_authorization_request_url(
        scopes=DEFAULT_SCOPES,
        redirect_uri=cfg["redirect_uri"],
        prompt="select_account",
    )
    st.link_button("Sign In", auth_url)

def is_authenticated():
    return st.session_state.get("authenticated", False)

def logout():
    st.session_state.clear()
    st.switch_page("app.py")
