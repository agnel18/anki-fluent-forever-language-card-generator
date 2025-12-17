# auth_handler.py - OAuth authentication handler page

import streamlit as st
from firebase_manager import sign_in_with_google, sign_out
import time

def render_auth_handler_page():
    """Handle OAuth callback and user setup."""
    st.title("🔐 Signing You In...")
    st.markdown("Please wait while we set up your account...")

    # Show loading spinner
    with st.spinner("Authenticating with Google..."):
        try:
            # For now, this is a placeholder - actual OAuth implementation needed
            # In a real implementation, this would handle the OAuth callback
            
            # Simulate authentication process
            time.sleep(2)
            
            # Mock successful authentication (replace with real OAuth)
            st.session_state.user = {
                'email': 'user@example.com',  # Would come from OAuth
                'uid': 'mock_user_id',       # Would come from OAuth
                'display_name': 'User'       # Would come from OAuth
            }
            st.session_state.is_guest = False
            
            # Load cloud data
            from sync_manager import load_cloud_data
            load_cloud_data()
            
            st.success("✅ Successfully signed in!")
            st.info("Your settings will now sync across devices.")
            
            # Auto-redirect after success
            time.sleep(2)
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
            # Trigger OAuth flow
            st.session_state.page = "auth_handler"
            st.rerun()
            
        if st.button("❌ Continue as Guest", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()
    
    st.markdown("---")
    st.caption("🔒 Your privacy is protected. We only store what you choose to save.")