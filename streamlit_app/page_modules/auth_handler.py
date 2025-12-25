# auth_handler.py - Firebase Authentication using httpx-oauth

import streamlit as st
import firebase_admin
from firebase_admin import auth, exceptions, credentials, initialize_app
import asyncio
from httpx_oauth.clients.google import GoogleOAuth2
import jwt
from typing import Optional
import streamlit.components.v1 as components

# Initialize Firebase Admin
try:
    firebase_admin.get_app()
except ValueError:
    # Initialize with your Firebase config
    cred = credentials.Certificate({
        "type": "service_account",
        "project_id": st.secrets.get("FIREBASE_PROJECT_ID", ""),
        "private_key_id": st.secrets.get("FIREBASE_PRIVATE_KEY_ID", ""),
        "private_key": st.secrets.get("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n"),
        "client_email": st.secrets.get("FIREBASE_CLIENT_EMAIL", ""),
        "client_id": st.secrets.get("FIREBASE_CLIENT_ID", ""),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
        "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{st.secrets.get('FIREBASE_CLIENT_EMAIL', '')}"
    })
    initialize_app(cred)

# Initialize Google OAuth2 client
client_id = st.secrets.get("GOOGLE_CLIENT_ID", "")
client_secret = st.secrets.get("GOOGLE_CLIENT_SECRET", "")
redirect_url = st.secrets.get("GOOGLE_REDIRECT_URL", "")

print(f"DEBUG: OAuth client_id: {client_id[:20]}..." if client_id else "DEBUG: No client_id")
print(f"DEBUG: OAuth client_secret: {'***' + client_secret[-4:] if client_secret else 'No client_secret'}")
print(f"DEBUG: OAuth redirect_url: {redirect_url}")

if client_id and client_secret and redirect_url:
    client = GoogleOAuth2(client_id=client_id, client_secret=client_secret)
    print("DEBUG: OAuth client initialized successfully")
else:
    client = None
    print("DEBUG: OAuth client not initialized - missing credentials")

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

def decode_user(token: str):
    """Decode JWT token to get user info."""
    decoded_data = jwt.decode(jwt=token, options={"verify_signature": False})
    return decoded_data

async def get_authorization_url(client: GoogleOAuth2, redirect_url: str) -> str:
    """Get Google OAuth authorization URL."""
    # Ensure no trailing spaces in redirect_url
    clean_redirect = redirect_url.strip()
    
    authorization_url = await client.get_authorization_url(
        clean_redirect,
        scope=["openid", "email", "profile"],
        # prompt="select_account" forces the account chooser to work properly
        extras_params={"access_type": "offline", "prompt": "select_account"},
    )
    return authorization_url

async def get_access_token(client: GoogleOAuth2, redirect_url: str, code: str):
    """Exchange authorization code for access token."""
    print(f"DEBUG: get_access_token called with redirect_url: {redirect_url}")
    print(f"DEBUG: Code length: {len(code) if code else 0}")
    try:
        token = await client.get_access_token(code, redirect_url)
        print("DEBUG: Token exchange successful")
        return token
    except Exception as e:
        print(f"DEBUG: Token exchange exception: {e}")
        print(f"DEBUG: Exception type: {type(e)}")
        raise

def get_access_token_from_query_params(client: GoogleOAuth2, redirect_url: str):
    """Get access token from URL query parameters."""
    print("DEBUG: get_access_token_from_query_params called")
    query_params = st.query_params
    print(f"DEBUG: Query params: {query_params}")
    if "code" in query_params:
        code = query_params["code"]
        print(f"DEBUG: Authorization code found: {code[:20]}...")
        print(f"DEBUG: Redirect URL: {redirect_url}")
        try:
            # More robust async handling for Streamlit
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            token = loop.run_until_complete(get_access_token(client, redirect_url, code))
            
            st.query_params.clear()
            return token
        except Exception as e:
            st.error(f"Authentication Error: {e}")
            return None
    else:
        print("DEBUG: No authorization code in query params")
    return None

