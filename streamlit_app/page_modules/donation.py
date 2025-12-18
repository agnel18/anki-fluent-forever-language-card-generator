# pages/donation.py - Donation page for the language learning app

import streamlit as st
from payment import render_donation_section

def render_donation_page():
    """Render the donation page."""
    st.title("💝 Support Our Mission")
    st.markdown("*Help us keep language learning free and accessible*")

    st.markdown("---")

    st.markdown("""
    ## 🌟 Why Your Support Matters

    Your generous donations directly support:

    ### 🎓 **Free Education for Everyone**
    - **Zero-cost access** to AI-powered language learning tools
    - **No premium tiers** or paywalls blocking learning
    - **Inclusive education** for students worldwide

    ### 🚀 **Innovation & Growth**
    - **New language support** (we're planning 50+ languages!)
    - **Advanced AI features** for better learning outcomes
    - **Mobile apps** and offline capabilities

    ### 🌍 **Global Impact**
    - **Educational initiatives** in underserved communities
    - **Teacher training programs** and resources
    - **Research partnerships** with universities

    ### 💻 **Technical Excellence**
    - **Server costs** for AI processing and cloud storage
    - **Development tools** and infrastructure
    - **Quality assurance** and security updates
    """)

    # Impact statistics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Languages Supported", "15+")
    with col2:
        st.metric("Flashcards Generated", "10,000+")
    with col3:
        st.metric("Happy Learners", "1,000+")

    st.markdown("---")

    # Donation section
    render_donation_section()

    st.markdown("---")

    st.markdown("""
    ## 🙏 Our Commitment to Donors

    ### **100% Transparency**
    - All donations go directly to development and operations
    - Regular updates on how funds are used
    - Public financial reports available

    ### **No Strings Attached**
    - Donations are voluntary and never required
    - No premium features or priority access
    - Your support doesn't change the free experience

    ### **Tax Benefits**
    - Donations may be tax-deductible in your country
    - We provide donation receipts upon request
    - Contact us for tax-related questions
    """)

    # Navigation back to main app
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back to Language Learning App", use_container_width=True, type="primary"):
            st.session_state.page = "main"
            st.rerun()</content>
<parameter name="filePath">d:\Language Learning\LanguagLearning\streamlit_app\page_modules\donation.py