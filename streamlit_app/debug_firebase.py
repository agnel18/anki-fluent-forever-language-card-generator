# debug_firebase.py - Debug Firebase initialization on Streamlit Cloud

import streamlit as st
import json

st.title("🔍 Firebase Debug")

st.markdown("### Streamlit Secrets Check")
try:
    if hasattr(st, 'secrets') and st.secrets:
        st.write("Available secrets:")
        for key in st.secrets.keys():
            if 'FIREBASE' in key.upper():
                value = st.secrets[key]
                if isinstance(value, str) and len(value) > 50:
                    st.write(f"**{key}**: [REDACTED - {len(value)} chars]")
                else:
                    st.write(f"**{key}**: {value}")
    else:
        st.error("No secrets available")
except Exception as e:
    st.error(f"Error accessing secrets: {e}")

st.markdown("### Firebase Initialization Test")
try:
    from firebase_manager import init_firebase, firebase_available, firebase_initialized
    st.write(f"Firebase available: {firebase_available}")
    st.write(f"Firebase initialized: {firebase_initialized}")

    if firebase_available and not firebase_initialized:
        result = init_firebase()
        st.write(f"Init result: {result}")
        st.write(f"Firebase initialized after init: {firebase_initialized}")
    else:
        st.success("Firebase is ready!")

except Exception as e:
    st.error(f"Firebase test failed: {e}")
    import traceback
    st.code(traceback.format_exc())