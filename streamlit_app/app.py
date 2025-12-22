#!/usr/bin/env python3
"""
Main entry point for Streamlit Cloud deployment in streamlit_app directory.
"""

try:
    from app_v3 import main
    print("Successfully imported main from app_v3")
except ImportError as e:
    print(f"ImportError: {e}")
    import sys
    sys.exit(1)

if __name__ == "__main__":
    main()