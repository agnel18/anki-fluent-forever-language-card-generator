# auth_handler.py - Streamlit OIDC Authentication with Google

import streamlit as st

# Session state guard for Streamlit bug workaround
if not hasattr(st, "session_state") or st.session_state is None:
    st.session_state = {}
import streamlit.components.v1 as components

# Local auth functions for backward compatibility

def is_signed_in():
    """Check if user is authenticated using Streamlit's built-in auth."""
    return hasattr(st, "user") and hasattr(st.user, "is_logged_in") and st.user.is_logged_in


def get_current_user():
    """Get current authenticated user info using Streamlit's built-in auth."""
    if is_signed_in():
        return {
            'uid': getattr(st.user, 'email', None),
            'email': getattr(st.user, 'email', None),
            'displayName': getattr(st.user, 'name', getattr(st.user, 'email', 'User')),
            'photoURL': getattr(st.user, 'picture', None)
        }
    return None

def sign_out():
    """Sign out user using Streamlit's built-in auth."""
    st.logout()

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
    """Render the authentication component using Streamlit's built-in OIDC."""
    if not is_signed_in():
        # User not logged in - show login button
        page_id = st.session_state.get('page', 'main')
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔐 Sign In with Google", type="primary", use_container_width=True, key=f"auth_component_signin_{page_id}"):
                st.login("google")
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
    """Handle authentication using Streamlit's built-in OIDC."""
    st.title("ðŸ” Sign In with Google")
    st.markdown("Connect your Google account to save progress across devices!")

    if not is_signed_in():
        # User not logged in - show login button
        col1, col2 = st.columns([1, 1])
        with col1:
            if st.button("🔐 Sign In with Google", type="primary", use_container_width=True, key="auth_page_signin"):
                st.login()
        with col2:
            st.info("Optional - Guest mode available")

        st.markdown("---")
        st.markdown("**Why sign in?**")
        st.markdown("âœ… Save your progress across devices")
        st.markdown("âœ… Backup your API keys securely")
        st.markdown("âœ… Access advanced statistics")
        st.markdown("âœ… Never lose your learning data")

        # Instructions
        st.markdown("---")
        st.markdown("### ðŸ“‹ How to Sign In")
        st.markdown("1. Click 'Sign In with Google' above")
        st.markdown("2. Choose your Google account in the popup")
        st.markdown("3. Grant permission to access your basic Google profile")
        st.markdown("4. Your data will be securely synced to the cloud!")

        # Privacy notice
        st.markdown("---")
        st.markdown("### ðŸ”’ Privacy & Security")
        st.markdown("â€¢ We only access your basic Google profile (name, email, photo)")
        st.markdown("â€¢ Your data is encrypted and stored securely")
        st.markdown("â€¢ You can delete your account and data anytime")
        st.markdown("â€¢ [Privacy Policy](https://agnel18.github.io/anki-fluent-forever-language-card-generator/privacy-policy.html)")
    else:
        # User is logged in
        user = get_current_user()
        if user:
            st.success(f"âœ… Signed in as {user.get('displayName', user.get('email', 'User'))}")

            # Show user info
            col1, col2 = st.columns([1, 3])
            with col1:
                if user.get('photoURL'):
                    st.image(user['photoURL'], width=60)
                else:
                    st.markdown("ðŸ‘¤")
            with col2:
                st.markdown(f"**{user.get('displayName', 'User')}**")
                st.markdown(f"*{user.get('email', '')}*")

            st.markdown("---")

            if st.button("ðŸšª Sign Out", use_container_width=True):
                st.logout()

            # Migration status (if applicable)
            if st.session_state.get('data_migrated', False):
                st.info("âœ… Your data has been migrated to the cloud!")
            else:
                st.info("â˜ï¸ Your data is automatically synced to the cloud!")

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
                    st.markdown("ðŸ‘¤")
            with col2:
                st.markdown(f"**{user.get('displayName', 'User')}**")
                st.caption(user.get('email', ''))

            # Sign out button
            if st.button("ðŸšª Sign Out", key="sign_out_sidebar", use_container_width=True):
                sign_out()
                st.rerun()
        else:
            st.error("User data not available")
    else:
        # Show sign-in option
        st.markdown("### â˜ï¸ Cloud Sync")
        st.markdown("Save progress across devices!")

        if st.button("ðŸ” Sign In", key="sign_in_sidebar", use_container_width=True):
            st.session_state.page = "auth_handler"
            st.rerun()

        st.caption("Optional - Guest mode available")
