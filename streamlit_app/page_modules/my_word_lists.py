# page_modules/my_word_lists.py - Custom word lists management page

import streamlit as st
import json
from firebase_manager import is_signed_in
from custom_lists_manager import (
    get_user_custom_lists, get_custom_list_words, save_custom_word_list,
    delete_custom_list, toggle_favorite_list, get_custom_list_stats
)
from frequency_utils import validate_word_list


def render_my_word_lists_page():
    """Render the custom word lists management page."""
    st.title("📝 My Custom Word Lists")

    # Back button
    if st.button("← Back to Main", key="back_to_main_lists"):
        st.session_state.page = "main"
        st.rerun()

    st.markdown("---")

    # Check if user is signed in
    if not is_signed_in():
        st.warning("🔐 Please sign in to manage your custom word lists.")
        if st.button("Sign In", key="signin_from_lists"):
            st.session_state.page = "auth_handler"
            st.rerun()
        return

    user_id = st.session_state.user['uid']
    user_name = st.session_state.user.get('displayName', 'User')

    st.markdown(f"**Welcome back, {user_name}!** Manage your custom word lists below.")

    # Get user's custom lists
    try:
        custom_lists = get_user_custom_lists(user_id)
    except Exception as e:
        st.error(f"Failed to load your word lists: {e}")
        return

    # Create new list section
    st.markdown("## ➕ Create New List")
    with st.expander("Create a new custom word list", expanded=False):
        with st.form("create_list_form"):
            col1, col2 = st.columns([2, 1])
            with col1:
                list_name = st.text_input("List Name", placeholder="e.g., Medical Terms, Business Vocabulary")
            with col2:
                language = st.selectbox("Language (optional)", [""] + [
                    "English", "Spanish", "French", "German", "Italian", "Portuguese",
                    "Chinese", "Japanese", "Korean", "Arabic", "Hindi", "Russian"
                ])

            words_input = st.text_area(
                "Words (one per line or comma-separated)",
                height=150,
                placeholder="apple\nbanana\norange\n\nor: apple, banana, orange"
            )

            submitted = st.form_submit_button("Create List", type="primary")

            if submitted:
                if not list_name.strip():
                    st.error("Please enter a list name.")
                    return

                if not words_input.strip():
                    st.error("Please enter some words.")
                    return

                # Process words
                import re
                words = re.split(r'[\s,\n]+', words_input)
                words = [w.strip() for w in words if w.strip()]
                words = list(dict.fromkeys(words))  # Remove duplicates

                if not words:
                    st.error("No valid words found. Please enter words separated by commas or new lines.")
                    return

                # Validate words
                is_valid, message = validate_word_list(words)
                if not is_valid:
                    st.error(f"Invalid word list: {message}")
                    return

                # Save the list
                try:
                    success = save_custom_word_list(
                        user_id=user_id,
                        list_name=list_name.strip(),
                        words=words,
                        language=language if language else None
                    )

                    if success:
                        st.success(f"✅ Created '{list_name}' with {len(words)} words!")
                        st.rerun()  # Refresh to show new list
                    else:
                        st.error("Failed to save the list. Please try again.")

                except Exception as e:
                    st.error(f"Error creating list: {e}")

    st.markdown("---")

    # Existing lists section
    if custom_lists:
        st.markdown(f"## 📚 Your Word Lists ({len(custom_lists)})")

        # Sort by favorite first, then by last used
        custom_lists.sort(key=lambda x: (not x['is_favorite'], x['last_used'] or ''), reverse=True)

        for list_info in custom_lists:
            with st.expander(
                f"{'⭐ ' if list_info['is_favorite'] else ''}{list_info['name']} ({list_info['word_count']} words)",
                expanded=False
            ):
                col1, col2, col3 = st.columns([2, 1, 1])

                with col1:
                    st.markdown(f"**Language:** {list_info['language'] or 'Not specified'}")
                    st.markdown(f"**Created:** {list_info['created_at'][:10] if list_info['created_at'] else 'Unknown'}")
                    if list_info['last_used']:
                        st.markdown(f"**Last used:** {list_info['last_used'][:10]}")

                    # Show stats
                    try:
                        stats = get_custom_list_stats(user_id, list_info['id'])
                        col_a, col_b, col_c = st.columns(3)
                        with col_a:
                            st.metric("Total Words", stats['total_words'])
                        with col_b:
                            st.metric("Completed", f"{stats['completed_words']} ({stats['completion_percentage']:.1f}%)")
                        with col_c:
                            st.metric("Times Generated", stats['total_generations'])
                    except Exception as e:
                        st.caption(f"Could not load stats: {e}")

                with col2:
                    if st.button("📥 Load for Generation", key=f"load_{list_info['id']}", use_container_width=True):
                        try:
                            words, progress = get_custom_list_words(user_id, list_info['id'])
                            if words:
                                # Store in session state for use in word selection
                                st.session_state.loaded_custom_list = {
                                    'name': list_info['name'],
                                    'words': words,
                                    'progress': progress
                                }
                                st.success(f"✅ Loaded '{list_info['name']}'! Go to word selection to use it.")
                                st.info("💡 Tip: In word selection, switch to 'Import Your Own Words' tab to see your loaded list.")
                            else:
                                st.error("Failed to load words from this list.")
                        except Exception as e:
                            st.error(f"Error loading list: {e}")

                    # Favorite toggle
                    favorite_text = "☆ Remove Favorite" if list_info['is_favorite'] else "⭐ Add Favorite"
                    if st.button(favorite_text, key=f"favorite_{list_info['id']}", use_container_width=True):
                        try:
                            success = toggle_favorite_list(user_id, list_info['id'])
                            if success:
                                st.success("Updated favorite status!")
                                st.rerun()
                            else:
                                st.error("Failed to update favorite status.")
                        except Exception as e:
                            st.error(f"Error updating favorite: {e}")

                with col3:
                    # Preview words
                    if st.button("👁️ Preview", key=f"preview_{list_info['id']}", use_container_width=True):
                        try:
                            words, progress = get_custom_list_words(user_id, list_info['id'])
                            if words:
                                st.markdown("**Words in this list:**")
                                preview_words = words[:20]  # Show first 20
                                cols = st.columns(3)
                                for i, word in enumerate(preview_words):
                                    completed = progress.get(word, {}).get('completed', False)
                                    status_icon = "✅" if completed else "⬜"
                                    cols[i % 3].write(f"{status_icon} {word}")

                                if len(words) > 20:
                                    st.caption(f"... and {len(words) - 20} more words")
                            else:
                                st.error("Could not load words for preview.")
                        except Exception as e:
                            st.error(f"Error previewing list: {e}")

                    # Delete button (with confirmation)
                    if st.button("🗑️ Delete", key=f"delete_{list_info['id']}", use_container_width=True):
                        st.session_state.delete_list_id = list_info['id']
                        st.session_state.delete_list_name = list_info['name']

                    # Show delete confirmation if this list is marked for deletion
                    if (st.session_state.get('delete_list_id') == list_info['id'] and
                        st.session_state.get('delete_list_name') == list_info['name']):

                        st.error(f"⚠️ Really delete '{list_info['name']}'? This cannot be undone!")

                        col_confirm, col_cancel = st.columns(2)
                        with col_confirm:
                            if st.button("✅ Yes, Delete", key=f"confirm_delete_{list_info['id']}", type="primary"):
                                try:
                                    success = delete_custom_list(user_id, list_info['id'])
                                    if success:
                                        st.success(f"✅ Deleted '{list_info['name']}'")
                                        # Clear delete state
                                        del st.session_state.delete_list_id
                                        del st.session_state.delete_list_name
                                        st.rerun()
                                    else:
                                        st.error("Failed to delete the list.")
                                except Exception as e:
                                    st.error(f"Error deleting list: {e}")

                        with col_cancel:
                            if st.button("❌ Cancel", key=f"cancel_delete_{list_info['id']}"):
                                del st.session_state.delete_list_id
                                del st.session_state.delete_list_name
                                st.rerun()

    else:
        # No lists yet
        st.markdown("## 📝 No Custom Lists Yet")
        st.info("Create your first custom word list using the form above! You can upload word lists for exams, specific topics, or any vocabulary you want to learn.")

        # Show example
        with st.expander("💡 Example: How to create a list", expanded=False):
            st.markdown("""
            **List Name:** Medical Terminology

            **Words (one per line):**
            ```
            hypertension
            myocardial
            infarction
            diabetes
            mellitus
            chemotherapy
            radiology
            diagnosis
            prognosis
            ```

            This will create a custom list you can use to generate Anki decks focused on medical vocabulary!
            """)

    st.markdown("---")
    st.caption("💡 Tip: Favorite lists appear at the top. Use 'Load for Generation' to use a list in the deck creation process.")