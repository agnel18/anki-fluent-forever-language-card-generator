#!/usr/bin/env python3
"""
Main entry point for Streamlit Cloud deployment.
This file imports and runs the main app from streamlit_app/app_v3.py
"""

import sys
import os

# Add streamlit_app directory to Python path so imports work
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

try:
    from app_v3 import main
    print("Successfully imported main from streamlit_app.app_v3")
except ImportError as e:
    print(f"ImportError: {e}")
    import sys
    sys.exit(1)

if __name__ == "__main__":
    main()