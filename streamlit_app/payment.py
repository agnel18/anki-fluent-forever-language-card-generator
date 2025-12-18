# payment.py - Razorpay payment integration module

try:
    import razorpay
    RAZORPAY_AVAILABLE = True
except ImportError:
    RAZORPAY_AVAILABLE = False
    razorpay = None

import json
from typing import Dict, Optional
import streamlit as st
import os

# Razorpay configuration - handle both Streamlit secrets and environment variables
try:
    RAZORPAY_KEY_ID = st.secrets.get("RAZORPAY_KEY_ID", os.getenv("RAZORPAY_KEY_ID"))
    RAZORPAY_KEY_SECRET = st.secrets.get("RAZORPAY_KEY_SECRET", os.getenv("RAZORPAY_KEY_SECRET"))
except:
    # Fallback for when Streamlit secrets are not available (e.g., during import testing)
    RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
    RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")

def initialize_razorpay():
    """Initialize Razorpay client."""
    if not RAZORPAY_AVAILABLE:
        print("Razorpay library not available")
        return None

    if not RAZORPAY_KEY_ID or not RAZORPAY_KEY_SECRET:
        return None

    try:
        client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
        return client
    except Exception as e:
        print(f"Failed to initialize Razorpay: {e}")
        return None

def create_order(amount: int, currency: str = "INR", receipt: str = None) -> Optional[Dict]:
    """
    Create a Razorpay order.

    Args:
        amount: Amount in paisa (1 INR = 100 paisa)
        currency: Currency code (default: INR)
        receipt: Optional receipt ID

    Returns:
        Order data dict or None if failed
    """
    client = initialize_razorpay()
    if not client:
        return None

    try:
        order_data = {
            "amount": amount,  # Amount in paisa
            "currency": currency,
            "payment_capture": 1  # Auto capture payment
        }

        if receipt:
            order_data["receipt"] = receipt

        order = client.order.create(data=order_data)
        return order
    except Exception as e:
        print(f"Failed to create order: {e}")
        return None

def verify_payment_signature(order_id: str, payment_id: str, signature: str) -> bool:
    """
    Verify payment signature for security.

    Args:
        order_id: Razorpay order ID
        payment_id: Razorpay payment ID
        signature: Razorpay signature

    Returns:
        True if signature is valid, False otherwise
    """
    client = initialize_razorpay()
    if not client:
        return False

    try:
        params_dict = {
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'razorpay_signature': signature
        }
        return client.utility.verify_payment_signature(params_dict)
    except Exception as e:
        print(f"Signature verification failed: {e}")
        return False

