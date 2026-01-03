#!/usr/bin/env python3
"""
Direct test of the settings page to check Firebase authentication
"""
import sys
import os

# Add streamlit_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

# Mock Streamlit for testing
class MockStreamlit:
    def __init__(self):
        self.session_state = type('obj', (object,), {'page': 'settings'})()
        self.secrets = type('obj', (object,), {
            'FIREBASE_WEB_API_KEY': 'AIzaSyDUMMY_API_KEY_FOR_TESTING',
            'FIREBASE_PROJECT_ID': 'dummy-project-id'
        })()
        self.query_params = {}

    def title(self, text):
        print(f"Title: {text}")

    def markdown(self, text, **kwargs):
        print(f"Markdown: {text[:100]}...")

    def write(self, text):
        print(f"Write: {text}")

    def columns(self, n):
        return [MockColumn() for _ in range(n)]

    def success(self, text):
        print(f"✅ Success: {text}")

    def info(self, text):
        print(f"ℹ️ Info: {text}")

    def warning(self, text):
        print(f"⚠️ Warning: {text}")

    def error(self, text):
        print(f"❌ Error: {text}")

    def button(self, text, **kwargs):
        print(f"Button: {text}")
        return False  # Never clicked

    def rerun(self):
        print("Rerun called")

    def sidebar(self):
        return self

class MockColumn:
    def __init__(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

# Replace streamlit with mock
sys.modules['streamlit'] = MockStreamlit()

# Now test the settings page
try:
    print("Testing settings page render...")
    from page_modules.settings import render_settings_page
    print("✅ Settings page imported successfully")

    # This will show us if the Firebase JavaScript is being generated
    render_settings_page()
    print("✅ Settings page rendered without errors")

except Exception as e:
    print(f"❌ Error testing settings page: {e}")
    import traceback
    traceback.print_exc()