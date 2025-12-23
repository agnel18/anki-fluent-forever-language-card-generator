# pages/shipping_delivery.py - Shipping and Delivery page for the language learning app

import streamlit as st


def render_shipping_delivery_page():
    """Render the shipping and delivery page."""
    st.title("📦 Shipping and Delivery Policy")
    st.markdown("*Last updated: December 18, 2025*")

    st.markdown("---")

    st.markdown("""
    ## 1. Digital Service Overview

    The **Language Anki Deck Generator** is a fully digital service that delivers educational content electronically. Unlike physical products, our service does not involve traditional shipping or physical delivery.

    ## 2. Service Delivery Method

    ### Instant Digital Delivery
    - **Anki Decks**: Generated and delivered instantly within the application
    - **Audio Files**: Created and embedded automatically in flashcards
    - **Images**: Downloaded and integrated seamlessly into learning materials
    - **Progress Data**: Stored locally on your device or synced to cloud

    ### No Physical Shipping
    - Our service requires no physical delivery
    - All content is digital and accessible immediately
    - No shipping costs, delays, or tracking numbers

    ## 3. Delivery Process

    ### Content Generation
    1. **Input**: You select language, words, and preferences
    2. **Processing**: AI generates sentences, audio, and finds images
    3. **Assembly**: Content is compiled into Anki-compatible format
    4. **Delivery**: Download link provided instantly

    ### Typical Delivery Time
    - **Small Decks** (1-50 cards): Instant (seconds)
    - **Medium Decks** (51-200 cards): 30-60 seconds
    - **Large Decks** (201+ cards): 2-5 minutes
    - **Factors**: Internet speed, API response times, content complexity

    ## 4. Delivery Requirements

    ### Technical Requirements
    - **Internet Connection**: Required for content generation and downloads
    - **Browser Compatibility**: Modern browsers with JavaScript enabled
    - **Storage Space**: Sufficient space for generated files
    - **Anki Software**: Required for importing generated decks

    ### System Compatibility
    - **Operating Systems**: Windows, macOS, Linux
    - **Mobile Devices**: iOS and Android (via Anki apps)
    - **Browser Requirements**: Chrome, Firefox, Safari, Edge (latest versions)

    ## 5. Download and Access

    ### File Formats
    - **Anki Decks**: .apkg files (universal Anki format)
    - **Audio Files**: MP3 format (embedded in decks)
    - **Images**: JPG/PNG format (embedded in decks)
    - **Logs**: TXT format (optional download)

    ### Access Methods
    - **Direct Download**: Files downloaded to your device
    - **Local Storage**: Content remains on your computer
    - **Cloud Sync**: Optional synchronization across devices
    - **Backup**: Generated content can be backed up manually

    ## 6. Delivery Issues and Troubleshooting

    ### Common Issues
    - **Slow Generation**: Check internet connection, try during off-peak hours
    - **Download Failures**: Clear browser cache, try different browser
    - **Import Problems**: Ensure Anki is updated, check file integrity
    - **Audio Issues**: Verify speakers/headphones, check volume settings

    ### Support for Delivery Issues
    - **Self-Help**: Check our troubleshooting guide
    - **Technical Support**: Contact us for assistance
    - **Regeneration**: Failed generations can be restarted
    - **Alternative Access**: Content accessible via multiple methods

    ## 7. Data Security During Delivery

    ### Transmission Security
    - **HTTPS Encryption**: All data transmitted securely
    - **API Security**: Communications with third-party services encrypted
    - **File Integrity**: Downloads verified for completeness
    - **Local Storage**: Content stored securely on your device

    ### Privacy Protection
    - **No Personal Data**: Generated content contains no personal information
    - **Usage Tracking**: Minimal analytics for service improvement
    - **Third-Party Access**: Only necessary API communications
    - **Data Retention**: Temporary processing data deleted after delivery

    ## 8. International Access

    ### Global Availability
    - **Service Access**: Available worldwide (subject to local restrictions)
    - **Content Generation**: Works in all countries with internet access
    - **Language Support**: Supports major world languages
    - **API Availability**: Dependent on third-party service availability

    ### Regional Considerations
    - **Internet Speed**: Delivery time varies by connection quality
    - **Content Filtering**: Some regions may restrict certain content
    - **Language Availability**: All supported languages available globally
    - **Support Hours**: Technical support available during business hours

    ## 9. Service Level Agreement

    ### Delivery Guarantees
    - **Completion Rate**: 99.5% successful generation rate
    - **Quality Assurance**: All content reviewed for accuracy
    - **Technical Support**: Available for delivery issues
    - **Regeneration**: Free regeneration for failed deliveries

    ### Limitations
    - **External Factors**: Dependent on third-party API availability
    - **Content Accuracy**: AI-generated content may require review
    - **Technical Issues**: Hardware/software compatibility requirements
    - **Internet Dependency**: Service requires stable internet connection

    ## 10. Future Service Expansions

    ### Potential Physical Products
    Should we expand to include physical products in the future:

    - **Printed Materials**: Physical flashcards or workbooks
    - **Shipping Costs**: Clearly disclosed before purchase
    - **Delivery Times**: Estimated delivery windows provided
    - **International Shipping**: Available with additional costs
    - **Tracking**: Tracking numbers provided for all shipments
    - **Returns**: Return policy for physical products

    ## 11. Contact Information

    For questions about digital delivery or technical issues:

    - **Email**: agnel.joseph.n@gmail.com
    - **Support Hours**: 9am to 5pm IST
    - **Response Time**: Within 24 hours for delivery issues

    ## 12. Policy Updates

    This shipping and delivery policy may be updated as our digital service evolves. Changes will be communicated through the app and this page.
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
        if st.button("Terms & Conditions", use_container_width=True):
            st.session_state.page = "terms_conditions"
            st.rerun()
    with col3:
        if st.button("Contact Us", use_container_width=True):
            st.session_state.page = "contact_us"
            st.rerun()