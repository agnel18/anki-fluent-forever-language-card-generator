# auth_handler.py - Google OAuth authentication handler page

import streamlit as st
import time
import json
import requests
from firebase_manager import is_signed_in, get_current_user

# Google OAuth configuration
GOOGLE_CLIENT_ID = st.secrets.get("GOOGLE_CLIENT_ID", "")
GOOGLE_CLIENT_SECRET = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
REDIRECT_URI = st.secrets.get("REDIRECT_URI", "http://localhost:8501")

# Google OAuth endpoints
AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

def render_auth_handler_page():
    """Handle Google OAuth authentication flow."""
    st.title("🔐 Sign In with Google")
    st.markdown("Please complete the Google authentication...")

    # Debug info
    st.write("**Debug Info:**")
    st.write(f"Client ID configured: {bool(GOOGLE_CLIENT_ID)}")
    st.write(f"Client Secret configured: {bool(GOOGLE_CLIENT_SECRET)}")
    st.write(f"Redirect URI: {REDIRECT_URI}")
    st.write(f"Auth URL: {AUTH_URL}")

    # Check if we have authorization code
    if st.query_params.get("code"):
        code = st.query_params.get("code")
        st.write(f"**Received authorization code:** {code[:20]}...")

        # Exchange code for token
        try:
            # Exchange authorization code for access token
            token_data = {
                'client_id': GOOGLE_CLIENT_ID,
                'client_secret': GOOGLE_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code',
                'redirect_uri': REDIRECT_URI
            }

            st.write("**Exchanging code for token...**")
            token_response = requests.post(TOKEN_URL, data=token_data)
            st.write(f"**Token response status:** {token_response.status_code}")

            token_json = token_response.json()
            st.write(f"**Token response:** {token_json}")

            if 'access_token' in token_json:
                access_token = token_json['access_token']
                st.write("**Got access token, fetching user info...**")

                # Get user info from Google
                headers = {'Authorization': f'Bearer {access_token}'}
                user_response = requests.get(USERINFO_URL, headers=headers)
                st.write(f"**User info response status:** {user_response.status_code}")

                user_info = user_response.json()
                st.write(f"**User info:** {user_info}")

                if user_info.get('email'):
                    # Create user object
                    user = {
                        'email': user_info.get('email', ''),
                        'uid': user_info.get('id', ''),
                        'display_name': user_info.get('name', ''),
                        'photo_url': user_info.get('picture', ''),
                        'email_verified': user_info.get('verified_email', False)
                    }

                    # Store user in session state
                    st.session_state.user = user
                    st.session_state.is_guest = False

                    # Load cloud data if available
                    try:
                        from sync_manager import load_cloud_data
                        load_cloud_data()
                    except Exception as e:
                        st.warning(f"Could not load cloud data: {e}")

                    st.success("✅ Successfully signed in with Google!")
                    st.info("Your settings will now sync across devices.")

                    # Show user info
                    st.markdown("---")
                    st.markdown("**Welcome!**")
                    st.markdown(f"**Name:** {user['display_name']}")
                    st.markdown(f"**Email:** {user['email']}")

                    # Clear query params
                    st.query_params.clear()

                    # Auto-redirect after success
                    time.sleep(3)
                    st.session_state.page = "main"
                    st.rerun()
                else:
                    st.error("❌ Failed to get user information from Google")
            else:
                st.error(f"❌ Failed to get access token: {token_json.get('error_description', 'Unknown error')}")
        except Exception as e:
            st.error(f"❌ Authentication failed: {e}")
            import traceback
            st.code(traceback.format_exc())
    else:
        # Start OAuth flow
        if st.button("🔐 Sign In with Google", type="primary"):
            # Build authorization URL with proper encoding
            from urllib.parse import urlencode

            auth_params = {
                'client_id': GOOGLE_CLIENT_ID,
                'redirect_uri': REDIRECT_URI,
                'scope': 'openid email profile',
                'response_type': 'code',
                'access_type': 'offline',
                'prompt': 'consent'
            }

            auth_url = f"{AUTH_URL}?{urlencode(auth_params)}"
            st.write(f"**Authorization URL:** {auth_url}")
            st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)
            st.stop()


def render_sign_in_page():
    """Render the sign-in page for users."""
    st.title("🚀 Enable Cloud Sync")
    st.markdown("Sign in with Google to backup your settings and sync across devices.")

    st.markdown("---")
    st.markdown("### Benefits of Cloud Sync:")
    st.markdown("✅ **Backup your API keys** securely in the cloud")
    st.markdown("✅ **Access your settings** on any device")
    st.markdown("✅ **Never lose your configuration**")
    st.markdown("✅ **Secure encryption** protects your data")

    st.markdown("---")

    # Check if Google OAuth is configured
    if not GOOGLE_CLIENT_ID or not GOOGLE_CLIENT_SECRET:
        st.warning("⚠️ Google OAuth is not configured. Using demo authentication instead.")

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔐 Try Demo Sign In", use_container_width=True, type="primary"):
                st.session_state.page = "auth_handler"
                st.rerun()

            if st.button("❌ Continue as Guest", use_container_width=True):
                st.session_state.page = "main"
                st.rerun()
    else:
        # Real Google OAuth
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            if st.button("🔐 Sign In with Google", use_container_width=True, type="primary"):
                st.session_state.page = "auth_handler"
                st.rerun()

            if st.button("❌ Continue as Guest", use_container_width=True):
                st.session_state.page = "main"
                st.rerun()

    st.markdown("---")
    st.caption("🔒 Your privacy is protected. We only store what you choose to save.")


def render_user_profile():
    """Render user profile information in sidebar."""
    if is_signed_in():
        user = get_current_user()
        if user:
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 👤 Account")

            # User info
            email = user.get('email', 'Unknown')
            name = user.get('display_name', email.split('@')[0])

            # Show profile picture if available
            photo_url = user.get('photo_url')
            if photo_url:
                st.sidebar.image(photo_url, width=50, caption=name)
            else:
                st.sidebar.markdown(f"**{name}**")

            st.sidebar.markdown(f"*{email}*")

            # Sign out button
            if st.sidebar.button("🚪 Sign Out", key="sidebar_signout"):
                from firebase_manager import sign_out
                sign_out()
                st.sidebar.success("✅ Signed out successfully")
                st.rerun()
        else:
            st.sidebar.markdown("---")
            st.sidebar.markdown("### 👤 Account")
            st.sidebar.markdown("*User data not available*")
    else:
        # Show sign-in option
        st.sidebar.markdown("---")
        st.sidebar.markdown("### 👤 Account")
        if st.sidebar.button("🔐 Sign In", key="sidebar_signin_profile", help="Sign in with Google to enable cloud sync"):
            st.session_state.page = "auth_handler"
            st.rerun()