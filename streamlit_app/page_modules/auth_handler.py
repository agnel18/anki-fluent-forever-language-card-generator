# auth_handler.py - Firebase Email/Password Authentication UI

import streamlit as st
from typing import Optional, Dict, Any
import streamlit.components.v1 as components
import re
import time
import sys
import os

# Add the parent directory to the path so we can import services
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

# Import authentication services
from services.auth.auth_service import AuthService
from services.auth.email_service import EmailService
from services.auth.session_manager import SessionManager

# Initialize services
email_service = EmailService()
session_manager = SessionManager()
auth_service = AuthService(email_service, session_manager)

# Firebase Auth JavaScript component for client-side authentication
def firebase_auth_component():
    """Firebase Auth component using JavaScript SDK."""
    # Check if secrets are available, otherwise use empty defaults
    try:
        # Try to access secrets to see if they exist
        firebase_api_key = st.secrets.get("firebase", {}).get("api_key", "")
        firebase_auth_domain = st.secrets.get("firebase", {}).get("auth_domain", "")
        firebase_project_id = st.secrets.get("firebase", {}).get("project_id", "")

        # Only use Firebase if we have the minimum required config
        if firebase_api_key and firebase_auth_domain and firebase_project_id:
            firebase_config = {
                "apiKey": firebase_api_key,
                "authDomain": firebase_auth_domain,
                "projectId": firebase_project_id,
                "storageBucket": st.secrets.get("firebase", {}).get("storage_bucket", ""),
                "messagingSenderId": st.secrets.get("firebase", {}).get("messaging_sender_id", ""),
                "appId": st.secrets.get("firebase", {}).get("app_id", "")
            }
            firebase_enabled = True
        else:
            firebase_config = {}
            firebase_enabled = False
    except Exception:
        # No secrets available, disable Firebase
        firebase_config = {}
        firebase_enabled = False

    # JavaScript code for Firebase Auth with email verification
    if firebase_enabled:
        auth_js = f"""
        <script type="module">
            import {{ initializeApp }} from 'https://www.gstatic.com/firebasejs/9.22.0/firebase-app.js';
            import {{ getAuth, signInWithEmailAndPassword, createUserWithEmailAndPassword, signOut, onAuthStateChanged, sendEmailVerification, reload, sendPasswordResetEmail }} from 'https://www.gstatic.com/firebasejs/9.22.0/firebase-auth.js';

            const firebaseConfig = {firebase_config};
            const app = initializeApp(firebaseConfig);
            const auth = getAuth(app);

            window.firebaseAuth = {{
                login: async (email, password) => {{
                    try {{
                        const userCredential = await signInWithEmailAndPassword(auth, email, password);
                        const user = userCredential.user;

                        // Check if email is verified
                        if (!user.emailVerified) {{
                            return {{
                                success: false,
                                error: "Please verify your email address before signing in. Check your inbox for the verification link.",
                                needsVerification: true,
                                user: {{
                                    uid: user.uid,
                                    email: user.email,
                                    displayName: user.displayName || user.email.split('@')[0],
                                    emailVerified: false
                                }}
                            }};
                        }}

                        return {{
                            success: true,
                            user: {{
                                uid: user.uid,
                                email: user.email,
                                displayName: user.displayName || user.email.split('@')[0],
                                emailVerified: user.emailVerified
                            }}
                        }};
                    }} catch (error) {{
                        return {{ success: false, error: error.message }};
                    }}
                }},
                register: async (email, password, displayName) => {{
                    try {{
                        const userCredential = await createUserWithEmailAndPassword(auth, email, password);
                        const user = userCredential.user;

                        // Update display name if provided
                        if (displayName) {{
                            await user.updateProfile({{ displayName: displayName }});
                        }}

                        // Send email verification
                        await sendEmailVerification(user);

                    return {{
                        success: true,
                        user: {{
                            uid: user.uid,
                            email: user.email,
                            displayName: user.displayName || user.email.split('@')[0],
                            emailVerified: false
                        }},
                        message: "Account created successfully! Please check your email and click the verification link before signing in."
                    }};
                }} catch (error) {{
                    return {{ success: false, error: error.message }};
                }}
            }},
            resendVerification: async () => {{
                try {{
                    const user = auth.currentUser;
                    if (user) {{
                        await sendEmailVerification(user);
                        return {{ success: true, message: "Verification email sent! Please check your inbox." }};
                    }} else {{
                        return {{ success: false, error: "No user signed in" }};
                    }}
                }} catch (error) {{
                    return {{ success: false, error: error.message }};
                }}
            }},
            logout: async () => {{
                try {{
                    await signOut(auth);
                    return {{ success: true }};
                }} catch (error) {{
                    return {{ success: false, error: error.message }};
                }}
            }},
            resetPassword: async (email) => {{
                try {{
                    await sendPasswordResetEmail(auth, email);
                    return {{ success: true, message: "Password reset email sent! Check your inbox." }};
                }} catch (error) {{
                    return {{ success: false, error: error.message }};
                }}
            }},
            checkEmailVerified: async () => {{
                try {{
                    const user = auth.currentUser;
                    if (user) {{
                        await reload(user);
                        return {{
                            emailVerified: user.emailVerified,
                            user: {{
                                uid: user.uid,
                                email: user.email,
                                displayName: user.displayName || user.email.split('@')[0]
                            }}
                        }};
                    }}
                    return {{ emailVerified: false }};
                }} catch (error) {{
                    return {{ success: false, error: error.message }};
                }}
            }},
            onAuthStateChanged: (callback) => {{
                onAuthStateChanged(auth, callback);
            }}
        }};
    </script>
    """
    else:
        # Firebase disabled - provide mock functions that return appropriate errors
        auth_js = """
        <script type="module">
            window.firebaseAuth = {
                login: async (email, password) => {
                    return { success: false, error: "Firebase authentication is not configured. Please contact support." };
                },
                register: async (email, password, displayName) => {
                    return { success: false, error: "Firebase authentication is not configured. Please contact support." };
                },
                resendVerification: async () => {
                    return { success: false, error: "Firebase authentication is not configured." };
                },
                logout: async () => {
                    return { success: false, error: "Firebase authentication is not configured." };
                },
                resetPassword: async (email) => {
                    return { success: false, error: "Firebase authentication is not configured." };
                },
                checkEmailVerified: async () => {
                    return { emailVerified: false };
                },
                onAuthStateChanged: (callback) => {
                    // Do nothing - no auth state changes
                }
            };
        </script>
        """

    components.html(auth_js, height=0)

