# pages/sentence_settings.py - Sentence settings page for the language learning app

import streamlit as st
try:
    from edge_tts_voices import EDGE_TTS_VOICES
except ImportError:
    EDGE_TTS_VOICES = {}  # Fallback empty dict
from constants import CURATED_TOPICS


def render_sentence_settings_page():
    """Render the sentence settings page."""

    with st.container():
        st.markdown("# ✍️ Step 3: Adjust Output Settings")
        st.markdown("Customize how your Anki cards will be generated. These settings control sentence complexity and audio pronunciation.")

        # Progress indicator
        st.markdown("**Progress:** Step 3 of 5")
        st.progress(0.6)

        st.markdown("---")

    # --- Sentence Settings ---
    with st.container():
        st.markdown("## ✍️ Sentence Settings")
        col_len, col_sent = st.columns(2)
        with col_len:
            current_length = st.session_state.sentence_length_range
            st.session_state.sentence_length_range = st.slider(
                "Sentence length (words)",
                min_value=4,
                max_value=30,
                value=current_length,
                step=1,
                help="Min and max words per sentence."
            )
        with col_sent:
            current_sentences = st.session_state.sentences_per_word
            st.session_state.sentences_per_word = st.slider(
                "Sentences per word",
                min_value=3,
                max_value=15,
                value=current_sentences,
                step=1,
                help="How many sentences to generate for each word."
            )
        
        # Difficulty setting - made more prominent
        st.markdown("---")
        st.markdown("### 🎯 **Difficulty Level**")
        st.markdown("*Choose the complexity level for your sentences*")

        difficulty_options = {
            "beginner": "beginner - Simple vocabulary and basic sentence structures for absolute beginners",
            "intermediate": "intermediate - Moderate vocabulary with varied sentence patterns for learners with basic knowledge",
            "advanced": "advanced - Complex vocabulary and sophisticated sentence structures for proficient learners"
        }

        selected_difficulty = st.selectbox(
            "Select Difficulty:",
            list(difficulty_options.keys()),
            index=list(difficulty_options.keys()).index(st.session_state.get("difficulty", "intermediate")),
            format_func=lambda x: difficulty_options[x],
            help="Choose the complexity level for generated sentences"
        )
        st.session_state.difficulty = selected_difficulty
        
        # Show difficulty explanations
        difficulty = st.session_state.difficulty
        if difficulty == "beginner":
            st.info("**Beginner**: Simple vocabulary and grammar, mostly present tense. Perfect for absolute beginners learning basic sentence structures.")
        elif difficulty == "intermediate":
            st.info("**Intermediate**: Mixed tenses, richer vocabulary, and varied grammar. Suitable for learners with basic knowledge who want more challenge.")
        elif difficulty == "advanced":
            st.info("**Advanced**: Complex structures, nuanced vocabulary, and sophisticated grammar. Ideal for advanced learners seeking native-like proficiency.")

    st.markdown("---")

    # --- Topic Settings ---
    with st.container():
        st.markdown("## 🎯 Topic Settings")
        
        # Enable/disable toggle
        enable_topics = st.toggle(
            "Enable Topic-Based Sentence Generation",
            value=st.session_state.get("enable_topics", False),
            help="When enabled, generated sentences will be themed around your selected topics for more relevant learning."
        )
        st.session_state.enable_topics = enable_topics
        
        if enable_topics:
            st.markdown("**Select topics to focus sentence generation around:**")
            
            # Initialize topic lists if not exists
            if "selected_topics" not in st.session_state:
                st.session_state.selected_topics = []
            if "custom_topics" not in st.session_state:
                st.session_state.custom_topics = []
            
            # Topic limit
            TOPIC_LIMIT = 5
            current_topic_count = len(st.session_state.selected_topics)
            limit_reached = current_topic_count >= TOPIC_LIMIT
            
            if limit_reached:
                st.warning(f"⚠️ **Topic limit reached:** You've selected the maximum of {TOPIC_LIMIT} topics. Unselect some topics to choose different ones.")
            else:
                st.info(f"📊 **Topic selection:** {current_topic_count}/{TOPIC_LIMIT} topics selected")
            
            # Curated topics selection
            st.markdown("### 📚 Curated Topics")
            col1, col2 = st.columns(2)
            
            # Split curated topics into two columns for better layout
            mid_point = len(CURATED_TOPICS) // 2
            left_topics = CURATED_TOPICS[:mid_point]
            right_topics = CURATED_TOPICS[mid_point:]
            
            with col1:
                for topic in left_topics:
                    is_selected = topic in st.session_state.selected_topics
                    # Disable checkbox if limit reached and topic not already selected
                    disabled = limit_reached and not is_selected
                    
                    if st.checkbox(
                        topic, 
                        value=is_selected,
                        key=f"curated_{topic}",
                        disabled=disabled
                    ):
                        if topic not in st.session_state.selected_topics and not limit_reached:
                            st.session_state.selected_topics.append(topic)
                    else:
                        if topic in st.session_state.selected_topics:
                            st.session_state.selected_topics.remove(topic)
            
            with col2:
                for topic in right_topics:
                    is_selected = topic in st.session_state.selected_topics
                    # Disable checkbox if limit reached and topic not already selected
                    disabled = limit_reached and not is_selected
                    
                    if st.checkbox(
                        topic, 
                        value=is_selected,
                        key=f"curated_{topic}",
                        disabled=disabled
                    ):
                        if topic not in st.session_state.selected_topics and not limit_reached:
                            st.session_state.selected_topics.append(topic)
                    else:
                        if topic in st.session_state.selected_topics:
                            st.session_state.selected_topics.remove(topic)
            
            # Custom topics section
            st.markdown("### ➕ Custom Topics")
            col_add, col_list = st.columns([1, 2])
            
            with col_add:
                new_topic = st.text_input(
                    "Add custom topic:",
                    placeholder="e.g., Gardening, Photography",
                    key="new_topic_input",
                    max_chars=50,
                    disabled=limit_reached
                )
                
                if st.button("➕ Add Topic", key="add_custom_topic", disabled=limit_reached):
                    if new_topic.strip():
                        # Validate input
                        clean_topic = new_topic.strip()
                        if len(clean_topic) < 2:
                            st.error("Topic must be at least 2 characters long.")
                        elif clean_topic in st.session_state.selected_topics:
                            st.warning("This topic is already selected.")
                        elif clean_topic in CURATED_TOPICS:
                            st.warning("This topic already exists in the curated list.")
                        else:
                            st.session_state.custom_topics.append(clean_topic)
                            st.session_state.selected_topics.append(clean_topic)
                            st.success(f"Added topic: {clean_topic}")
                            st.rerun()
            
            with col_list:
                if st.session_state.custom_topics:
                    st.markdown("**Your Custom Topics:**")
                    for i, topic in enumerate(st.session_state.custom_topics):
                        col_topic, col_remove = st.columns([3, 1])
                        with col_topic:
                            is_selected = st.checkbox(
                                topic, 
                                value=topic in st.session_state.selected_topics,
                                key=f"custom_{topic}_{i}"
                            )
                            if is_selected and topic not in st.session_state.selected_topics:
                                st.session_state.selected_topics.append(topic)
                            elif not is_selected and topic in st.session_state.selected_topics:
                                st.session_state.selected_topics.remove(topic)
                        
                        with col_remove:
                            if st.button("🗑️", key=f"remove_custom_{i}", help=f"Remove {topic}"):
                                if topic in st.session_state.selected_topics:
                                    st.session_state.selected_topics.remove(topic)
                                st.session_state.custom_topics.remove(topic)
                                st.rerun()
            
            # Selected topics summary
            if st.session_state.selected_topics:
                st.markdown("### ✅ Selected Topics")
                topics_text = ", ".join(st.session_state.selected_topics)
                st.info(f"**{len(st.session_state.selected_topics)} topics selected:** {topics_text}")
                
                # Topic priority/reordering (simple version - could be enhanced with drag-drop later)
                if len(st.session_state.selected_topics) > 1:
                    st.markdown("**Topic Priority (drag to reorder if needed):**")
                    # For now, just show them in order - drag-drop would require more complex implementation
                    for i, topic in enumerate(st.session_state.selected_topics):
                        st.caption(f"{i+1}. {topic}")
            else:
                st.info("No topics selected. Sentences will be generated without topic constraints.")
        else:
            st.info("Topic selection is disabled. Sentences will be generated with general vocabulary.")

    st.markdown("---")

    # --- Audio Settings ---
    with st.container():
        st.markdown("## 🎵 Audio Settings")
        col_voice, col_speed = st.columns(2)
        with col_voice:
            lang = st.session_state.selected_language
            if lang in EDGE_TTS_VOICES:
                voice_options = [f"{v[0]} ({v[1]}, {v[2]})" for v in EDGE_TTS_VOICES[lang]]
                selected_voice_idx = voice_options.index(st.session_state.selected_voice_display) if st.session_state.selected_voice_display in voice_options else 0
                selected_voice_display = st.selectbox(
                    "Voice",
                    options=voice_options,
                    index=selected_voice_idx,
                    help="Choose the voice for audio generation."
                )
                st.session_state.selected_voice_display = selected_voice_display
                st.session_state.selected_voice = EDGE_TTS_VOICES[lang][voice_options.index(selected_voice_display)][0]
            else:
                st.session_state.selected_voice_display = "en-US-AvaNeural (Female, Ava)"
                st.session_state.selected_voice = "en-US-AvaNeural"
        with col_speed:
            audio_speed = st.slider(
                "Audio Speed",
                min_value=0.5,
                max_value=1.5,
                value=st.session_state.audio_speed,
                step=0.1,
                help="0.5 = very slow, 0.8 = learner-friendly (recommended), 1.0 = normal, 1.5 = fast"
            )
            st.session_state.audio_speed = audio_speed

    with st.container():
        st.markdown("---")
        st.markdown(f"**Audio Preview:** {st.session_state.audio_speed}x speed, **Voice:** {st.session_state.selected_voice_display}")

    st.markdown("---")

    # Navigation buttons at bottom
    col_back, col_next = st.columns([1, 1])
    with col_back:
        if st.button("⬅️ Back to Word Selection", key="back_from_sentence_settings", use_container_width=True):
            st.session_state.page = "word_select"
            st.rerun()
    with col_next:
        if st.button("Next: Generate Deck ➡️", key="next_from_sentence_settings", use_container_width=True, type="primary"):
            st.session_state.page = "generate"
            st.session_state.scroll_to_top = True
            st.rerun()