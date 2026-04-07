# pages/main.py - Main overview page for the language learning app
# Updated import to fix module path issues

import streamlit as st
import os
import json

def render_main_page():
    """Render the main overview page with introduction and start button."""

    # Header
    col_logo, col_title = st.columns([0.3, 1])
    with col_logo:
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo.svg")
        if os.path.exists(logo_path):
            st.image(logo_path, width=200)
        else:
            st.markdown("🧠")
    with col_title:
        st.markdown("# Language Anki Deck Generator")
        st.markdown("*Create personalized Anki decks for language learning with AI-generated sentences and images.*")

    st.markdown("---")



    # Features overview - moved before How It Works
    with st.container():
        st.markdown("## 🌟 Features")

        col1, col2 = st.columns(2, gap="large")

        with col1:
            st.markdown("""
            **📊 Smart Word Selection**
            - Frequency-based word lists for natural learning
            - Custom word uploads for specialized vocabulary
            - 77 languages supported

            **🤖 AI-Powered Generation**
            - Natural sentence creation with context
            - Contextual image matching for visual learning
            - Multiple audio voices for pronunciation
            """)

        with col2:
            st.markdown("""
            **🎵 Audio Support**
            - Multiple language voices for authenticity
            - Adjustable speed for learning pace
            - Native pronunciation practice

            **🎨 Grammar Coloring**
            - Color-coded grammar overlays on sentences
            - 11 language-specific grammar analyzers
            - Word-by-word explanations
            """)

    st.markdown("---")

    # Check for missing API keys and show consolidated warning
    missing_keys = []
    google_key = st.session_state.get("google_api_key") or os.environ.get("GOOGLE_API_KEY", "")

    if not google_key:
        missing_keys.append("Google Cloud APIs")

    # Check for Pixabay API key (required for image generation)
    pixabay_key = st.session_state.get("pixabay_api_key", "")
    if not pixabay_key:
        missing_keys.append("Pixabay Images")

    if missing_keys:
        st.warning(f"⚠️ **API Keys Required**: {', '.join(missing_keys)} API key(s) not configured. You'll be redirected to set them up.")
    else:
        st.success("✅ All API keys configured! Ready to generate decks.")

    # Quick start section - moved to bottom, left-aligned with bigger button
    with st.container():

        # Add custom CSS class for enhanced styling
        st.markdown("""
        <style>
        .primary-action-button button {
            animation: pulse-glow 2s infinite;
        }
        @keyframes pulse-glow {
            0%, 100% { box-shadow: 0 4px 12px rgba(0,0,0,0.15); }
            50% { box-shadow: 0 4px 20px rgba(0,0,0,0.25); }
        }
        </style>
        """, unsafe_allow_html=True)

        # Wrap button in container with custom class
        st.markdown('<div class="primary-action-button">', unsafe_allow_html=True)
        
        # Define button text and help text
        has_google_api_key = bool(st.session_state.get("google_api_key"))
            
        # Check Pixabay API key
        has_pixabay_key = bool(st.session_state.get("pixabay_api_key", ""))
            
        has_all_api_keys = has_google_api_key and has_pixabay_key
        button_text = "🚀 Start Creating Your Deck" if not has_all_api_keys else "🚀 Continue Creating Your Deck"
        help_text = "Begin the 5-step deck creation process" if not has_all_api_keys else "Continue with your saved API keys"
        
        if st.button(button_text, type="primary", help=help_text, use_container_width=True):
            # Add brief loading animation
            with st.spinner("🚀 Getting started..."):
                import time
                time.sleep(0.3)  # Brief pause for visual feedback
            if has_all_api_keys:
                st.session_state.page = "language_select"
            else:
                st.session_state.page = "api_setup"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # Scroll to top after all content is rendered
    st.markdown("""
    <script>
        setTimeout(function() {
            window.scrollTo({top: 0, behavior: 'smooth'});
        }, 1000);
    </script>
    """, unsafe_allow_html=True)