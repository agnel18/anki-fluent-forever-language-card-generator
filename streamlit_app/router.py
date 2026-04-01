import importlib
import logging
import streamlit as st

logger = logging.getLogger(__name__)

# Registry: page_name -> (module_path, function_name)
PAGE_REGISTRY = {
    "api_setup":          ("streamlit_app.page_modules.api_setup",          "render_api_setup_page"),
    "main":               ("streamlit_app.page_modules.main",               "render_main_page"),
    "language_select":    ("streamlit_app.page_modules.language_select",    "render_language_select_page"),
    "word_select":        ("streamlit_app.page_modules.word_select",        "render_word_select_page"),
    "sentence_settings":  ("streamlit_app.page_modules.sentence_settings",  "render_sentence_settings_page"),
    "generate":           ("streamlit_app.page_modules.generate",           "render_generate_page"),
    "generating":         ("streamlit_app.page_modules.generating",         "render_generating_page"),
    "complete":           ("streamlit_app.page_modules.complete",           "render_complete_page"),
    "settings":           ("streamlit_app.page_modules.settings",           "render_settings_page"),
    "statistics":         ("streamlit_app.page_modules.statistics",         "render_statistics_page"),
    "my_word_lists":      ("streamlit_app.page_modules.my_word_lists",      "render_my_word_lists_page"),
    "privacy_policy":     ("streamlit_app.page_modules.privacy_policy",     "render_privacy_policy_page"),
    "terms_conditions":   ("streamlit_app.page_modules.terms_conditions",   "render_terms_conditions_page"),
    "refund_policy":      ("streamlit_app.page_modules.refund_policy",      "render_refund_policy_page"),
    "shipping_delivery":  ("streamlit_app.page_modules.shipping_delivery",  "render_shipping_delivery_page"),
    "contact_us":         ("streamlit_app.page_modules.contact_us",         "render_contact_us_page"),
    "auth_handler":       ("streamlit_app.page_modules.auth_handler",       "render_auth_handler_page"),
}

def route_to_page(current_page):
    """Route to the appropriate page based on current_page."""
    try:
        entry = PAGE_REGISTRY.get(current_page)
        if entry:
            module_path, func_name = entry
            module = importlib.import_module(module_path)
            getattr(module, func_name)()
        else:
            logger.warning(f"Unknown page '{current_page}', defaulting to main")
            module = importlib.import_module("streamlit_app.page_modules.main")
            module.render_main_page()
    except Exception as page_error:
        logger.error(f"Page loading error for '{current_page}': {type(page_error).__name__}: {page_error}", exc_info=True)
        st.error(f"Error loading page '{current_page}': {page_error}")
        st.write("Falling back to main page...")
        try:
            from page_modules.main import render_main_page
            render_main_page()
        except Exception as fallback_error:
            st.error(f"Critical error: Could not load any page. {fallback_error}")
            st.stop()