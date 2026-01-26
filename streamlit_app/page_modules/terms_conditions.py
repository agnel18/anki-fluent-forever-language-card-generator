# pages/terms_conditions.py - Terms and Conditions page for the language learning app

import streamlit as st


def render_terms_conditions_page():
    """Render the terms and conditions page."""
    st.title("📋 Terms and Conditions")
    st.markdown("*Last updated: December 18, 2025*")

    st.markdown("---")

    st.markdown("""
    ## 1. Acceptance of Terms

    Welcome to the **Language Anki Deck Generator**. These Terms and Conditions ("Terms") govern your use of our language learning application and services. By accessing or using our service, you agree to be bound by these Terms.

    If you do not agree to these Terms, please do not use our service.

    ## 2. Description of Service

    Our service provides:
    - **Language Anki Deck Generation**: Generation of personalized Anki flashcards
    - **Multilingual Support**: Learning materials for multiple languages
    - **Audio and Visual Content**: Pronunciation guides and contextual images
    - **Progress Tracking**: Learning analytics and statistics

    The service is provided "as is" and is intended for educational purposes only.

    ## 3. User Accounts and Registration

    ### Account Creation
    - You may use the service as a guest or create an account via Google authentication
    - You are responsible for maintaining the confidentiality of your account credentials
    - You must provide accurate and complete information during registration

    ### Account Responsibilities
    - You are responsible for all activities under your account
    - Notify us immediately of any unauthorized use
    - We reserve the right to suspend or terminate accounts that violate these Terms

    ## 4. Acceptable Use Policy

    You agree to use the service only for lawful purposes and in accordance with these Terms:

    ### Permitted Use
    - Personal language learning and educational purposes
    - Sharing generated content for non-commercial purposes
    - Providing constructive feedback

    ### Prohibited Activities
    - Using the service for illegal, harmful, or offensive purposes
    - Attempting to reverse engineer or copy the service
    - Overloading the service with excessive requests
    - Sharing account credentials with others
    - Using automated tools to access the service

    ## 5. Intellectual Property Rights

    ### Our Content
    - The service, including all software, algorithms, and content, is owned by us
    - All rights, title, and interest remain with us
    - You may not reproduce, distribute, or create derivative works without permission

    ### User-Generated Content
    - You retain ownership of content you create using the service
    - By using the service, you grant us a license to process and store your content
    - You are responsible for ensuring your content does not violate third-party rights

    ### Third-Party Services
    - Content from Google Cloud services (Gemini AI, Text-to-Speech) is subject to their respective terms
    - You agree to comply with all third-party service terms

    ## 6. Privacy and Data Protection

    Your privacy is important to us. Please review our Privacy Policy, which forms part of these Terms, for information about how we collect, use, and protect your data.

    ## 7. Service Availability and Modifications

    ### Availability
    - We strive to provide continuous service but do not guarantee uptime
    - Service may be interrupted for maintenance, updates, or unforeseen circumstances
    - We are not liable for service interruptions beyond our reasonable control

    ### Modifications
    - We reserve the right to modify, suspend, or discontinue the service at any time
    - We will provide reasonable notice of significant changes
    - Continued use after changes constitutes acceptance of modified Terms

    ## 8. Payment and Donations

    ### Free Service
    - Basic features are provided free of charge
    - Donations are voluntary and non-refundable
    - No payment is required to use core language learning features

    ### Future Paid Features
    - We may introduce premium features in the future
    - Payment terms for premium features will be clearly communicated
    - All payments are processed securely through authorized payment processors

    ## 9. Limitation of Liability

    ### Disclaimer
    - The service is provided "as is" without warranties of any kind
    - We do not guarantee accuracy of generated content or learning outcomes
    - Language learning results depend on individual effort and circumstances

    ### Liability Limits
    - Our total liability is limited to the amount paid by you for the service
    - We are not liable for indirect, incidental, or consequential damages
    - This limitation applies to the fullest extent permitted by law

    ## 10. Indemnification

    You agree to indemnify and hold us harmless from any claims, damages, losses, or expenses arising from:
    - Your use of the service
    - Your violation of these Terms
    - Your infringement of any third-party rights
    - Any content you submit or generate

    ## 11. Termination

    ### Termination by You
    - You may stop using the service at any time
    - Account deletion requests will be processed within 30 days

    ### Termination by Us
    - We may terminate or suspend your access for violations of these Terms
    - We will provide notice and opportunity to cure where appropriate
    - Upon termination, your right to use the service ceases immediately

    ## 12. Governing Law and Dispute Resolution

    ### Governing Law
    - These Terms are governed by the laws of India Karnataka
    - Any disputes will be resolved in the courts of India Karnataka

    ### Dispute Resolution
    - We encourage amicable resolution of disputes
    - Mediation may be required before legal proceedings
    - Small claims court is appropriate for disputes under applicable thresholds

    ## 13. Severability

    If any provision of these Terms is found to be invalid or unenforceable, the remaining provisions will remain in full force and effect.

    ## 14. Entire Agreement

    These Terms, together with our Privacy Policy, constitute the entire agreement between you and us regarding the use of our service.

    ## 15. Contact Information

    For questions about these Terms, please contact us:
    - **Email**: agnel.joseph.n@gmail.com
    - **Response Time**: We aim to respond within 48 hours

    ## 16. Changes to Terms

    We may update these Terms from time to time. Changes will be:
    - Posted on this page with an updated revision date
    - Communicated via email or in-app notifications
    - Effective 30 days after posting unless otherwise stated

    Your continued use of the service after changes constitutes acceptance of the updated Terms.
    """)

    st.markdown("---")

    # Navigation back to main app
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back to Language Anki Deck Generator", use_container_width=True, type="primary"):
            st.session_state.page = "main"
            st.rerun()

    # Footer with links to other policies
    st.markdown("---")
    st.markdown("### 📄 Related Policies")
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Privacy Policy", use_container_width=True):
            st.session_state.page = "privacy_policy"
            st.rerun()
    with col2:
        if st.button("Refund Policy", use_container_width=True):
            st.session_state.page = "refund_policy"
            st.rerun()
    with col3:
        if st.button("Contact Us", use_container_width=True):
            st.session_state.page = "contact_us"
            st.rerun()