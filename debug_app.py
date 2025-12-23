#!/usr/bin/env python3
"""
Minimal test script to debug Streamlit app startup issues
"""
import sys
import os

# Add streamlit_app to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

def test_main_execution():
    """Test the main execution flow without Streamlit"""
    try:
        print("Testing imports...")

        # Test basic imports
        import streamlit as st
        print("✅ Streamlit imported")

        # Test constants
        from constants import GROQ_CALL_LIMIT
        print(f"✅ Constants loaded: GROQ_CALL_LIMIT = {GROQ_CALL_LIMIT}")

        # Test state manager functions
        from state_manager import initialize_languages_config, initialize_firebase_settings
        print("✅ State manager functions imported")

        # Test router
        from router import route_to_page
        print("✅ Router imported")

        # Test page modules
        from page_modules.main import render_main_page
        from page_modules.settings import render_settings_page
        from page_modules.auth_handler import render_auth_handler_page
        print("✅ Page modules imported")

        print("🎉 All imports successful! The issue might be in Streamlit runtime.")

    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_main_execution()