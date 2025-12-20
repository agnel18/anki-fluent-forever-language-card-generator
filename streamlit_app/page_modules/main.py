# pages/main.py - Main overview page for the language learning app

import streamlit as st
import os



def render_main_page():
    """Render the main overview page with introduction and start button."""


    # Place logo next to the title using columns with less spacing
    col_logo, col_title = st.columns([0.3, 1])
    with col_logo:
        logo_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logo.svg")
        if os.path.exists(logo_path):
            st.image(logo_path, width=200)
        else:
            st.markdown("🧠")
    with col_title:
        st.markdown("# Language Learning Anki Deck Generator")
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
            - Progress tracking across learning sessions

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

            **📈 Usage Tracking**
            - API call monitoring for cost control
            - Progress statistics and analytics
            - Session-based usage tracking
            """)

    st.markdown("---")

    # Introduction section - moved after Features
    with st.container():
        st.markdown("## 🎯 How It Works")
        st.markdown("This app guides you through a **5-step process** to create custom Anki decks:")

        # Step indicators in a nice layout
        steps = [
            ("📋 Language Selection", "Choose your target language"),
            ("📚 Word Selection", "Pick words from frequency lists or upload your own"),
            ("⚙️ Sentence Settings", "Configure sentence generation parameters"),
            ("✨ Generate", "Create your Anki deck with AI sentences and images"),
            ("📥 Complete", "Download your ready-to-use Anki deck")
        ]

        for i, (title, desc) in enumerate(steps, 1):
            st.markdown(f"**{i}. {title}** - {desc}")

        st.markdown("*Each step is on a separate page so you can focus without confusion.*")
        st.markdown("---")

    # Quick start section - moved to bottom, left-aligned with bigger button
    with st.container():
        # Check if API keys are already set
        has_api_keys = bool(st.session_state.get("groq_api_key") and st.session_state.get("pixabay_api_key"))
        button_text = "🚀 Start Creating Your Deck" if not has_api_keys else "🚀 Continue Creating Your Deck"
        help_text = "Begin the 5-step deck creation process" if not has_api_keys else "Continue with your saved API keys"
        
        if st.button(button_text, type="primary", help=help_text, use_container_width=True):
            # Add brief loading animation
            with st.spinner("🚀 Getting started..."):
                import time
                time.sleep(0.3)  # Brief pause for visual feedback
            if has_api_keys:
                st.session_state.page = "language_select"
            else:
                st.session_state.page = "api_setup"
            st.rerun()

    # Scroll to top after all content is rendered
    st.markdown("""
    <script>
        setTimeout(function() {
            window.scrollTo({top: 0, behavior: 'smooth'});
        }, 1000);
    </script>
    """, unsafe_allow_html=True)