
# payment.py - Simple voluntary payment integration using Razorpay.me links

import streamlit as st


def render_payment_section():
    """Render the voluntary payment section in Streamlit (Razorpay compliant)."""
    st.markdown("---")
    st.markdown("## Pay Fees of Any Amount")
    st.markdown("Your fees help keep this language learning app running. Any amount is welcome!")
    payment_url = "https://razorpay.me/@agneljosephn"
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f'<a href="{payment_url}" target="_blank" style="text-decoration: none;"><button style="background-color: #FF6B35; color: white; border: none; padding: 12px 24px; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: bold; width: 100%;">Pay Fees</button></a>', unsafe_allow_html=True)
    st.info("Any amount is welcome – choose what works for you. Thank you for helping maintain this free tool! 🙏")
    return