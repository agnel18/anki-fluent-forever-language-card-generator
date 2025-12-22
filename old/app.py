#!/usr/bin/env python3
"""
Main entry point for Streamlit Cloud deployment.
This file serves as the entry point for the Language Learning App on Streamlit Cloud.
"""

import sys
import os

# Change to the streamlit_app directory so relative paths work correctly
streamlit_app_dir = os.path.join(os.path.dirname(__file__), 'streamlit_app')
os.chdir(streamlit_app_dir)

# Add the streamlit_app directory to the Python path
sys.path.insert(0, streamlit_app_dir)

# Import and run the main app
try:
    from app_v3 import main
    print("Successfully imported main from app_v3")
except ImportError as e:
    print(f"ImportError: {e}")
    import sys
    sys.exit(1)

# Run the main function
if __name__ == "__main__":
    main()