def markdown_button(url: str, text: Optional[str] = None, color="#4285f4", sidebar: bool = True):
    """Create a styled HTML button for OAuth."""
    markdown = st.sidebar.markdown if sidebar else st.markdown
    markdown(
        f"""
        <a href="{url}" target="_top">
            <div style="
                display: inline-flex;
                align-items: center;
                justify-content: center;
                font-weight: 400;
                padding: 0.5rem 1rem;
                border-radius: 0.25rem;
                margin: 0px;
                margin-bottom: 2px;
                line-height: 1.6;
                width: auto;
                user-select: none;
                background-color: {color};
                color: rgb(255, 255, 255);
                border: 1px solid {color};
                text-decoration: none;
                text-align: center;
                cursor: pointer;
                font-size: 16px;
            ">
                🔐 {text}
            </div>
        </a>
        """,
        unsafe_allow_html=True,
    )

def show_login_button(text: Optional[str] = "Sign In with Google", color="#4285f4", sidebar: bool = True):
    """Show the Google sign-in button."""
    if client and not is_signed_in():
        # Handle async URL generation
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        authorization_url = loop.run_until_complete(get_authorization_url(client, redirect_url))
        
        markdown_button(authorization_url, text, color, sidebar)

def handle_auth_callback():
    """Handle OAuth callback from URL parameters."""
    print("DEBUG: handle_auth_callback called")
    if client:
        print("DEBUG: OAuth client is available")
        try:
            print("DEBUG: Calling get_access_token_from_query_params")
            token = get_access_token_from_query_params(client, redirect_url)
            print(f"DEBUG: Token received: {token is not None}")
            if token and "id_token" in token:
                print("DEBUG: Decoding user token")
                user_info = decode_user(token=token["id_token"])
                print(f"DEBUG: User info decoded: {user_info is not None}")
                if user_info and "email" in user_info:
                    print(f"DEBUG: User email: {user_info['email']}")
                    # Create or get Firebase user
                    try:
                        user = auth.get_user_by_email(user_info["email"])
                        print("DEBUG: Existing Firebase user found")
                    except exceptions.FirebaseError:
                        user = auth.create_user(email=user_info["email"])
                        print("DEBUG: New Firebase user created")

                    # Store user info in session
                    st.session_state.user = {
                        "uid": user.uid,
                        "email": user_info["email"],
                        "displayName": user_info.get("name", user_info["email"]),
                        "photoURL": user_info.get("picture", ""),
                    }
                    st.session_state.is_guest = False
                    print("DEBUG: User session updated, rerunning")
                    st.rerun()
                else:
                    print("DEBUG: No email in user info")
            else:
                print("DEBUG: No valid token or id_token")
        except Exception as e:
            print(f"DEBUG: Authentication failed with error: {e}")
            st.error(f"Authentication failed: {e}")
    else:
        print("DEBUG: OAuth client is not available")

def firebase_auth_component():
    """Render the authentication component."""
    if not is_signed_in():
        # User not logged in - show login button
        col1, col2 = st.columns([1, 1])
        with col1:
            show_login_button("Sign In with Google", "#4285f4", sidebar=False)
        with col2:
            st.info("Optional - Guest mode available")
        return None
    else:
        # User is logged in - show logout option
        user_info = get_current_user()
        return user_info

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

def render_auth_handler_page():
    """Handle authentication page."""
    st.title("🔐 Sign In with Google")
    st.markdown("Connect your Google account to save progress across devices!")

    if not is_signed_in():
        show_login_button("Sign In with Google", "#4285f4", sidebar=False)

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
    else:
        st.success("You're already signed in!")
        user = get_current_user()
        st.write(f"Welcome back, {user.get('displayName', 'User')}!")
        if st.button("Go to Main App"):
            st.session_state.page = "main"
            st.rerun()
