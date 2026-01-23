# pages/privacy_policy.py - Privacy Policy page for the language learning app

import streamlit as st


def render_privacy_policy_page():
    """Render the privacy policy page."""
    st.title("🔒 Privacy Policy")
    st.markdown("*Last updated: December 18, 2025*")

    st.markdown("---")

    st.markdown("""
    ## 1. Introduction

    Welcome to the **Language Anki Deck Generator** ("we," "our," or "us"). This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our language learning application that generates personalized Anki flashcards.

    By using our service, you agree to the collection and use of information in accordance with this policy.

    ## 2. Information We Collect

    ### Personal Information
    - **Account Information**: Email address (if you sign in with Google)
    - **Usage Preferences**: Language preferences, API settings, theme choices
    - **Contact Information**: Information provided in contact forms or support requests

    ### Technical Information
    - **Device Information**: Browser type, operating system, screen resolution
    - **Usage Data**: Pages visited, features used, time spent on app
    - **Log Data**: IP address, access times, error reports

    ### Third-Party Service Data
    - **API Usage**: Information sent to and received from Google Gemini AI, Pixabay, and Google Cloud Text-to-Speech
    - **Generated Content**: Language learning cards and audio files you create

    ## 3. How We Use Your Information

    We use the collected information for:

    - **Providing Services**: Generate personalized language learning content
    - **Improving User Experience**: Analyze usage patterns to enhance features
    - **Technical Support**: Troubleshoot issues and provide assistance
    - **Communication**: Send important updates about service changes
    - **Legal Compliance**: Meet legal obligations and protect our rights

    ## 4. Information Sharing and Disclosure

    We do not sell, trade, or rent your personal information to third parties. We may share information only in the following circumstances:

    - **Service Providers**: With trusted third-party services (Groq, Pixabay, Firebase) necessary for app functionality
    - **Legal Requirements**: When required by law or to protect our rights
    - **Business Transfers**: In case of merger, acquisition, or sale of assets
    - **With Your Consent**: When you explicitly agree to sharing

    ## 5. Data Security

    We implement appropriate technical and organizational measures to protect your personal information:

    - **Encryption**: Data transmitted using HTTPS/TLS encryption
    - **Access Controls**: Limited access to personal data on a need-to-know basis
    - **Regular Updates**: Security measures are regularly reviewed and updated
    - **Data Minimization**: We collect only necessary information for service provision

    ## 6. Data Retention

    - **Account Data**: Retained while your account is active and for 2 years after deactivation
    - **Usage Logs**: Retained for 1 year for analytics and troubleshooting
    - **Generated Content**: Stored according to your local storage preferences
    - **Legal Holds**: Data may be retained longer if required for legal proceedings

    ## 7. Your Rights

    Depending on your location, you may have the following rights:

    - **Access**: Request a copy of your personal data
    - **Correction**: Update inaccurate or incomplete information
    - **Deletion**: Request deletion of your personal data
    - **Portability**: Receive your data in a structured format
    - **Opt-out**: Withdraw consent for data processing
    - **Complaint**: Lodge a complaint with supervisory authorities

    ## 8. Cookies and Tracking

    ### Essential Cookies
    - **Session Management**: Maintain your login status and preferences
    - **Security**: Prevent unauthorized access and detect fraud

    ### Analytics Cookies
    - **Usage Tracking**: Understand how users interact with the app
    - **Performance Monitoring**: Identify and fix technical issues

    You can control cookie preferences through your browser settings.

    ## 9. Third-Party Services

    Our app integrates with several third-party services:

    - **Google Gemini AI**: Processes text for sentence generation (see their [privacy policy](https://policies.google.com/privacy))
    - **Pixabay**: Provides images for flashcards (see their [privacy policy](https://pixabay.com/service/privacy/))
    - **Google Cloud Text-to-Speech**: Generates audio pronunciations (Google service)
    - **Firebase**: Cloud storage and authentication (see their [privacy policy](https://firebase.google.com/support/privacy))

    ## 10. International Data Transfers

    Your data may be processed in countries other than your own. We ensure appropriate safeguards are in place for international transfers in compliance with applicable data protection laws.

    ## 11. Children's Privacy

    Our service is designed for users of all ages interested in language learning. We do not knowingly collect personal information from children under 13. If you believe we have collected information from a child, please contact us immediately.

    ## 12. Changes to This Privacy Policy

    We may update this Privacy Policy from time to time. We will notify you of any changes by:

    - Posting the new policy on this page
    - Sending an email notification (if applicable)
    - Displaying an in-app notification

    Your continued use of the service after changes constitutes acceptance of the updated policy.

    ## 13. Contact Us

    If you have any questions about this Privacy Policy, please contact us:

    - **Email**: agnel.joseph.n@gmail.com
    - **Response Time**: We aim to respond within 48 hours
    - **Data Protection Officer**: agnel.joseph.n@gmail.com

    ## 14. Governing Law

    This Privacy Policy is governed by the laws of India Karnataka. Any disputes will be resolved in the courts of India Karnataka.
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
        if st.button("Terms & Conditions", use_container_width=True):
            st.session_state.page = "terms_conditions"
            st.rerun()
    with col2:
        if st.button("Refund Policy", use_container_width=True):
            st.session_state.page = "refund_policy"
            st.rerun()
    with col3:
        if st.button("Contact Us", use_container_width=True):
            st.session_state.page = "contact_us"
            st.rerun()