# Local auth functions
def is_signed_in():
    """Check if user is authenticated."""
    return session_manager.is_signed_in()

def get_current_user():
    """Get current authenticated user info."""
    return session_manager.get_current_user()

def sign_out():
    """Sign out user."""
    session_manager.sign_out()

def validate_email(email: str) -> bool:
    """Validate email format."""
    return auth_service.validate_email(email)

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    return auth_service.validate_password(password)

def create_user_profile(uid: str, email: str, display_name: str = None):
    """Create user profile in Firestore."""
    auth_service.create_user_profile(uid, email, display_name)

def update_user_last_login(uid: str):
    """Update user's last login timestamp."""
    auth_service.update_user_last_login(uid)

def get_user_profile(uid: str) -> Dict[str, Any]:
    """Get user profile from Firestore."""
    return auth_service.get_user_profile(uid)

def save_user_api_keys(uid: str, api_keys: Dict[str, str]):
    """Save encrypted API keys to Firestore."""
    auth_service.save_user_api_keys(uid, api_keys)

def get_user_api_keys(uid: str) -> Dict[str, str]:
    """Get user's API keys from Firestore."""
    return auth_service.get_user_api_keys(uid)

def save_user_progress(uid: str, language: str, progress_data: Dict[str, Any]):
    """Save user progress to Firestore."""
    auth_service.save_user_progress(uid, language, progress_data)

def get_user_progress(uid: str, language: str) -> Dict[str, Any]:
    """Get user progress from Firestore."""
    return auth_service.get_user_progress(uid, language)

def save_user_preferences(uid: str, preferences: Dict[str, Any]):
    """Save user preferences to Firestore."""
    auth_service.save_user_preferences(uid, preferences)

def get_user_preferences(uid: str) -> Dict[str, Any]:
    """Get user preferences from Firestore."""
    return auth_service.get_user_preferences(uid)

# Local auth functions
def is_signed_in():
    """Check if user is authenticated."""
    return session_manager.is_signed_in()

def get_current_user():
    """Get current authenticated user info."""
    return session_manager.get_current_user()

def sign_out():
    """Sign out user."""
    session_manager.sign_out()

def validate_email(email: str) -> bool:
    """Validate email format."""
    return auth_service.validate_email(email)

def validate_password(password: str) -> tuple[bool, str]:
    """Validate password strength."""
    return auth_service.validate_password(password)

