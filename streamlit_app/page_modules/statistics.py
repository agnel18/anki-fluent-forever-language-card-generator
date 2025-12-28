# pages/statistics.py - Statistics page for the language learning app

import streamlit as st
from constants import (
    GROQ_CALL_LIMIT, GROQ_TOKEN_LIMIT, PIXABAY_CALL_LIMIT,
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
        groq_calls = stats.get("groq_calls", 0)
        groq_tokens = stats.get("groq_tokens", 0)
        pixabay_calls = stats.get("pixabay_calls", 0)
        decks_exported = stats.get("decks_exported", 0)
        cards_generated = stats.get("cards_generated", 0)
        images_downloaded = stats.get("images_downloaded", 0)
        audio_generated = stats.get("audio_generated", 0)
        api_errors = stats.get("api_errors", 0)
        per_language = stats.get("per_language", {})
    else:
        groq_calls = st.session_state.get("groq_api_calls", 0)
        groq_tokens = st.session_state.get("groq_tokens_used", 0)
        pixabay_calls = st.session_state.get("pixabay_api_calls", 0)
        decks_exported = st.session_state.get("decks_exported", 0)
        cards_generated = st.session_state.get("cards_generated", 0)
        images_downloaded = st.session_state.get("images_downloaded", 0)
        audio_generated = st.session_state.get("audio_generated", 0)
        api_errors = st.session_state.get("api_errors", 0)
        per_language = {}

    st.markdown("#### API Usage")
    st.markdown("*Track your usage of external AI and image services*")
    st.markdown(f"Groq Calls: {fmt_num(groq_calls)} / {fmt_num(GROQ_CALL_LIMIT)}", unsafe_allow_html=True)
    st.markdown(usage_bar(groq_calls, GROQ_CALL_LIMIT), unsafe_allow_html=True)
    st.caption("🤖 Groq API calls for generating sentences and translations")
    st.markdown(f"Groq Tokens: {fmt_num(groq_tokens)} / {fmt_num(GROQ_TOKEN_LIMIT)}", unsafe_allow_html=True)
    st.markdown(usage_bar(groq_tokens, GROQ_TOKEN_LIMIT), unsafe_allow_html=True)
    st.caption("📊 Text tokens processed by Groq AI (includes prompts and responses)")
    st.markdown(f"Pixabay Calls: {fmt_num(pixabay_calls)} / {fmt_num(PIXABAY_CALL_LIMIT)}", unsafe_allow_html=True)
    st.markdown(usage_bar(pixabay_calls, PIXABAY_CALL_LIMIT), unsafe_allow_html=True)
    st.caption("🖼️ Image searches on Pixabay for word illustrations")
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