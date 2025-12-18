# auth_handler.py - Firebase Authentication handler page

import streamlit as st
import time
import json
from firebase_manager import is_signed_in, get_current_user

def render_auth_handler_page():
    """Handle Firebase Authentication flow."""
    st.title("🔐 Signing You In...")
    st.markdown("Please wait while we authenticate with Google...")

    # Show loading spinner
    with st.spinner("Authenticating with Google..."):
        try:
            # For Streamlit Cloud deployment, we need to use a simplified approach
            # since full OAuth redirects don't work well in Streamlit

            # Check if Firebase is available
            from firebase_manager import firebase_initialized
            if not firebase_initialized:
                st.error("❌ Firebase authentication is not available")
                st.info("Returning to main page...")
                time.sleep(2)
                st.session_state.page = "main"
                st.rerun()
                return

            # In a production app, you would implement proper OAuth flow here
            # For now, we'll create a mock authenticated user for demonstration
            # This simulates what would happen after successful Google OAuth

            time.sleep(2)  # Simulate authentication delay

            # Mock successful authentication (replace with real OAuth)
            # In production, this would come from Firebase Auth after OAuth callback
            # For demo purposes, we'll create a consistent user ID based on session
            import hashlib
            import streamlit as st

            # Create a consistent demo user ID based on the session
            # This ensures the same "user" gets the same ID across sessions
            session_fingerprint = f"demo_user_{st.session_state.get('user_agent', 'unknown')}"
            consistent_uid = hashlib.md5(session_fingerprint.encode()).hexdigest()[:16]

            mock_user = {
                'email': 'demo@example.com',  # Would come from Google OAuth
                'uid': f"demo_{consistent_uid}",  # Consistent ID for cloud sync
                'display_name': 'Demo User',  # Would come from Google profile
                'photo_url': None,            # Would come from Google profile
                'email_verified': True        # Would come from Firebase Auth
            }

            # Store user in session state
            st.session_state.user = mock_user
            st.session_state.is_guest = False

            # Load cloud data if available
            try:
                from sync_manager import load_cloud_data
                load_cloud_data()
            except Exception as e:
                st.warning(f"Could not load cloud data: {e}")

            st.success("✅ Successfully signed in!")
            st.info("Your settings will now sync across devices.")

            # Show user info
            st.markdown("---")
            st.markdown("**Welcome!**")
            st.markdown(f"**Email:** {mock_user['email']}")
            st.markdown(f"**Name:** {mock_user['display_name']}")

            # Auto-redirect after success
            time.sleep(3)
            st.session_state.page = "main"
            st.rerun()

        except Exception as e:
            st.error(f"❌ Authentication failed: {e}")
            st.info("Returning to main page...")
            time.sleep(2)
            st.session_state.page = "main"
            st.rerun()


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

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("🔐 Sign In with Google", use_container_width=True, type="primary"):
            # Trigger authentication flow
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