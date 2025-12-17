# pages/word_select.py - Word selection page for the language learning app

import streamlit as st
import re
import time
from frequency_utils import get_words_with_ranks, parse_uploaded_word_file, validate_word_list


def render_word_select_page():
    """Render the word selection page."""
    st.markdown("# 🌍 Step 2: Select Words")
    st.markdown("Choose words to include in your language learning deck.")

    # Progress indicator
    st.markdown("**Progress:** Step 2 of 5")
    st.progress(0.4)

    st.markdown("---")

    # Initialize selected words if not exists
    if "selected_words" not in st.session_state:
        st.session_state.selected_words = []

    if "current_page" not in st.session_state:
        st.session_state.current_page = {}
    if st.session_state.get('selected_language', None) and st.session_state.get('selected_language') not in st.session_state.current_page:
        st.session_state.current_page[st.session_state.get('selected_language')] = 1

    # Show current selection summary
    selected_count = len(st.session_state.selected_words)
    st.markdown(f"### 📝 Current Selection: **{selected_count} word(s)**")
    if selected_count > 0:
        with st.expander("View selected words", expanded=False):
            if selected_count <= 20:
                st.write(", ".join(st.session_state.selected_words))
            else:
                cols = st.columns(3)
                words_per_col = (selected_count + 2) // 3
                for i in range(3):
                    start_idx = i * words_per_col
                    end_idx = min((i + 1) * words_per_col, selected_count)
                    if start_idx < end_idx:
                        cols[i].write("• " + "\n• ".join(st.session_state.selected_words[start_idx:end_idx]))

    try:
        # Limit to 20 words per page to reduce API costs
        words_df, total_words = get_words_with_ranks(st.session_state.get('selected_language', ''), page=st.session_state.current_page[st.session_state.get('selected_language', '')], page_size=20)
    except Exception as e:
        st.error(f"Error loading words: {e}")
        return

    # Initialize variables
    uploaded_file_name = None
    custom_words = []
    typed_words_raw = ""

    if total_words > 0:
        st.markdown(f"### Pick from **Top Words Used in** {st.session_state.get('selected_language', '')}")
        # Add third option: Type Your Own Words
        tab_frequency, tab_custom, tab_typed = st.tabs(["📊 Frequency List", "📥 Import Your Own Words", "✍️ Type Your Own Words"])

        with tab_typed:
            st.markdown("""
            **Type or paste your own words below.**
            - Separate words with commas, spaces, or new lines.
            - Example: `apple, banana, orange` or one word per line.
            - Max 10 words per batch. Recommended: 5-10 words for optimal processing. Duplicates will be removed.
            """)
            # Text area for manual word input
            # Use a flag to control clearing instead of modifying session state directly
            clear_text_area = st.session_state.get('clear_typed_words_input', False)
            if clear_text_area:
                st.session_state.clear_typed_words_input = False
                default_value = ""
            else:
                default_value = ""

            typed_words_raw = st.text_area(
                "Enter your words:",
                value=default_value,
                height=120,
                placeholder="e.g. apple, banana, orange or one per line",
                key="typed_words_input"
            )

            # Process Words button always visible, disabled when no content
            if st.button("🔍 Process Words", key="process_typed_words", type="secondary", use_container_width=True, disabled=not typed_words_raw.strip()):
                # Process the words
                import re
                typed_words_list = re.split(r'[\s,\n]+', typed_words_raw)
                typed_words_list = [w.strip() for w in typed_words_list if w.strip()]
                typed_words_list = list(dict.fromkeys(typed_words_list))[:10]  # Remove duplicates and limit

                if typed_words_list:
                    st.success(f"✅ **{len(typed_words_list)} word(s) processed!** Ready to add to your selection.")
                    st.session_state.processed_words = typed_words_list
                else:
                    st.warning("No valid words found. Please enter some words.")
                    st.session_state.processed_words = []

            # Check if words are processed
            if 'processed_words' in st.session_state and st.session_state.processed_words:
                typed_words_list = st.session_state.processed_words
            else:
                typed_words_list = []

            # Process and display typed words
            if typed_words_list:
                st.success(f"✅ **{len(typed_words_list)} word(s) ready to add**")
                
                # Show preview of words
                with st.expander("📋 Preview words to be added", expanded=False):
                    cols = st.columns(3)
                    for i, word in enumerate(typed_words_list):
                        cols[i % 3].write(f"• {word}")
                
                # Add words button
                col_add, col_clear = st.columns([1, 1])
                with col_add:
                    if st.button("➕ Add These Words", key="add_typed_words", type="primary", use_container_width=True):
                        # Add to selected words, avoiding duplicates
                        existing_words = set(st.session_state.selected_words)
                        new_words = [w for w in typed_words_list if w not in existing_words]
                        st.session_state.selected_words.extend(new_words)
                        # Detailed confirmation
                        if new_words:
                            st.success(f"✅ Successfully added {len(new_words)} new word(s): {', '.join(new_words)}")
                            time.sleep(2)  # Keep the success message visible for 2 seconds
                            # Clear the text area using flag instead of direct session state modification
                            st.session_state.clear_typed_words_input = True
                        else:
                            st.info("All words were already in your selection.")
                            time.sleep(2)  # Keep the info message visible for 2 seconds
                            # Clear the text area using flag instead of direct session state modification
                            st.session_state.clear_typed_words_input = True
                
                with col_clear:
                    if st.button("🗑️ Clear Text", key="clear_typed_words", use_container_width=True):
                        st.session_state.clear_typed_words_input = True
            else:
                st.info("Enter some words above to see them here.")

            # Handle text area clearing with rerun
            if st.session_state.get('clear_typed_words_input', False):
                st.session_state.clear_typed_words_input = False
                st.rerun()

        with tab_frequency:
            page_size = 20  # Reduced to 20 for API cost control
            current_page = st.session_state.current_page[st.session_state.get('selected_language', '')]
            total_pages = (total_words + page_size - 1) // page_size

            st.markdown("#### Select words to include in your deck:")
            st.markdown(f"**Selected: {len(st.session_state.selected_words)} words**")

            # Single-click selection with visual feedback
            for idx, row in words_df.iterrows():
                is_selected = row['Word'] in st.session_state.selected_words
                button_text = f"✅ {row['Word']}" if is_selected else f"➕ {row['Word']}"
                button_type = "secondary" if is_selected else "primary"
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**#{row['Rank']}: {row['Word']}**")
                    if row['Completed']:
                        st.caption("✅ Completed")
                    else:
                        st.caption("Not studied")
                with col2:
                    if st.button(button_text, key=f"word_select_{row['Word']}_{idx}", 
                               type=button_type, use_container_width=True):
                        if is_selected:
                            st.session_state.selected_words.remove(row['Word'])
                        else:
                            st.session_state.selected_words.append(row['Word'])
                        st.rerun()

            st.divider()
            start_rank = (current_page - 1) * page_size + 1
            end_rank = min(current_page * page_size, total_words)
            st.markdown(f"**Top {start_rank}–{end_rank}** | Page {current_page} of {total_pages}")

            col_prev, col_next, col_jump = st.columns([1, 1, 2])
            with col_prev:
                if st.button("⬅️ Previous", key="prev_page"):
                    if current_page > 1:
                        st.session_state.current_page[st.session_state.get('selected_language', '')] -= 1
                        st.rerun()
            with col_next:
                if st.button("Next ➡️", key="next_page"):
                    if current_page < total_pages:
                        st.session_state.current_page[st.session_state.get('selected_language', '')] += 1
                        st.rerun()
            with col_jump:
                if total_pages > 1:
                    jump_page = st.number_input("Jump to page", min_value=1, max_value=total_pages, value=current_page, key="jump_page")
                    if jump_page != current_page:
                        st.session_state.current_page[st.session_state.get('selected_language', '')] = jump_page
                        st.rerun()

        with tab_custom:
            st.markdown("**Import your own list of words** for exams, specific topics, or custom learning needs.")
            st.divider()
            st.markdown("**Expected format:** One word per line (plain text, CSV, or XLSX)")
            uploaded_file = st.file_uploader(
                "Choose CSV or XLSX file",
                type=['csv', 'xlsx', 'xls'],
                key="custom_words_upload",
                help="First column will be used as word list"
            )
            if uploaded_file:
                uploaded_file_name = uploaded_file.name if hasattr(uploaded_file, 'name') else None
                st.info(f"Custom word import detected: {uploaded_file_name}")
                custom_words, parse_msg = parse_uploaded_word_file(uploaded_file)
                st.info(parse_msg)
                if custom_words:
                    is_valid, validation_msg = validate_word_list(custom_words)
                    st.info(validation_msg)
                    if is_valid:
                        st.markdown(f"#### Words from custom list ({len(custom_words)})")
                        for idx, word in enumerate(custom_words[:100]):  # Limit display to 100
                            is_selected = word in st.session_state.selected_words
                            button_text = f"✅ {word}" if is_selected else f"➕ {word}"
                            button_type = "secondary" if is_selected else "primary"
                            
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{idx + 1}. {word}**")
                            with col2:
                                if st.button(button_text, key=f"custom_word_select_{word}_{idx}", 
                                           type=button_type, use_container_width=True):
                                    if is_selected:
                                        st.session_state.selected_words.remove(word)
                                    else:
                                        st.session_state.selected_words.append(word)
                                    st.rerun()
    else:
        st.warning("No frequency data available for the selected language. Please use the custom import or type your own words.")

    # Store variables for the next button
    st.session_state.custom_words = custom_words
    st.session_state.typed_words_raw = typed_words_raw

    st.markdown("---")

    # Navigation buttons at the bottom
    col_back, col_next = st.columns([1, 1])
    with col_back:
        if st.button("⬅️ Back to Language Selection", key="back_from_word_select", use_container_width=True):
            st.session_state.page = "language_select"
            st.session_state.scroll_to_top = True
            st.rerun()
    with col_next:
        if st.button("Next: Adjust Output Settings ➡️", key="next_from_word_select", use_container_width=True, type="primary"):
            # Use selected words (which may include typed words that were added)
            words_to_use = st.session_state.selected_words
            
            # If no selected words, try to process typed words as fallback
            if not words_to_use and typed_words_raw.strip():
                # Split by comma, newline, or space, remove duplicates and empty
                import re
                words = re.split(r'[\s,\n]+', typed_words_raw)
                words_to_use = [w.strip() for w in words if w.strip()]
            
            # Remove duplicates and limit to 10 words
            words_to_use = list(dict.fromkeys(words_to_use))[:10]
            st.session_state.selected_words = words_to_use
            
            if not words_to_use:
                st.error("Please select or enter at least one word.")
            else:
                st.session_state.page = "sentence_settings"
                st.session_state.scroll_to_top = True
                st.rerun()