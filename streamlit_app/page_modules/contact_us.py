# pages/contact_us.py - Contact Us page for the language learning app

import streamlit as st


def render_contact_us_page():
    """Render the contact us page."""
    st.title("📞 Contact Us")
    st.markdown("*Last updated: December 18, 2025*")

    st.markdown("---")

    st.markdown("""
    ## Get in Touch

    We're here to help you with your language learning journey! Whether you have questions about the app, need technical support, or want to share feedback, don't hesitate to reach out.

    ## 📧 Primary Contact Information

    ### Developer & Support
    - **Name**: Agnel J N
    - **Role**: Full Stack Developer & Language Learning Enthusiast
    - **Email**: agnel.joseph.n@gmail.com
    - **Response Time**: Within 24-48 hours

    ### Business Inquiries
    - **Email**: agnel.joseph.n@gmail.com
    - **Subject**: Include "Business Inquiry" in the subject line
    - **Topics**: Partnerships, collaborations, media inquiries

    ## 🆘 Technical Support

    ### Before Contacting Support
    Please check our troubleshooting resources:
    - **Common Issues**: Browser compatibility, API key setup, Anki import problems
    - **Self-Help Guide**: Available in the app's help section
    - **Community Forum**: Check for similar issues reported by other users

    ### Support Hours
    - **Primary Hours**: Monday - Friday, 9:00 AM - 6:00 PM IST
    - **Emergency Support**: Critical technical issues responded to within 12 hours
    - **Weekend Support**: Limited support on weekends

    ### What to Include in Support Requests
    - **Clear Description**: What you were trying to do and what went wrong
    - **Error Messages**: Copy any error messages you received
    - **Browser/Device Info**: Browser type, operating system, device
    - **Steps to Reproduce**: How to recreate the issue
    - **Screenshots**: If applicable (please blur sensitive information)

    ## 💡 Feature Requests & Feedback

    ### How to Submit Ideas
    - **Email**: agnel.joseph.n@gmail.com
    - **Subject**: "Feature Request" or "Feedback"
    - **Details**: Describe your idea and why it would be valuable
    - **Priority**: Let us know how important this is to you

    ### Feedback Categories
    - **Bug Reports**: Technical issues and errors
    - **Feature Suggestions**: New language support, UI improvements
    - **Content Quality**: Sentence accuracy, audio quality, image relevance
    - **User Experience**: Navigation, performance, accessibility

    ## 🌐 Language Support

    ### Supported Languages
    Our app currently supports learning in multiple languages. If you need support for additional languages, please let us know!

    ### Translation Requests
    - **UI Translation**: Help translate the interface to new languages
    - **Content Localization**: Requests for region-specific content
    - **Cultural Adaptation**: Suggestions for culturally appropriate content

    ## 🔒 Privacy & Security

    ### Data Protection
    - **Privacy Concerns**: Questions about data handling and privacy
    - **Security Questions**: How we protect your information
    - **Data Deletion**: Requests to delete your account and data

    ### Report Issues
    - **Privacy Violations**: Report suspected privacy issues
    - **Security Concerns**: Report potential security vulnerabilities
    - **Content Issues**: Report inappropriate or harmful content

    ## 📊 Analytics & Usage Data

    ### Usage Statistics
    - **API Usage**: Questions about API limits and usage tracking
    - **Progress Tracking**: How your learning progress is stored
    - **Data Export**: Requests for your personal data

    ## 🎓 Educational Partnerships

    ### Schools & Institutions
    - **Educational Licenses**: Special pricing for educational institutions
    - **Classroom Integration**: How to use the app in classroom settings
    - **Teacher Resources**: Additional resources for educators

    ### Researchers
    - **Academic Research**: Collaboration opportunities
    - **Data Access**: Requests for anonymized usage data
    - **API Access**: Special access for research purposes

    ## 💰 Donations & Contributions

    ### Donation Support
    - **Donation Confirmation**: Questions about donation processing
    - **Tax Receipts**: Inquiries about donation tax implications
    - **Donation Impact**: How donations support development

    ### Contributing to the Project
    - **Code Contributions**: How to contribute to the open-source project
    - **Translation Help**: Volunteer to translate the app
    - **Testing**: Help test new features and provide feedback

    ## 📱 Social Media & Community

    ### Stay Connected
    - **GitHub**: agnel.joseph.n@gmail.com
    - **LinkedIn**: https://in.linkedin.com/in/agnel-noojibalthila-08976b29
    - **Twitter/X**: @agnel18
    - **YouTube**: https://www.youtube.com/@agnel14

    ### Community Guidelines
    - **Respectful Communication**: Keep discussions constructive and respectful
    - **Help Others**: Share your knowledge and help fellow learners
    - **Report Issues**: Use appropriate channels for bug reports and feature requests

    ## ⚖️ Legal Inquiries

    ### Policy Questions
    - **Terms of Service**: Questions about acceptable use
    - **Privacy Policy**: Clarifications about data handling
    - **Refund Policy**: Questions about donations and refunds

    ### Legal Compliance
    - **Accessibility**: Questions about app accessibility
    - **GDPR/CCPA**: Data protection regulation questions
    - **Copyright**: Intellectual property and content licensing

    ## 🚀 Future Development

    ### Roadmap Questions
    - **Upcoming Features**: What's planned for future releases
    - **Beta Testing**: How to participate in beta testing
    - **Early Access**: Special access to new features

    ## 📞 Emergency Contact

    For urgent technical issues that prevent you from using the service:

    - **Emergency Email**: agnel.joseph.n@gmail.com
    - **Priority Response**: Within 4 hours during business days
    - **After Hours**: Best effort response within 12 hours

    ---

    ## 📝 Contact Form

    For your convenience, here's what we need to help you effectively:
    """)

    # Contact form simulation
    with st.form("contact_form"):
        st.markdown("### Send us a message")

        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Your Name", placeholder="Enter your full name")
        with col2:
            email = st.text_input("Email Address", placeholder="your.email@example.com")

        category = st.selectbox(
            "Category",
            ["General Inquiry", "Technical Support", "Bug Report", "Feature Request",
             "Privacy Concern", "Educational Partnership", "Other"]
        )

        subject = st.text_input("Subject", placeholder="Brief description of your inquiry")

        message = st.text_area(
            "Message",
            placeholder="Please provide detailed information about your question or issue...",
            height=150
        )

        urgency = st.selectbox(
            "Urgency",
            ["Low - General question", "Medium - Need help soon", "High - Urgent issue", "Critical - Service down"]
        )

        submitted = st.form_submit_button("Send Message", type="primary", use_container_width=True)

        if submitted:
            if not name or not email or not message:
                st.error("Please fill in all required fields.")
            else:
                st.success("Thank you for your message! We'll get back to you within 24-48 hours.")
                # In a real implementation, this would send an email or save to database

    st.markdown("---")

    # Quick contact options
    st.markdown("### Quick Contact Options")
    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("**📧 Email Support**")
        st.code("agnel.joseph.n@gmail.com")
        st.markdown("*Response: 24-48 hours*")

    with col2:
        st.markdown("**🐛 Bug Reports**")
        st.code("agnel.joseph.n@gmail.com")
        st.markdown("*Priority handling*")

    with col3:
        st.markdown("**💡 Feature Requests**")
        st.code("agnel.joseph.n@gmail.com")
        st.markdown("*Community driven*")

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
        if st.button("Refund Policy", use_container_width=True):
            st.session_state.page = "refund_policy"
            st.rerun()