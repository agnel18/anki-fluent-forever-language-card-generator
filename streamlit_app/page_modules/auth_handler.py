# auth_handler.py - Firebase Authentication

import streamlit as st
import streamlit.components.v1 as components
from streamlit_firebase_auth import login

# Local auth functions for backward compatibility
def is_signed_in():
    """Check if user is authenticated."""
    return st.session_state.get("user") is not None

def get_current_user():
    """Get current authenticated user info."""
    return st.session_state.get("user")

def sign_out():
    """Sign out user."""
    st.session_state.user = None

# Firebase configuration
FIREBASE_API_KEY = st.secrets.get("FIREBASE_WEB_API_KEY", "")
FIREBASE_PROJECT_ID = st.secrets.get("FIREBASE_PROJECT_ID", "")

def get_firebase_config():
    """Get Firebase configuration from secrets."""
    return {
        "apiKey": FIREBASE_API_KEY,
        "authDomain": f"{FIREBASE_PROJECT_ID}.firebaseapp.com",
        "projectId": FIREBASE_PROJECT_ID,
        "storageBucket": f"{FIREBASE_PROJECT_ID}.firebasestorage.app",
        "appId": "1:144901974646:web:5f677d6632d5b79f2c4d57"
    }

def firebase_auth_component():
    """Render the authentication component."""
    if not is_signed_in():
        # User not logged in - show login button
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔐 Sign In with Google", type="primary", use_container_width=True, key="auth_component_signin_main"):
                st.session_state.page = "auth_handler"
                st.rerun()
        with col2:
            st.info("Optional - Guest mode available")
        return None
    else:
        # User is logged in - show logout option
        user_info = get_current_user()
        return user_info

def get_firebase_config():
    """Get Firebase configuration from secrets."""
    firebase_config = {
        "apiKey": FIREBASE_API_KEY,
        "authDomain": f"{FIREBASE_PROJECT_ID}.firebaseapp.com",
        "projectId": FIREBASE_PROJECT_ID,
        "storageBucket": f"{FIREBASE_PROJECT_ID}.firebasestorage.app",
        "messagingSenderId": "144901974646",
        "appId": "1:144901974646:web:5f677d6632d5b79f2c4d57"
    }
    return firebase_config if FIREBASE_API_KEY and FIREBASE_PROJECT_ID else None

def render_auth_handler_page():
    """Handle authentication using Firebase."""
    st.title("🔐 Sign In with Google")
    st.markdown("Connect your Google account to save progress across devices!")

    user = login()
    if user:
        st.session_state.user = user
        st.session_state.page = "main"
        st.rerun()
    else:
        st.markdown("---")
        st.markdown("**Why sign in?**")
        st.markdown("✅ Save your progress across devices")
        st.markdown("✅ Backup your API keys securely")
        st.markdown("✅ Access advanced statistics")
        st.markdown("✅ Never lose your learning data")

        # Instructions
        st.markdown("---")
        st.markdown("### 📋 How to Sign In")
        st.markdown("1. Click 'Sign In with Google' above")
        st.markdown("2. Choose your Google account in the popup")
        st.markdown("3. Grant permission to access your basic Google profile")
        st.markdown("4. Your data will be securely synced to the cloud!")

        # Privacy notice
        st.markdown("---")
        st.markdown("### 🔒 Privacy & Security")
        st.markdown("• We only access your basic Google profile (name, email, photo)")
        st.markdown("• Your data is encrypted and stored securely")
        st.markdown("• You can delete your account and data anytime")
        st.markdown("• [Privacy Policy](https://agnel18.github.io/anki-fluent-forever-language-card-generator/privacy-policy.html)")

def render_user_profile():
    """Render user profile section in sidebar."""
    if is_signed_in():
        user = get_current_user()
        if user:
            # Display user info
            col1, col2 = st.columns([1, 3])
            with col1:
                if user.get('photoURL'):
                    st.image(user['photoURL'], width=40)
                else:
                    st.markdown("👤")
            with col2:
                st.markdown(f"**{user.get('displayName', 'User')}**")
                st.caption(user.get('email', ''))

            # Sign out button
            if st.button("🚪 Sign Out", key="sign_out_sidebar", use_container_width=True):
                sign_out()
                st.rerun()
        else:
            st.error("User data not available")
    else:
        # Show sign-in option
        st.markdown("### ☁️ Cloud Sync")
        st.markdown("Save progress across devices!")

        if st.button("🔐 Sign In", key="sign_in_sidebar", use_container_width=True):
            st.session_state.page = "auth_handler"
            st.rerun()

        st.caption("Optional - Guest mode available")
