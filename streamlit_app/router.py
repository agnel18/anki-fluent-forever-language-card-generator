import streamlit as st

def route_to_page(current_page):
    """Route to the appropriate page based on current_page."""
    try:
        if current_page == "api_setup":
            from page_modules.api_setup import render_api_setup_page
            render_api_setup_page()
        elif current_page == "main":
            from page_modules.main import render_main_page
            render_main_page()
        elif current_page == "language_select":
            from page_modules.language_select import render_language_select_page
            render_language_select_page()
        elif current_page == "word_select":
            from page_modules.word_select import render_word_select_page
            render_word_select_page()
        elif current_page == "sentence_settings":
            from page_modules.sentence_settings import render_sentence_settings_page
            render_sentence_settings_page()
        elif current_page == "generate":
            from page_modules.generate import render_generate_page
            render_generate_page()
        elif current_page == "generating":
            from page_modules.generating import render_generating_page
            render_generating_page()
        elif current_page == "complete":
            from page_modules.complete import render_complete_page
            render_complete_page()
        elif current_page == "settings":
            from page_modules.settings import render_settings_page
            render_settings_page()
        elif current_page == "statistics":
            from page_modules.statistics import render_statistics_page
            render_statistics_page()
        elif current_page == "my_word_lists":
            from page_modules.my_word_lists import render_my_word_lists_page
            render_my_word_lists_page()
        elif current_page == "privacy_policy":
            from page_modules.privacy_policy import render_privacy_policy_page
            render_privacy_policy_page()
        elif current_page == "terms_conditions":
            from page_modules.terms_conditions import render_terms_conditions_page
            render_terms_conditions_page()
        elif current_page == "refund_policy":
            from page_modules.refund_policy import render_refund_policy_page
            render_refund_policy_page()
        elif current_page == "shipping_delivery":
            from page_modules.shipping_delivery import render_shipping_delivery_page
            render_shipping_delivery_page()
        elif current_page == "contact_us":
            from page_modules.contact_us import render_contact_us_page
            render_contact_us_page()
        elif current_page == "auth_handler":
            from page_modules.auth_handler import render_auth_handler_page
            render_auth_handler_page()
        else:
            # Default to main page
            print(f"Warning: Unknown page '{current_page}', defaulting to main")
            from page_modules.main import render_main_page
            render_main_page()
    except Exception as page_error:
        st.error(f"Error loading page '{current_page}': {page_error}")
        st.write("Falling back to main page...")
        try:
            from page_modules.main import render_main_page
            render_main_page()
        except Exception as fallback_error:
            st.error(f"Critical error: Could not load any page. {fallback_error}")
            st.stop()