def get_payment_status(payment_id: str) -> Optional[Dict]:
    """Get payment status from Razorpay."""
    client = initialize_razorpay()
    if not client:
        return None

    try:
        payment = client.payment.fetch(payment_id)
        return payment
    except Exception as e:
        print(f"Failed to fetch payment: {e}")
        return None

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

    # Check if Razorpay is available
    if not RAZORPAY_AVAILABLE:
        st.info("💳 **Payment Integration Status:** Currently using external payment links for better compatibility.")

        # Alternative payment methods
        st.markdown("### Choose Your Payment Method:")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 💳 **UPI/Google Pay/PhonePe**")
            st.markdown("**Scan QR Code or use UPI ID:**")
            st.markdown("`your-upi-id@paytm`")  # Replace with actual UPI ID

            # Placeholder for QR code
            st.image("https://via.placeholder.com/200x200?text=UPI+QR+Code", caption="Scan to donate via UPI")

        with col2:
            st.markdown("#### 🏦 **Bank Transfer**")
            st.markdown("**Account Details:**")
            st.markdown("""
            - **Account Name:** AI Language Learning
            - **Account Number:** XXXXXXXX1234
            - **IFSC Code:** SBIN0001234
            - **Bank:** State Bank of India
            """)

        st.markdown("---")
        st.markdown("#### 📧 **Contact for Custom Donations**")
        st.markdown("For larger donations or corporate sponsorships:")
        st.markdown("📧 donations@ailanguagelearning.org")
        st.markdown("📱 +91-XXXXXXXXXX")

        return

    # Original Razorpay integration (when available)
    # Donation amounts
    donation_options = {
        "Coffee ☕": 10000,  # ₹100
        "Lunch 🍽️": 20000,  # ₹200
        "Book 📚": 50000,   # ₹500
        "Custom Amount": None
    }

    col1, col2 = st.columns([2, 1])

    with col1:
        selected_option = st.selectbox(
            "Choose your donation amount:",
            options=list(donation_options.keys()),
            help="Select a preset amount or choose 'Custom Amount'"
        )

        if selected_option == "Custom Amount":
            custom_amount = st.number_input(
                "Enter amount (₹):",
                min_value=10,
                max_value=10000,
                value=100,
                step=50,
                help="Minimum ₹10, Maximum ₹10,000"
            )
            amount_paisa = custom_amount * 100
        else:
            amount_paisa = donation_options[selected_option]

        # Donor information
        with st.expander("📝 Donor Information (Optional)", expanded=False):
            donor_name = st.text_input("Full Name", placeholder="Your name")
            donor_email = st.text_input("Email", placeholder="your.email@example.com")
            donor_message = st.text_area("Message", placeholder="Leave a message of encouragement...", height=80)

    with col2:
        if amount_paisa:
            amount_rupees = amount_paisa / 100
            st.markdown(f"### Amount: ₹{amount_rupees:,.0f}")

            # Check if Razorpay is configured
            if not RAZORPAY_KEY_ID:
                st.error("⚠️ Payment system not configured. Please contact support.")
                return

            # Payment button
            if st.button("💳 Donate Now", type="primary", use_container_width=True):
                process_payment(amount_paisa, donor_name, donor_email, donor_message)

    # Payment status display
    if "payment_status" in st.session_state:
        status = st.session_state.payment_status
        if status == "success":
            st.success("✅ Thank you for your generous donation!")
            st.balloons()
        elif status == "failed":
            st.error("❌ Payment failed. Please try again.")
        elif status == "cancelled":
            st.warning("⚠️ Payment was cancelled.")

        # Clear status after showing
        del st.session_state.payment_status

    # JavaScript to handle payment callbacks
    payment_callback_js = """
    <script>
        window.addEventListener('message', function(event) {
            if (event.data.type === 'razorpay_success') {
                // Store callback data in session state
                window.parent.postMessage({
                    type: 'streamlit:setSessionState',
                    key: 'payment_callback_data',
                    value: {
                        status: 'success',
                        payment_id: event.data.payment_id,
                        order_id: event.data.order_id,
                        signature: event.data.signature
                    }
                }, '*');
            } else if (event.data.type === 'razorpay_failed') {
                // Store failure data in session state
                window.parent.postMessage({
                    type: 'streamlit:setSessionState',
                    key: 'payment_callback_data',
                    value: {
                        status: 'failed',
                        error: event.data.error
                    }
                }, '*');
            }
        });
    </script>
    """

    st.components.v1.html(payment_callback_js, height=1)

def process_payment(amount_paisa: int, donor_name: str = "", donor_email: str = "", donor_message: str = ""):
    """Process the payment with Razorpay."""

    # Create order
    order = create_order(amount_paisa, receipt=f"donation_{st.session_state.get('session_id', 'anonymous')}")

    if not order:
        st.error("Failed to create payment order. Please try again.")
        return

    order_id = order['id']

    # Store order details in session state
    st.session_state.razorpay_order = {
        'order_id': order_id,
        'amount': amount_paisa,
        'donor_name': donor_name,
        'donor_email': donor_email,
        'donor_message': donor_message
    }

    # Razorpay Checkout JavaScript
    checkout_script = f"""
    <script src="https://checkout.razorpay.com/v1/checkout.js"></script>
    <script>
        var options = {{
            "key": "{RAZORPAY_KEY_ID}",
            "amount": "{amount_paisa}",
            "currency": "INR",
            "name": "AI Language Learning App",
            "description": "Support our educational mission",
            "order_id": "{order_id}",
            "handler": function (response) {{
                // Handle successful payment
                window.parent.postMessage({{
                    type: 'razorpay_success',
                    payment_id: response.razorpay_payment_id,
                    order_id: response.razorpay_order_id,
                    signature: response.razorpay_signature
                }}, '*');
            }},
            "prefill": {{
                "name": "{donor_name}",
                "email": "{donor_email}"
            }},
            "notes": {{
                "message": "{donor_message}"
            }},
            "theme": {{
                "color": "#3399cc"
            }}
        }};

        var rzp = new Razorpay(options);

        rzp.on('payment.failed', function (response) {{
            window.parent.postMessage({{
                type: 'razorpay_failed',
                error: response.error
            }}, '*');
        }});

        rzp.open();
    </script>
    """

    # Display the checkout
    st.components.v1.html(checkout_script, height=1)

    # Listen for payment messages (this would need to be handled in the main app)
    st.markdown("**Processing payment...** Please complete the payment in the popup window.")

def handle_payment_callback():
    """Handle payment callback messages from JavaScript."""
    # This function would be called from the main app to handle payment results
    pass