import streamlit as st
import sys
import os

# Add the streamlit_app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

# Import the auth handler
from page_modules.auth_handler import render_auth_handler_page

# Set up minimal session state for testing
if 'page' not in st.session_state:
    st.session_state.page = 'auth_handler'

# Mock secrets for testing
if not hasattr(st, 'secrets') or not st.secrets:
    class MockSecrets:
        def get(self, key, default=None):
            secrets = {
                'FIREBASE_WEB_API_KEY': 'AIzaSyDUMMY_API_KEY_FOR_TESTING',
                'FIREBASE_PROJECT_ID': 'dummy-project-id'
            }
            return secrets.get(key, default)
    st.secrets = MockSecrets()

# Mock query params
if not hasattr(st, 'query_params') or not st.query_params:
    st.query_params = {}

# Render the auth handler page
render_auth_handler_page()

# Add a note that this is for testing
st.markdown("---")
st.info("🔧 This is a test page to verify Firebase JavaScript injection. Check browser console for Firebase messages.")