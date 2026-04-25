"""Streamlit UI block for exporting/importing api_keys.json.

Kept separate from api_keys_io (which is UI-free) so the IO layer stays importable
without Streamlit. Both api_setup.py and settings.py call render_api_key_backup_section.
"""

import streamlit as st

from streamlit_app.api_keys_io import (
    apply_imported_keys,
    export_api_keys_json,
    parse_imported_file,
)


def render_api_key_backup_section(key_suffix: str) -> None:
    """Export/import block for the 3 API keys. key_suffix uniquifies Streamlit widget keys."""
    st.markdown("### 🔐 Save / Restore Your API Keys")
    st.caption(
        "Export your keys to a file you keep locally, then import on next session — "
        "no need to re-enter them."
    )

    col_export, col_import = st.columns([1, 1])

    with col_export:
        st.download_button(
            label="📤 Export api_keys.json",
            data=export_api_keys_json(st.session_state),
            file_name="api_keys.json",
            mime="application/json",
            key=f"export_api_keys_{key_suffix}",
            use_container_width=True,
        )

    with col_import:
        show_flag = f"show_api_keys_import_{key_suffix}"
        if not st.session_state.get(show_flag):
            if st.button(
                "📥 Import api_keys.json",
                use_container_width=True,
                key=f"open_import_api_keys_{key_suffix}",
            ):
                st.session_state[show_flag] = True
                st.rerun()
        else:
            uploaded = st.file_uploader(
                "Choose api_keys.json",
                type=["json"],
                key=f"import_api_keys_{key_suffix}",
                label_visibility="collapsed",
            )
            if uploaded is not None:
                try:
                    keys = parse_imported_file(uploaded)
                    count = apply_imported_keys(st.session_state, keys)
                    st.session_state[show_flag] = False
                    st.success(f"✅ Imported {count} API key(s)")
                    st.rerun()
                except ValueError as e:
                    st.error(f"Import failed: {e}")
            if st.button("Cancel", key=f"cancel_api_keys_import_{key_suffix}"):
                st.session_state[show_flag] = False
                st.rerun()

    st.warning(
        "⚠️ This file contains your secret API keys. Don't share it or commit it to git.",
        icon="🔒",
    )
    st.markdown("---")
