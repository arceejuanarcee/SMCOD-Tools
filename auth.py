# auth.py
import streamlit as st
import ms_graph

def require_login():
    """
    Ensures user is logged in.
    If not, redirect to app.py (the only page that shows login UI).
    """
    token = ms_graph.get_access_token()
    if not token:
        st.warning("Please sign in to continue.")
        st.switch_page("app.py")
        st.stop()
    return token
