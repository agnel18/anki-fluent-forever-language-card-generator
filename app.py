#!/usr/bin/env python3
"""
Main entry point for Streamlit Cloud deployment.
This file serves as the entry point for the Language Learning App on Streamlit Cloud.
"""

import sys
import os

# Add the streamlit_app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'streamlit_app'))

# Import and run the main app
from app_v3 import *