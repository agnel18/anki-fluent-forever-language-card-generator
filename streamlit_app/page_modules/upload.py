# pages/upload.py - CSV upload page for the language learning app

import streamlit as st
import pandas as pd
from frequency_utils import get_csv_template, validate_word_list


def render_upload_page():
    """Render the CSV upload page for custom word lists."""

    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("# 📥 Upload Your Own Words")
    with col2:
        if st.button("← Back"):
            st.session_state.page = "main"
            st.session_state.scroll_to_top = True
            st.rerun()

    st.divider()

    csv_template = get_csv_template()
    st.download_button(
        label="📋 Download CSV Template",
        data=csv_template,
        file_name="word_list_template.csv",
        mime="text/csv",
        use_container_width=True
    )

    st.divider()

    uploaded_file = st.file_uploader("Choose CSV or XLSX file", type=["csv", "xlsx"])

    if uploaded_file:
        try:
            if uploaded_file.type == "text/csv":
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            words = df.iloc[:, 0].dropna().tolist()
            words = [str(w).strip() for w in words if w]

            is_valid, message = validate_word_list(words)

            if is_valid:
                st.success(message)
                col1, col2 = st.columns(2)
                col1.metric("Words", len(words))
                col2.metric("Ready", "✅")

                st.divider()

                if st.button("🚀 Generate from Custom Words", use_container_width=True, type="primary"):
                    with st.spinner("Starting deck generation..."):
                        st.session_state.selected_lang = "Custom"
                        st.session_state.selected_words = words
                        st.session_state.page = "generating"
                        st.session_state.scroll_to_top = True
                        st.rerun()
            else:
                st.error(message)

        except Exception as e:
            st.error(f"❌ Error: {str(e)}")