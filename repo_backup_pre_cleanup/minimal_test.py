import streamlit as st

st.title("Minimal Test App")
st.write("If you can see this, basic Streamlit is working.")

# Test our imports
try:
    from constants import GROQ_CALL_LIMIT
    st.write(f"✅ Constants: GROQ_CALL_LIMIT = {GROQ_CALL_LIMIT}")

    from state_manager import initialize_languages_config
    st.write("✅ State manager imported")

    from router import route_to_page
    st.write("✅ Router imported")

    st.success("🎉 All imports work in Streamlit runtime!")

except Exception as e:
    st.error(f"❌ Error: {e}")
    st.code(str(e))