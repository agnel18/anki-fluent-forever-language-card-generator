# pages/refund_policy.py - Refund Policy page for the language learning app

import streamlit as st


def render_refund_policy_page():
    """Render the refund policy page."""
    st.title("💰 Cancellation and Refund Policy")
    st.markdown("*Last updated: December 18, 2025*")

    st.markdown("---")

    st.markdown("""
    ## 1. Overview

    The **AI-Powered Language Learning App** is primarily a free educational service. While we accept voluntary donations to support development, our core language learning features are provided at no cost. This refund policy explains our approach to donations, cancellations, and any future paid services.

    ## 2. Free Service Policy

    ### No Payment Required
    - All core language learning features are completely free
    - No subscription fees or mandatory payments
    - You can use the service indefinitely without any cost

    ### Voluntary Donations
    - Donations are entirely optional and appreciated
    - Donations support continued development and improvement
    - Donors receive no additional features or priority access

    ## 3. Donation Policy

    ### Nature of Donations
    - Donations are voluntary contributions to support our mission
    - Donations are processed through secure third-party payment processors
    - All donations are final and non-refundable

    ### Donation Processing
    - Donations are processed immediately upon submission
    - You will receive a confirmation email from the payment processor
    - Processing fees may apply (varies by payment method and location)

    ### Tax Implications
    - Donations may be tax-deductible in some jurisdictions
    - Consult your local tax advisor for specific guidance
    - We do not provide tax receipts unless required by law

    ## 4. Cancellation Policy

    ### Account Cancellation
    - You may cancel your account at any time
    - Cancellation does not affect previously generated content
    - Your data will be deleted according to our Privacy Policy

    ### Service Access
    - Cancellation prevents future access to your account
    - Generated Anki decks remain accessible locally
    - No refunds for account cancellation

    ## 5. Future Paid Services

    Should we introduce premium features in the future:

    ### Refund Eligibility
    - Refunds available within 30 days of purchase
    - Technical issues preventing service use
    - Service not matching advertised description
    - Duplicate or erroneous charges

    ### Non-Refundable Items
    - Voluntary donations
    - Services already consumed or delivered
    - Charges older than 30 days
    - Refunds already processed

    ### Refund Process
    1. Contact us with your refund request
    2. Provide order/transaction details
    3. Explain the reason for the refund
    4. We will review and respond within 5-7 business days
    5. Approved refunds processed within 10-14 business days

    ## 6. Refund Methods

    ### Payment Method Refunds
    - Refunds credited to original payment method
    - Processing time varies by payment provider
    - Bank transfers may take 5-10 business days

    ### Alternative Refund Options
    - Store credit for future services (if applicable)
    - Alternative payment methods (case-by-case basis)

    ## 7. Refund Exceptions

    ### Special Circumstances
    - Refunds may be denied for policy violations
    - Fraudulent or abusive refund requests
    - Requests submitted after extended periods

    ### Dispute Resolution
    - Contact us first for all refund inquiries
    - We strive to resolve issues amicably
    - Payment processor dispute processes available as last resort

    ## 8. Contact Information

    For refund requests or questions:

    ### Primary Contact
    - **Email**: [Your contact email]
    - **Subject Line**: "Refund Request - [Transaction ID]"
    - **Response Time**: Within 48 hours

    ### Required Information
    - Full name and contact details
    - Transaction/order ID
    - Date of purchase/donation
    - Reason for refund request
    - Any supporting documentation

    ## 9. Changes to Policy

    ### Policy Updates
    - This policy may be updated as our services evolve
    - Changes will be posted on this page
    - Continued use constitutes acceptance of updates

    ### Notification
    - Major policy changes will be communicated via email
    - In-app notifications for significant updates

    ## 10. Governing Law

    This refund policy is governed by the laws of [Your jurisdiction]. Any disputes will be resolved through appropriate legal channels in [Your jurisdiction].

    ## 11. Acknowledgment

    By using our service, you acknowledge that you have read, understood, and agree to this refund policy. For donations, you understand that they are voluntary and non-refundable contributions to support our educational mission.
    """)

    st.markdown("---")

    # Navigation back to main app
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        if st.button("← Back to Language Learning App", use_container_width=True, type="primary"):
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
        if st.button("Terms & Conditions", use_container_width=True):
            st.session_state.page = "terms_conditions"
            st.rerun()
    with col3:
        if st.button("Contact Us", use_container_width=True):
            st.session_state.page = "contact_us"
            st.rerun()