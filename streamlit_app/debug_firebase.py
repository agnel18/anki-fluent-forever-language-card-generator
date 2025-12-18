# debug_firebase.py - Debug Firebase initialization on Streamlit Cloud

import streamlit as st
import json

def main():
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
    try:
        import firebase_admin
        from firebase_admin import credentials

        st.write("**Firebase Admin SDK version:**", firebase_admin.__version__)

        # Check if app already exists
        st.write(f"**Firebase apps count:** {len(firebase_admin._apps)}")

        # Try to manually initialize with secrets
        st.write("**Manual initialization test:**")
        try:
            api_key = st.secrets.get("FIREBASE_API_KEY")
            project_id = st.secrets.get("FIREBASE_PROJECT_ID")
            private_key = st.secrets.get("FIREBASE_PRIVATE_KEY")
            client_email = st.secrets.get("FIREBASE_CLIENT_EMAIL")

            st.write(f"Project ID available: {bool(project_id)}")
            st.write(f"Private key available: {bool(private_key)}")
            st.write(f"Client email available: {bool(client_email)}")

            if private_key and client_email and project_id:
                # Create credentials dict
                cred_dict = {
                    "type": "service_account",
                    "project_id": project_id,
                    "private_key_id": st.secrets.get("FIREBASE_PRIVATE_KEY_ID", ""),
                    "private_key": private_key.replace('\\n', '\n'),
                    "client_email": client_email,
                    "client_id": st.secrets.get("FIREBASE_CLIENT_ID", ""),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": st.secrets.get("FIREBASE_CLIENT_X509_CERT_URL", "")
                }

                st.write("Creating credentials...")
                cred = credentials.Certificate(cred_dict)

                st.write("Initializing Firebase...")
                firebase_admin.initialize_app(cred, {'projectId': project_id})

                st.success("✅ Manual initialization successful!")
            else:
                st.error("Missing required secrets for manual initialization")

        except Exception as manual_error:
            st.error(f"Manual initialization failed: {manual_error}")
            st.code(str(manual_error))

    except Exception as detailed_error:
        st.error(f"Detailed debug failed: {detailed_error}")
        st.code(str(detailed_error))