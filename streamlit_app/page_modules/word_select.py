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

    # MAXIMUM 5 WORDS LIMIT - Clear messaging
    st.warning("⚠️ **Maximum 5 words per deck** - This keeps generation fast and API costs low!")
    
    # Initialize selected words if not exists
    if "selected_words" not in st.session_state:
        st.session_state.selected_words = []

    if "current_page" not in st.session_state:
        st.session_state.current_page = {}
    if st.session_state.get('selected_language', None) and st.session_state.get('selected_language') not in st.session_state.current_page:
        st.session_state.current_page[st.session_state.get('selected_language')] = 1

    # Show current selection summary with limit indicator
    selected_count = len(st.session_state.selected_words)
    remaining_slots = max(0, 5 - selected_count)
    
    if selected_count >= 5:
        st.error(f"❌ **Word limit reached!** You've selected the maximum of 5 words. Remove some words to add different ones.")
    elif selected_count > 0:
        st.success(f"✅ **{selected_count}/5 words selected** - {remaining_slots} slots remaining")
    else:
        st.info("ℹ️ **0/5 words selected** - Choose up to 5 words for your deck")
    
    st.markdown(f"### 📝 Current Selection: **{selected_count}/5 word(s)**")
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
        tab_frequency, tab_custom, tab_typed, tab_my_lists = st.tabs(["📊 Frequency List", "📥 Import Your Own Words", "✍️ Type Your Own Words", "📝 My Saved Lists"])

        with tab_frequency:
            page_size = 20  # Reduced to 20 for API cost control
            current_page = st.session_state.current_page[st.session_state.get('selected_language', '')]
            total_pages = (total_words + page_size - 1) // page_size

            st.markdown("#### Select words to include in your deck:")
            st.markdown(f"**Selected: {len(st.session_state.selected_words)}/5 words**")

            # Single-click selection with visual feedback
            for idx, row in words_df.iterrows():
                is_selected = row['Word'] in st.session_state.selected_words
                can_add_more = len(st.session_state.selected_words) < 5
                
                if is_selected:
                    button_text = f"✅ {row['Word']}"
                    button_type = "secondary"
                    disabled = False
                elif can_add_more:
                    button_text = f"➕ {row['Word']}"
                    button_type = "primary"
                    disabled = False
                else:
                    button_text = f"🚫 {row['Word']}"
                    button_type = "secondary"
                    disabled = True
                
                col1, col2 = st.columns([2, 1])
                with col1:
                    st.markdown(f"**#{row['Rank']}: {row['Word']}**")
                    if row['Completed']:
                        st.caption("✅ Completed")
                    else:
                        st.caption("Not studied")
                with col2:
                    if st.button(button_text, key=f"word_select_{row['Word']}_{idx}", 
                               type=button_type, use_container_width=True, disabled=disabled):
                        if is_selected:
                            st.session_state.selected_words.remove(row['Word'])
                        elif can_add_more:
                            st.session_state.selected_words.append(row['Word'])
                        # Don't add if limit reached
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

            # Save selected words option (only for signed-in users with selected words)
            from firebase_manager import is_signed_in
            if is_signed_in() and st.session_state.selected_words:
                st.divider()
                st.markdown("**💾 Save your selected words as a custom list**")

                col_save, col_name = st.columns([1, 2])
                with col_name:
                    frequency_list_name = st.text_input(
                        "List name",
                        key="frequency_list_name",
                        placeholder="e.g., Essential Vocabulary, Common Words",
                        help="Save your curated selection for future use"
                    )
                with col_save:
                    can_save_frequency = bool(frequency_list_name.strip())
                    if st.button("💾 Save Selection", key="save_frequency_list", type="secondary",
                               use_container_width=True, disabled=not can_save_frequency):
                        try:
                            from custom_lists_manager import save_custom_word_list
                            user_id = st.session_state.user['uid']
                            success = save_custom_word_list(
                                user_id=user_id,
                                list_name=frequency_list_name.strip(),
                                words=st.session_state.selected_words.copy(),  # Copy to avoid reference issues
                                language=st.session_state.get('selected_language')
                            )
                            if success:
                                st.success(f"✅ Selected words saved as '{frequency_list_name}'! You can reuse this list anytime.")
                                # Update achievements
                                from achievements_manager import check_and_update_achievements
                                check_and_update_achievements(user_id)
                            else:
                                st.error("❌ Failed to save word selection. Please try again.")
                        except Exception as e:
                            st.error(f"❌ Error saving selection: {e}")

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
                            can_add_more = len(st.session_state.selected_words) < 5
                            
                            if is_selected:
                                button_text = f"✅ {word}"
                                button_type = "secondary"
                                disabled = False
                            elif can_add_more:
                                button_text = f"➕ {row['Word']}"
                                button_type = "primary"
                                disabled = False
                            else:
                                button_text = f"🚫 {word}"
                                button_type = "secondary"
                                disabled = True
                            
                            col1, col2 = st.columns([3, 1])
                            with col1:
                                st.markdown(f"**{idx + 1}. {word}**")
                            with col2:
                                if st.button(button_text, key=f"custom_word_select_{word}_{idx}", 
                                           type=button_type, use_container_width=True, disabled=disabled):
                                    if is_selected:
                                        st.session_state.selected_words.remove(word)
                                    elif can_add_more:
                                        st.session_state.selected_words.append(word)
                                    # Don't add if limit reached
                                    st.rerun()

                        # Save custom list option (only for signed-in users)
                        from firebase_manager import is_signed_in
                        if is_signed_in() and custom_words:
                            st.divider()
                            st.markdown("**💾 Save this custom list for future use**")

                            col_save, col_name = st.columns([1, 2])
                            with col_name:
                                list_name = st.text_input(
                                    "List name",
                                    key="custom_list_name",
                                    placeholder="e.g., Medical Terms, Business Vocabulary",
                                    help="Give your word list a memorable name"
                                )
                            with col_save:
                                can_save = bool(list_name.strip())
                                if st.button("💾 Save List", key="save_custom_list", type="secondary",
                                           use_container_width=True, disabled=not can_save):
                                    try:
                                        from custom_lists_manager import save_custom_word_list
                                        user_id = st.session_state.user['uid']
                                        success = save_custom_word_list(
                                            user_id=user_id,
                                            list_name=list_name.strip(),
                                            words=custom_words,
                                            language=st.session_state.get('selected_language')
                                        )
                                        if success:
                                            st.success(f"✅ Custom list '{list_name}' saved! You can reuse it anytime.")
                                            # Update achievements
                                            from achievements_manager import check_and_update_achievements
                                            check_and_update_achievements(user_id)
                                        else:
                                            st.error("❌ Failed to save custom list. Please try again.")
                                    except Exception as e:
                                        st.error(f"❌ Error saving list: {e}")

                            # Show saved lists
                            try:
                                from custom_lists_manager import get_user_custom_lists
                                user_id = st.session_state.user['uid']
                                saved_lists = get_user_custom_lists(user_id)

                                if saved_lists:
                                    st.markdown("**📚 Your saved custom lists:**")
                                    for saved_list in saved_lists[:5]:  # Show up to 5
                                        col_info, col_load, col_delete = st.columns([2, 1, 1])
                                        with col_info:
                                            favorite_icon = "⭐" if saved_list['is_favorite'] else ""
                                            st.caption(f"{favorite_icon} {saved_list['name']} ({saved_list['word_count']} words)")
                                        with col_load:
                                            if st.button("📥 Load", key=f"load_list_{saved_list['id']}",
                                                       use_container_width=True):
                                                try:
                                                    from custom_lists_manager import get_custom_list_words
                                                    words, progress = get_custom_list_words(user_id, saved_list['id'])
                                                    if words:
                                                        # Replace current custom words
                                                        st.session_state.custom_words = words
                                                        st.success(f"✅ Loaded '{saved_list['name']}' with {len(words)} words!")
                                                        st.rerun()
                                                except Exception as e:
                                                    st.error(f"❌ Failed to load list: {e}")
                                        with col_delete:
                                            if st.button("🗑️", key=f"delete_list_{saved_list['id']}",
                                                       use_container_width=True):
                                                try:
                                                    from custom_lists_manager import delete_custom_list
                                                    success = delete_custom_list(user_id, saved_list['id'])
                                                    if success:
                                                        st.success(f"✅ Deleted '{saved_list['name']}'")
                                                        st.rerun()
                                                    else:
                                                        st.error("❌ Failed to delete list")
                                                except Exception as e:
                                                    st.error(f"❌ Error deleting list: {e}")
                            except Exception as e:
                                st.warning(f"Could not load saved lists: {e}")

        with tab_typed:
            remaining_slots = max(0, 5 - len(st.session_state.selected_words))
            st.markdown(f"""
            **Type or paste your own words below.**
            - Separate words with commas, spaces, or new lines.
            - Example: `apple, banana, orange` or one word per line.
            - **Maximum {remaining_slots} more words** (total limit: 5 words per deck).
            - Duplicates will be removed automatically.
            """)
            
            # Disable input if limit reached
            input_disabled = remaining_slots == 0
            if input_disabled:
                st.warning("⚠️ **Word limit reached!** You've already selected 5 words. Remove some words from your selection to add new ones.")
            
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
                key="typed_words_input",
                disabled=input_disabled
            )

            # Process Words button always visible, disabled when no content or limit reached
            can_process = typed_words_raw.strip() and not input_disabled
            if st.button("🔍 Process Words", key="process_typed_words", type="secondary", use_container_width=True, disabled=not can_process):
                # Process the words
                import re
                typed_words_list = re.split(r'[\s,\n]+', typed_words_raw)
                typed_words_list = [w.strip() for w in typed_words_list if w.strip()]
                typed_words_list = list(dict.fromkeys(typed_words_list))  # Remove duplicates
                
                # Respect the remaining slots limit
                available_slots = max(0, 5 - len(st.session_state.selected_words))
                typed_words_list = typed_words_list[:available_slots]

                if typed_words_list:
                    st.success(f"✅ **{len(typed_words_list)} word(s) processed!** Ready to add to your selection.")
                    st.session_state.processed_words = typed_words_list
                else:
                    if input_disabled:
                        st.warning("Cannot process words - word limit reached.")
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
                
                # Add words button - check if we can add more
                can_add_words = len(st.session_state.selected_words) < 5
                if not can_add_words:
                    st.warning("⚠️ **Cannot add more words** - you've reached the 5-word limit. Remove some words first.")
                
                col_add, col_clear = st.columns([1, 1])
                with col_add:
                    if st.button("➕ Add These Words", key="add_typed_words", type="primary", use_container_width=True, disabled=not can_add_words):
                        if can_add_words:
                            # Add to selected words, avoiding duplicates
                            existing_words = set(st.session_state.selected_words)
                            new_words = [w for w in typed_words_list if w not in existing_words]
                            
                            # Double-check we don't exceed limit
                            available_slots = max(0, 5 - len(st.session_state.selected_words))
                            new_words = new_words[:available_slots]
                            
                            st.session_state.selected_words.extend(new_words)
                            # Detailed confirmation
                            if new_words:
                                st.success(f"✅ Successfully added {len(new_words)} new word(s): {', '.join(new_words)}")
                                time.sleep(2)  # Keep the success message visible for 2 seconds
                                # Clear the text area using flag instead of direct session state modification
                                st.session_state.clear_typed_words_input = True
                            else:
                                st.info("All words were already in your selection or limit reached.")
                                time.sleep(2)  # Keep the info message visible for 2 seconds
                                # Clear the text area using flag instead of direct session state modification
                                st.session_state.clear_typed_words_input = True
                
                with col_clear:
                    if st.button("🗑️ Clear Text", key="clear_typed_words", use_container_width=True):
                        st.session_state.clear_typed_words_input = True
            else:
                st.info("Enter some words above to see them here.")

            # Save typed words option (only for signed-in users)
            from firebase_manager import is_signed_in
            if is_signed_in() and typed_words_list:
                st.divider()
                st.markdown("**💾 Save this word list for future use**")

                col_save, col_name = st.columns([1, 2])
                with col_name:
                    typed_list_name = st.text_input(
                        "List name",
                        key="typed_list_name",
                        placeholder="e.g., Medical Terms, Business Vocabulary",
                        help="Give your word list a memorable name"
                    )
                with col_save:
                    can_save_typed = bool(typed_list_name.strip())
                    if st.button("💾 Save List", key="save_typed_list", type="secondary",
                               use_container_width=True, disabled=not can_save_typed):
                        try:
                            from custom_lists_manager import save_custom_word_list
                            user_id = st.session_state.user['uid']
                            success = save_custom_word_list(
                                user_id=user_id,
                                list_name=typed_list_name.strip(),
                                words=typed_words_list,
                                language=st.session_state.get('selected_language')
                            )
                            if success:
                                st.success(f"✅ Typed word list '{typed_list_name}' saved! You can reuse it anytime.")
                                # Update achievements
                                from achievements_manager import check_and_update_achievements
                                check_and_update_achievements(user_id)
                            else:
                                st.error("❌ Failed to save typed word list. Please try again.")
                        except Exception as e:
                            st.error(f"❌ Error saving list: {e}")

            # Handle text area clearing with rerun
            if st.session_state.get('clear_typed_words_input', False):
                st.session_state.clear_typed_words_input = False
                st.rerun()

        with tab_my_lists:
            from firebase_manager import is_signed_in
            if not is_signed_in():
                st.info("🔐 Sign in to access your saved custom word lists.")
                if st.button("Sign In", key="signin_from_word_select"):
                    st.session_state.page = "auth_handler"
                    st.rerun()
            else:
                st.markdown("**Use your saved custom word lists** for deck generation.")

                # Check if a list was loaded from My Word Lists page
                loaded_list = st.session_state.get('loaded_custom_list')
                if loaded_list:
                    st.success(f"📥 **Loaded from 'My Word Lists':** {loaded_list['name']}")

                    words = loaded_list['words']
                    progress = loaded_list.get('progress', {})

                    st.markdown(f"#### Words from '{loaded_list['name']}' ({len(words)})")

                    # Show words with progress
                    for idx, word in enumerate(words[:100]):  # Limit display to 100
                        is_selected = word in st.session_state.selected_words
                        can_add_more = len(st.session_state.selected_words) < 10
                        is_completed = progress.get(word, {}).get('completed', False)

                        if is_selected:
                            button_text = f"✅ {word}"
                            button_type = "secondary"
                            disabled = False
                        elif can_add_more:
                            button_text = f"➕ {word}"
                            button_type = "primary"
                            disabled = False
                        else:
                            button_text = f"🚫 {word}"
                            button_type = "secondary"
                            disabled = True

                        col1, col2 = st.columns([3, 1])
                        with col1:
                            status_icon = "✅" if is_completed else "⬜"
                            st.markdown(f"**{idx + 1}. {status_icon} {word}**")
                        with col2:
                            if st.button(button_text, key=f"my_list_word_select_{word}_{idx}",
                                       type=button_type, use_container_width=True, disabled=disabled):
                                if is_selected:
                                    st.session_state.selected_words.remove(word)
                                elif can_add_more:
                                    st.session_state.selected_words.append(word)
                                # Don't add if limit reached
                                st.rerun()

                    # Clear loaded list button
                    if st.button("🗑️ Clear Loaded List", key="clear_loaded_list"):
                        del st.session_state.loaded_custom_list
                        st.rerun()

                else:
                    st.info("💡 No list loaded. Go to **My Word Lists** page to load a saved list, then return here to use it.")

                    # Quick access to My Word Lists page
                    if st.button("📝 Go to My Word Lists", key="goto_my_lists", type="secondary"):
                        st.session_state.page = "my_word_lists"
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
                st.rerun()

    # Scroll to top after all content is rendered
    st.markdown("""
    <script>
        setTimeout(function() {
            window.scrollTo({top: 0, behavior: 'smooth'});
        }, 1000);
    </script>
    """, unsafe_allow_html=True)