# UI Components
def login_form():
    """Display login form."""
    st.subheader("🔐 Sign In")

    # Add enhanced button styling
    st.markdown("""
    <style>
    .auth-button-primary button {
        background: linear-gradient(135deg, #238636 0%, #2ea043 100%) !important;
    }
    .auth-button-secondary button {
        border: 2px solid #0969da !important;
        background-color: transparent !important;
        color: #0969da !important;
    }
    .auth-button-secondary button:hover {
        background-color: #0969da !important;
        color: white !important;
    }
    </style>
    """, unsafe_allow_html=True)

    # Check if we need to show verification options (set from previous login attempt)
    if session_manager.should_show_verification_options():
        _show_verification_options()
        return

    with st.form("login_form"):
        # Email field with label
        st.markdown("**📧 Email Address**")
        email = st.text_input("Enter your email address", key="login_email", help="Enter the email you used to create your account")

        # Password field with label
        st.markdown("**🔒 Password**")
        password = st.text_input("Enter your password", type="password", key="login_password", help="Your account password")

        # Enhanced Sign In button
        st.markdown('<div class="auth-button-primary">', unsafe_allow_html=True)
        submitted = st.form_submit_button("🔓 Sign In", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if submitted:
            if not email or not password:
                st.error("Please fill in all fields")
                return

            if not validate_email(email):
                st.error("Please enter a valid email address")
                return

            # Show loading spinner
            with st.spinner("Signing you in..."):
                success, message, user_data = auth_service.authenticate_user(email, password)

                if success:
                    st.success(message)
                    st.rerun()
                else:
                    if "verify your email" in message.lower():
                        # Set flag to show verification options
                        session_manager.set_verification_options(email)
                        st.rerun()
                    else:
                        st.error(message)

def _show_verification_options():
    """Show email verification options outside the form."""
    email = session_manager.get_verification_email()

    st.subheader("📧 Email Verification Required")
    st.info(f"Please verify your email address: **{email}**")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📧 Resend Verification Email", key="resend_verification"):
            success, message = auth_service.resend_verification_email(email)
            if success:
                st.success(message)
            else:
                st.error(message)

    with col2:
        if st.button("🔄 Check Verification Status", key="check_verification"):
            is_verified, message = auth_service.check_email_verification_status(email)
            if is_verified:
                st.success(message)
                session_manager.clear_verification_options()
                st.rerun()
            else:
                st.warning(message)

    with col3:
        if st.button("⬅️ Back to Sign In", key="back_to_login"):
            session_manager.clear_verification_options()
            st.rerun()

def registration_form():
    """Display registration form."""
    st.subheader("📝 Create Account")

    # Debug: Check if Firebase auth is loaded
    st.markdown("""
    <script>
    setTimeout(() => {
        if (window.firebaseAuth) {
            console.log('Firebase Auth loaded successfully');
        } else {
            console.error('Firebase Auth NOT loaded');
        }
    }, 2000);
    </script>
    """, unsafe_allow_html=True)

    with st.form("register_form"):
        # Email field with label
        st.markdown("**📧 Email Address**")
        email = st.text_input("Enter your email address", key="register_email", help="We'll use this to create your account and send important updates")

        # Password field with label and requirements
        st.markdown("**🔒 Password**")
        password = st.text_input("Create a strong password", type="password", key="register_password",
                                help="Must be at least 8 characters with uppercase, lowercase, and numbers")

        # Password requirements shown inline
        with st.expander("💡 Password Requirements", expanded=False):
            st.markdown("""
            Your password must contain:
            - At least 8 characters
            - One uppercase letter (A-Z)
            - One lowercase letter (a-z)
            - One number (0-9)
            """)

        # Confirm password field
        st.markdown("**🔄 Confirm Password**")
        confirm_password = st.text_input("Re-enter your password", type="password", key="confirm_password",
                                       help="Enter the same password again to confirm")

        # Display name field
        st.markdown("**👤 Display Name** *(optional)*")
        display_name = st.text_input("Choose a display name", key="display_name",
                                   help="This will be shown in your profile. If left blank, we'll use your email username")

        # Enhanced Create Account button
        st.markdown('<div class="auth-button-primary">', unsafe_allow_html=True)
        submitted = st.form_submit_button("🚀 Create Account", use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if submitted:
            if not email or not password:
                st.error("Please fill in email and password")
                return

            if password != confirm_password:
                st.error("Passwords do not match")
                return

            if not validate_email(email):
                st.error("Please enter a valid email address")
                return

            is_valid, msg = validate_password(password)
            if not is_valid:
                st.error(msg)
                return

            # Show loading spinner
            with st.spinner("Creating your account..."):
                success, message = auth_service.register_user(email, password, display_name or None)

                if success:
                    st.success("✅ Account created successfully!")
                    st.info(message)
                else:
                    st.error(message)

def password_reset_form():
    """Display password reset form."""
    st.subheader("🔑 Reset Password")

    with st.form("reset_form"):
        # Email field with label
        st.markdown("**📧 Account Email**")
        email = st.text_input("Enter your account email", key="reset_email",
                            help="We'll send a password reset link to this email address")

        submitted = st.form_submit_button("📤 Send Reset Email", use_container_width=True)

        if submitted:
            if not email:
                st.error("Please enter your email address")
                return

            if not validate_email(email):
                st.error("Please enter a valid email address")
                return

            # Show loading spinner
            with st.spinner("Sending reset email..."):
                success, message = auth_service.send_password_reset(email)
                if success:
                    st.success(message)
                else:
                    st.error(message)

def show_auth_forms():
    """Display authentication forms with tabs."""
    st.markdown("### Choose an option below:")

    tab1, tab2, tab3 = st.tabs(["🔐 Sign In", "📝 Create Account", "🔑 Reset Password"])

    with tab1:
        login_form()

    with tab2:
        registration_form()

    with tab3:
        password_reset_form()

def firebase_auth_component_legacy():
    """Legacy function for backward compatibility."""
    if not is_signed_in():
        col1, col2 = st.columns([1, 1])
        with col1:
            show_auth_forms()
        with col2:
            st.info("Optional - Guest mode available")
        return None
    else:
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
    if not is_signed_in():
        st.title("🔐 Sign In")
        st.markdown("Create an account or sign in to save progress across devices!")
        st.markdown("📧 **Email verification required** - You'll need to verify your email before you can sign in.")

        show_auth_forms()

        st.markdown("---")

        # Why create an account section
        with st.expander("💡 Why create an account?", expanded=False):
            st.markdown("""
            **🌟 Benefits of having an account:**

            ✅ **Save Progress Across Devices** - Access your learning data from any computer or mobile device

            ✅ **Secure API Key Storage** - Your Google API keys are encrypted and stored safely in the cloud

            ✅ **Advanced Statistics** - Track your learning progress over time with detailed analytics

            ✅ **Never Lose Your Data** - Your generated decks, preferences, and settings are backed up automatically

            ✅ **Personalized Experience** - Your preferences and custom settings sync across all your devices

            **Your privacy matters!** We only store the data you choose to save, and you can delete your account anytime.
            """)

        st.markdown("---")
        st.markdown("**Password Requirements:**")
        st.markdown("• At least 8 characters")
        st.markdown("• One uppercase letter")
        st.markdown("• One lowercase letter")
        st.markdown("• One number")

        # Privacy notice
        st.markdown("---")
        st.markdown("### 🔒 Privacy & Security")
        st.markdown("• Your password is securely hashed and stored")
        st.markdown("• Your data is encrypted and stored securely")
        st.markdown("• Email verification ensures account security")
        st.markdown("• You can delete your account and data anytime")
        st.markdown("• [Privacy Policy](https://agnel18.github.io/anki-fluent-forever-language-card-generator/privacy-policy.html)")
    else:
        st.success("You're already signed in!")
        user = get_current_user()
        st.write(f"Welcome back, {user.get('displayName', 'User')}!")

        # Show user stats
        user_profile = get_user_profile(user['uid'])
        if user_profile:
            col1, col2 = st.columns(2)
            with col1:
                created_at = user_profile.get('createdAt')
                if created_at:
                    # Convert DatetimeWithNanoseconds to readable string
                    if hasattr(created_at, 'strftime'):
                        created_at_str = created_at.strftime('%Y-%m-%d %H:%M')
                    else:
                        created_at_str = str(created_at).split('+')[0]  # Fallback
                    st.metric("Account Created", created_at_str)
                else:
                    st.metric("Account Created", "Unknown")
            with col2:
                last_login = user_profile.get('lastLogin')
                if last_login:
                    # Convert DatetimeWithNanoseconds to readable string
                    if hasattr(last_login, 'strftime'):
                        last_login_str = last_login.strftime('%Y-%m-%d %H:%M')
                    else:
                        last_login_str = str(last_login).split('+')[0]  # Fallback
                    st.metric("Last Login", last_login_str)
                else:
                    st.metric("Last Login", "Unknown")

        if st.button("Go to Main App"):
            st.session_state.page = "main"
            st.rerun()
