# payment.py - Simple donation integration using Razorpay.me links

import streamlit as st

def render_donation_section():
    """Render the donation/payment section in Streamlit."""
    st.markdown("---")
    st.markdown("## 💝 Support Our Mission")

    st.markdown("""
    Your generous donations help us:
    - Keep the language learning tools **free and accessible**
    - Add **new languages and features**
    - Maintain and improve our AI-powered learning system
    - Support **educational initiatives** worldwide
    """)

    # Simple donation button
    st.markdown("### Make a Donation")
    st.markdown("Click below to support us with any amount you choose:")

    # Razorpay.me link
    donation_url = "https://razorpay.me/@agneljosephn"

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<a href="{donation_url}" target="_blank" style="text-decoration: none;"><button style="background-color: #FF6B35; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%;">💳 Donate Now</button></a>', unsafe_allow_html=True)

    # Impact message
    st.success("🎉 Every contribution, no matter the size, helps us continue our mission!")

    return