
# pages/donation.py - Voluntary payment page for the language learning app

import streamlit as st
from payment import render_payment_section


def render_payment_page():
    """Render the voluntary payment page."""
    st.title("💸 Pay Fees of Any Amount")
    st.markdown("*Help keep this language learning app running for everyone*")

    st.markdown("---")

    st.markdown("""
    ## 🌟 Why Your Payment Matters

    Your fees directly help with:

    ### 🎓 **Free Education for Everyone**
    - **Zero-cost access** to AI-powered language learning tools
    - **No premium tiers** or paywalls blocking learning
    - **Inclusive education** for students worldwide

    ### 🚀 **Innovation & Growth**
    - **New language support**
    - **Advanced AI features** for better learning outcomes
    - **Mobile apps** and offline capabilities

    ### 🌍 **Global Impact**
    - **Educational initiatives** in underserved communities
    - **Teacher training programs** and resources

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

    # Payment section
    render_payment_section()

    st.markdown("---")

    st.markdown("""
    ## 🙏 Our Commitment to You

    ### **100% Transparency**
    - All fees go directly to development and operations

    ### **No Strings Attached**
    - Payments are voluntary and never required
    - No premium features or priority access
    - Your payment doesn't change the free experience

    ### **Receipts**
    - Receipts available upon request
    - Contact us for payment-related questions
    """)

    # Navigation back to main app
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back to Language Anki Deck Generator", use_container_width=True, type="primary"):
            st.session_state.page = "main"
            st.rerun()