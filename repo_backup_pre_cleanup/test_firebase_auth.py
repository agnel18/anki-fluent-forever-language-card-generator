import streamlit as st
import sys
import os

# Add streamlit_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

st.title("🔧 Firebase Auth Test Page")

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

# Initialize basic session state
if 'page' not in st.session_state:
    st.session_state.page = 'settings'

try:
    # Import and render the settings page (which has the sign-in button)
    from page_modules.settings import render_settings_page
    render_settings_page()
    st.success("✅ Settings page rendered successfully!")

except Exception as e:
    st.error(f"❌ Error rendering settings page: {e}")
    st.code(str(e))
    import traceback
    st.code(traceback.format_exc())