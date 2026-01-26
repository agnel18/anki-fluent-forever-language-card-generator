# pages/statistics.py - Statistics page for the language learning app

import streamlit as st
from constants import (
    GEMINI_CALL_LIMIT, GEMINI_TOKEN_LIMIT, GOOGLE_SEARCH_CALL_LIMIT,
    PAGE_LANGUAGE_SELECT, PAGE_LOGIN
)
from utils import fmt_num, usage_bar


def render_statistics_page():
    """Render the usage statistics and progress tracking page."""
    st.title("📊 Usage Statistics & Progress Tracking")

    # Back button
    if st.button("← Back to Main", key="back_to_main_stats"):
        st.session_state.page = "main"
        st.rerun()

    st.markdown("---")

    # Use persistent stats if logged in, else session stats
    stats = st.session_state.get("persistent_usage_stats") if not st.session_state.get("is_guest", True) else None
    if stats:
        gemini_calls = stats.get("gemini_calls", 0)
        gemini_tokens = stats.get("gemini_tokens", 0)
        google_search_calls = stats.get("google_search_calls", 0)
        decks_exported = stats.get("decks_exported", 0)
        cards_generated = stats.get("cards_generated", 0)
        images_downloaded = stats.get("images_downloaded", 0)
        audio_generated = stats.get("audio_generated", 0)
        api_errors = stats.get("api_errors", 0)
        per_language = stats.get("per_language", {})
    else:
        gemini_calls = st.session_state.get("gemini_api_calls", 0)
        gemini_tokens = st.session_state.get("gemini_tokens_used", 0)
        google_search_calls = st.session_state.get("google_search_api_calls", 0)
        decks_exported = st.session_state.get("decks_exported", 0)
        cards_generated = st.session_state.get("cards_generated", 0)
        images_downloaded = st.session_state.get("images_downloaded", 0)
        audio_generated = st.session_state.get("audio_generated", 0)
        api_errors = st.session_state.get("api_errors", 0)
        per_language = {}

    st.markdown("#### API Usage")
    st.markdown("*Track your usage of external AI and image services*")
    st.markdown(f"Gemini Calls: {fmt_num(gemini_calls)} / {fmt_num(GEMINI_CALL_LIMIT)}", unsafe_allow_html=True)
    st.markdown(usage_bar(gemini_calls, GEMINI_CALL_LIMIT), unsafe_allow_html=True)
    st.caption("🤖 Gemini API calls for generating sentences and translations")
    st.markdown(f"Gemini Tokens: {fmt_num(gemini_tokens)} / {fmt_num(GEMINI_TOKEN_LIMIT)}", unsafe_allow_html=True)
    st.markdown(usage_bar(gemini_tokens, GEMINI_TOKEN_LIMIT), unsafe_allow_html=True)
    st.caption("📊 Text tokens processed by Gemini AI (includes prompts and responses)")
    st.markdown(f"Google Search Calls: {fmt_num(google_search_calls)} / {fmt_num(GOOGLE_SEARCH_CALL_LIMIT)}", unsafe_allow_html=True)
    st.markdown(usage_bar(google_search_calls, GOOGLE_SEARCH_CALL_LIMIT), unsafe_allow_html=True)
    st.caption("🖼️ Image searches on Google Custom Search for word illustrations")
    st.markdown("---")

    # Enhanced Cost Calculator Section
    st.markdown("#### 💰 Cost Calculator & Usage Costs")
    st.markdown("*Track your actual API costs and estimate future expenses*")

    # Actual costs section
    st.markdown("**📊 Your Actual Costs This Session:**")
    col_actual1, col_actual2 = st.columns(2)

    with col_actual1:
        # Calculate actual costs based on usage
        gemini_cost = gemini_tokens * 0.0000001  # $0.10 per 1M tokens
        search_cost = google_search_calls * 0.005  # $5 per 1000 searches
        tts_cost = audio_generated * 0.0024  # Rough estimate for Standard voice

        st.metric("Gemini API Cost", f"${gemini_cost:.4f}")
        st.metric("Image Search Cost", f"${search_cost:.4f}")
        st.caption("🤖 Text generation & translation")

    with col_actual2:
        st.metric("TTS Audio Cost", f"${tts_cost:.4f}")
        total_actual = gemini_cost + search_cost + tts_cost
        st.metric("**Total Cost**", f"${total_actual:.4f}", delta=f"{fmt_num(cards_generated)} cards generated")
        st.caption("🔊 Audio generation (Standard voice)")

    # Free tier impact
    free_tier_remaining = max(0, 1000 - gemini_tokens)  # Assuming 1000 free tokens
    if free_tier_remaining > 0:
        st.info(f"💡 **Free Tier Remaining:** {fmt_num(free_tier_remaining)} Gemini tokens left in free tier")
    else:
        st.warning("⚠️ **Free Tier Exceeded:** You're now paying for Gemini API usage")

    st.markdown("---")

    # Enhanced cost estimator
    st.markdown("**🧮 Cost Estimator - Plan Your Next Deck:**")
    col_est1, col_est2 = st.columns(2)

    with col_est1:
        est_sentences = st.number_input(
            "Sentences per card:",
            min_value=1,
            max_value=20,
            value=10,
            help="How many sentences will be generated per word"
        )

        est_cards = st.number_input(
            "Cards to generate:",
            min_value=1,
            max_value=1000,
            value=50,
            help="How many Anki cards you plan to generate"
        )

        voice_options = {
            "Standard (Default)": 0.000016,
            "Chirp3 (Budget)": 0.000004,
            "Chirp3 HD": 0.00002,
            "Wavenet": 0.000032,
            "Neural2": 0.000024
        }

        selected_voice = st.selectbox(
            "Voice Type:",
            list(voice_options.keys()),
            index=0,
            help="Choose voice type for cost estimation"
        )

    with col_est2:
        # Calculate estimated costs
        total_chars = est_sentences * est_cards * 80  # Rough estimate: 80 chars per sentence
        voice_cost_per_char = voice_options[selected_voice]
        est_tts_cost = total_chars * voice_cost_per_char

        # Estimate Gemini usage (rough calculation)
        est_gemini_tokens = est_cards * 1500  # Rough estimate: 1500 tokens per card
        est_gemini_cost = est_gemini_tokens * 0.0000001

        # Estimate image searches (1-2 per card)
        est_search_calls = est_cards * 1.5
        est_search_cost = est_search_calls * 0.005

        total_estimated = est_gemini_cost + est_search_cost + est_tts_cost

        st.markdown("**Estimated Costs:**")
        st.info(f"""
        **Gemini API:** ${est_gemini_cost:.4f} ({fmt_num(est_gemini_tokens)} tokens)  
        **Image Search:** ${est_search_cost:.4f} ({fmt_num(int(est_search_calls))} calls)  
        **TTS Audio ({selected_voice}):** ${est_tts_cost:.4f}  
        **Total Estimated:** ${total_estimated:.4f}
        """)

        # Cost per card
        cost_per_card = total_estimated / est_cards if est_cards > 0 else 0
        st.metric("Cost per Card", f"${cost_per_card:.4f}")

    # Cost optimization tips
    with st.expander("💡 Cost Optimization Tips", expanded=False):
        st.markdown("""
        **🎯 Cost-Saving Strategies:**
        - **Voice Selection:** Standard voice offers best quality/cost ratio
        - **Batch Processing:** Generate larger decks less frequently
        - **Free Tier:** Stay under 1000 Gemini tokens for free usage
        - **Image Reuse:** App caches images to avoid repeated downloads

        **📈 Scaling Costs:**
        - 50 cards: ~$0.15-0.30 (depending on voice)
        - 100 cards: ~$0.30-0.60
        - 500 cards: ~$1.50-3.00

        **⚠️ Hidden Costs:**
        - Premium voices can 2-3x cost of Standard
        - Complex sentences use more Gemini tokens
        - High-quality images may cost more in search API
        """)

    st.markdown("---")

    st.markdown("#### Generation & Export Stats")
    st.markdown("*Your deck creation and content generation activity*")
    st.metric("Decks Exported", decks_exported)
    st.caption("📚 Complete Anki decks you've downloaded")
    st.metric("Cards Generated", cards_generated)
    st.caption("🃏 Individual flashcards created across all decks")
    st.metric("Images Downloaded", images_downloaded)
    st.caption("📷 Images fetched for word illustrations")
    st.metric("Audio Generated", audio_generated)
    st.caption("🔊 Audio pronunciations created for words")
    st.metric("API Errors", api_errors)
    st.caption("❌ Failed API calls (network issues, rate limits, etc.)")
    st.markdown("---")

    if per_language:
        st.markdown("#### Per-Language Usage")
        st.markdown("*Breakdown of your activity by language*")
        for lang, lang_stats in per_language.items():
            st.markdown(f"**{lang}**")
            st.write({k: v for k, v in lang_stats.items() if isinstance(v, int)})

    st.markdown("---")

    # Achievements Section (for both signed-in users and guests)
    from firebase_manager import is_signed_in
    show_achievements = is_signed_in()

    # For guest users, show achievements based on session data
    if not show_achievements:
        # Always show achievements for guests so they can see what's available
        show_achievements = True

    if show_achievements:
        st.markdown("## 🏆 Achievements")
        st.markdown("*Track your learning milestones and accomplishments*")
        st.caption("🎯 Unlock achievements by using the app, generating decks, and learning new languages!")

        try:
            if is_signed_in():
                # Signed-in user achievements
                from achievements_manager import get_user_achievements, get_achievement_stats, get_recent_unlocks
                user_id = st.session_state.user['uid']
                achievements = get_user_achievements(user_id)
                stats = get_achievement_stats(user_id)
                recent_unlocks = get_recent_unlocks(user_id, days=30)
                is_guest = False
            else:
                # Guest user achievements (simplified)
                from achievements_manager import ACHIEVEMENTS
                # Calculate progress for each achievement based on session data
                achievements = []
                for ach in ACHIEVEMENTS:
                    # Calculate progress based on achievement type
                    if ach.key in ["first_deck", "deck_collector", "deck_master", "deck_legend"]:
                        progress = decks_exported
                    elif ach.key in ["word_smith", "word_weaver", "word_wizard"]:
                        progress = cards_generated
                    elif ach.key in ["first_day", "week_warrior", "month_master"]:
                        # For guest users, we can't track actual usage days, so show as locked
                        progress = 0
                    elif ach.key in ["polyglot_start", "polyglot", "linguist"]:
                        # For guest users, we can't track languages used, so show as locked
                        progress = 0
                    else:
                        progress = 0

                    # Determine if achievement is unlocked
                    unlocked = progress >= ach.target_value

                    # Calculate progress percentage
                    progress_pct = min(100, (progress / ach.target_value) * 100) if ach.target_value > 0 else 0

                    achievements.append({
                        'type': ach.type, 'key': ach.key, 'title': ach.title,
                        'description': ach.description, 'icon': ach.icon,
                        'unlocked': unlocked, 'progress': progress,
                        'target': ach.target_value, 'progress_percentage': progress_pct
                    })

                stats = {'completion_percentage': sum(1 for a in achievements if a['unlocked']) / len(achievements) * 100}
                recent_unlocks = []  # No recent unlocks tracking for guests
                is_guest = True

            # Overall progress
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Achievements", len(achievements))
            with col2:
                unlocked_count = sum(1 for a in achievements if a['unlocked'])
                st.metric("Unlocked", unlocked_count)
            with col3:
                completion_pct = stats.get('completion_percentage', 0)
                st.metric("Completion", f"{completion_pct:.1f}%")

            # Progress bar
            st.progress(completion_pct / 100)
            st.caption(f"{unlocked_count} of {len(achievements)} achievements unlocked")

            if is_guest:
                st.info("💡 **Guest Mode**: Achievements are based on your current session. Sign in to save progress permanently and unlock time-based achievements!")

            # Achievement explanation
            with st.expander("ℹ️ How Achievements Work", expanded=False):
                st.markdown("""
                **Achievement Categories:**
                - **Usage**: Daily app usage and streaks
                - **Creation**: Deck generation and content creation milestones
                - **Languages**: Learning multiple languages

                **For Signed-in Users:**
                - Persistent progress tracking across sessions
                - Time-based achievements (daily usage streaks)
                - Recent unlocks showcase
                - Cloud synchronization

                **For Guest Users:**
                - Session-based progress (resets when app restarts)
                - Creation-based achievements (decks, cards generated)
                - Language achievements not available (requires persistent tracking)
                """)

            # Recent unlocks (only for signed-in users)
            if not is_guest and recent_unlocks:
                st.markdown("### 🎉 Recent Unlocks")
                cols = st.columns(min(len(recent_unlocks), 3))
                for i, achievement in enumerate(recent_unlocks[:3]):
                    with cols[i]:
                        st.markdown(f"""
                        <div style="text-align: center; padding: 10px; border: 1px solid var(--card-border); border-radius: 5px; background-color: var(--card-bg); color: var(--text-color);">
                            <div style="font-size: 2em;">{achievement['icon']}</div>
                            <div style="font-weight: bold; color: var(--text-color);">{achievement['title']}</div>
                            <div style="font-size: 0.8em; color: var(--subtle-text);">{achievement['description'][:50]}...</div>
                        </div>
                        """, unsafe_allow_html=True)

            # Achievement categories
            st.markdown("### 📂 Achievement Categories")

            # Group achievements by category
            categories = {}
            for achievement in achievements:
                category = achievement['type']
                if category not in categories:
                    categories[category] = []
                categories[category].append(achievement)

            # Display each category
            for category_name, category_achievements in categories.items():
                with st.expander(f"**{category_name.title()} Achievements** ({sum(1 for a in category_achievements if a['unlocked'])}/{len(category_achievements)})", expanded=False):
                    cols = st.columns(2)
                    for i, achievement in enumerate(category_achievements):
                        with cols[i % 2]:
                            # Achievement card - theme-aware colors
                            if achievement['unlocked']:
                                border_color = "var(--success-border)"
                                bg_color = "var(--success-bg)"
                                text_color = "var(--text-color)"
                                desc_color = "var(--subtle-text)"
                            else:
                                border_color = "var(--card-border)"
                                bg_color = "var(--card-bg)"
                                text_color = "var(--text-color)"
                                desc_color = "var(--subtle-text)"

                            st.markdown(f"""
                            <div style="border: 2px solid {border_color}; border-radius: 10px; padding: 15px; margin: 5px 0; background-color: {bg_color}; color: {text_color};">
                                <div style="display: flex; align-items: center; margin-bottom: 10px;">
                                    <span style="font-size: 1.5em; margin-right: 10px;">{achievement['icon']}</span>
                                    <div>
                                        <div style="font-weight: bold; font-size: 1.1em; color: {text_color};">{achievement['title']}</div>
                                        <div style="font-size: 0.9em; color: {desc_color}; margin-bottom: 5px;">{achievement['description']}</div>
                                        <div style="font-size: 0.8em; color: {desc_color};">Target: {achievement['target']} | Current: {achievement['progress']}</div>
                                    </div>
                                </div>
                            """, unsafe_allow_html=True)

                            # Progress bar for locked achievements
                            if not achievement['unlocked']:
                                progress_pct = achievement['progress_percentage']
                                st.progress(progress_pct / 100)
                                st.caption(f"{achievement['progress']}/{achievement['target']} ({progress_pct:.1f}%)")
                            else:
                                st.success("✅ Unlocked!")

                            st.markdown("</div>", unsafe_allow_html=True)

        except Exception as e:
            st.warning(f"Could not load achievements: {e}")

        st.markdown("---")

    st.caption("Counts update live as you generate decks. Persistent stats for logged-in users, session stats for guests. Achievements available for both signed-in users and guests!")

    if st.button("⬅️ Back", key="stats_back_btn"):
        st.session_state.page = PAGE_LANGUAGE_SELECT if st.session_state.get("first_run_complete", False) else PAGE_LOGIN
        st.rerun()