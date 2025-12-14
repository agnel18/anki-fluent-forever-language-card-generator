# pages/login.py - Login page for the language learning app

import streamlit as st
from constants import PAGE_API_SETUP


def render_login_page():
    """Render the login page with Google sign-in and guest options."""
    st.markdown("# 🔐 Login to Language Card Generator")
    st.markdown("""
    - **Sign in with Google for full access and persistent stats**
    - Or continue as guest (limited, no cloud sync)
    """)
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Sign in with Google", use_container_width=True):
            st.session_state.page = PAGE_API_SETUP
            st.session_state.is_guest = False
            st.rerun()
    with col2:
        if st.button("Continue as Guest", use_container_width=True):
            st.session_state.page = PAGE_API_SETUP
            st.session_state.is_guest = True
            st.rerun()