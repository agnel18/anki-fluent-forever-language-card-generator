# pages/sentence_settings.py - Sentence settings page for the language learning app

import streamlit as st
import logging
from constants import CURATED_TOPICS

logger = logging.getLogger(__name__)

def _get_bcp47_code(language_name: str) -> str:
    """
    Convert language name to BCP-47 code for Google TTS.

    Args:
        language_name: Language name (e.g., "Chinese", "Spanish")

    Returns:
        BCP-47 language code (e.g., "zh-CN", "es-ES")
    """
    # Comprehensive mapping from language names to BCP-47 codes
    bcp47_map = {
        # Chinese variants - use cmn-CN for Neural2 voice names
        "Chinese": "cmn-CN",
        "Chinese (Simplified)": "cmn-CN",
        "Chinese (Traditional)": "cmn-TW",
        "Mandarin Chinese": "cmn-CN",
        "Cantonese": "yue-HK",

        # Major European languages
        "English": "en-US",
        "Spanish": "es-ES",
        "French": "fr-FR",
        "German": "de-DE",
        "Italian": "it-IT",
        "Portuguese": "pt-BR",
        "Russian": "ru-RU",
        "Dutch": "nl-NL",
        "Polish": "pl-PL",
        "Turkish": "tr-TR",
        "Swedish": "sv-SE",
        "Norwegian": "nb-NO",
        "Danish": "da-DK",
        "Finnish": "fi-FI",
        "Greek": "el-GR",
        "Czech": "cs-CZ",
        "Hungarian": "hu-HU",
        "Romanian": "ro-RO",
        "Bulgarian": "bg-BG",
        "Croatian": "hr-HR",
        "Slovak": "sk-SK",
        "Slovenian": "sl-SI",
        "Ukrainian": "uk-UA",
        "Serbian": "sr-RS",
        "Bosnian": "bs-BA",  # Not supported by Google TTS - keep for compatibility

        # Asian languages
        "Japanese": "ja-JP",
        "Korean": "ko-KR",
        "Hindi": "hi-IN",
        "Arabic": "ar-XA",
        "Hebrew": "he-IL",
        "Thai": "th-TH",
        "Vietnamese": "vi-VN",
        "Indonesian": "id-ID",
        "Malay": "ms-MY",
        "Tamil": "ta-IN",
        "Telugu": "te-IN",
        "Kannada": "kn-IN",
        "Bengali": "bn-IN",
        "Gujarati": "gu-IN",
        "Marathi": "mr-IN",
        "Urdu": "ur-IN",
        "Persian": "fa-IR",  # Not supported by Google TTS - keep for compatibility
        "Pashto": "ps-AF",  # Not supported by Google TTS - keep for compatibility

        # Other languages - using closest supported alternatives for unsupported languages
        "Afrikaans": "af-ZA",
        "Albanian": "sq-AL",  # Not supported by Google TTS - keep for compatibility
        "Amharic": "am-ET",
        "Armenian": "hy-AM",  # Not supported - keep for compatibility
        "Azerbaijani": "az-AZ",  # Not supported - keep for compatibility
        "Basque": "eu-ES",
        "Belarusian": "be-BY",  # Not supported - keep for compatibility
        "Estonian": "et-EE",
        "Georgian": "ka-GE",  # Not supported - keep for compatibility
        "Icelandic": "is-IS",
        "Irish": "ga-IE",  # Not supported - keep for compatibility
        "Kazakh": "kk-KZ",  # Not supported - keep for compatibility
        "Khmer": "km-KH",  # Not supported - keep for compatibility
        "Lao": "lo-LA",  # Not supported - keep for compatibility
        "Latvian": "lv-LV",
        "Lithuanian": "lt-LT",
        "Macedonian": "mk-MK",  # Not supported - keep for compatibility
        "Maltese": "mt-MT",  # Not supported - keep for compatibility
        "Mongolian": "mn-MN",  # Not supported - keep for compatibility
        "Nepali": "ne-NP",  # Not supported - keep for compatibility
        "Sinhala": "si-LK",  # Not supported - keep for compatibility
        "Swahili": "sw-KE",
        "Welsh": "cy-GB",  # Not supported - keep for compatibility
        "Zulu": "zu-ZA",  # Not supported - keep for compatibility
        "Burmese": "my-MM",  # Not supported - keep for compatibility
        "Javanese": "jv-ID",  # Not supported - keep for compatibility
        "Sundanese": "su-ID",  # Not supported - keep for compatibility
        "Uzbek": "uz-UZ",  # Not supported - keep for compatibility
    }

    return bcp47_map.get(language_name, "en-US")


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
            st.markdown("**Sentence Length (words)**")
            current_length = st.session_state.sentence_length_range
            st.session_state.sentence_length_range = st.slider(
                "Sentence Length Range",
                min_value=4,
                max_value=20,
                value=current_length,
                step=1,
                help="Min and max words per sentence.",
                label_visibility="collapsed"
            )
        with col_sent:
            st.markdown("**Sentences Per Word**")
            current_sentences = st.session_state.sentences_per_word
            st.session_state.sentences_per_word = st.slider(
                "Sentences Per Word",
                min_value=3,
                max_value=15,
                value=current_sentences,
                step=1,
                help="How many sentences to generate for each word.",
                label_visibility="collapsed"
            )
        
        # Difficulty setting - made more prominent
        st.markdown("---")
        st.markdown("## 🎯 **Difficulty Level**")
        st.markdown("*Choose the complexity level for your sentences*")

        difficulty_options = {
            "beginner": "Beginner - Simple vocabulary and basic sentence structures for absolute beginners",
            "intermediate": "Intermediate - Moderate vocabulary with varied sentence patterns for learners with basic knowledge",
            "advanced": "Advanced - Complex vocabulary and sophisticated sentence structures for proficient learners"
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

            try:
                from audio_generator import get_google_voices_for_language, GOOGLE_TTS_AVAILABLE, is_google_tts_configured, _get_bcp47_code
                
                # Check API configuration instead of SDK availability
                if not is_google_tts_configured():
                    st.warning("⚠️ Google Cloud Text-to-Speech API key not configured. Audio generation will be skipped.")
                    # Provide language-specific fallback voices even without API key
                    bcp47_code = _get_bcp47_code(lang)
                    lang_prefix = bcp47_code.split('-')[0] if bcp47_code else "en"
                    fallback_voices = {
                        "en": ["D (Female, Neural2)", "C (Male, Neural2)"],
                        "es": ["A (Female, Neural2)", "B (Male, Neural2)"],
                        "fr": ["A (Female, Neural2)", "B (Male, Neural2)"],
                        "de": ["A (Female, Neural2)", "B (Male, Neural2)"],
                        "it": ["A (Female, Neural2)", "B (Male, Neural2)"],
                        "pt": ["A (Female, Neural2)", "B (Male, Neural2)"],
                        "ru": ["A (Female, Standard)", "B (Male, Standard)"],
                        "ja": ["A (Female, Standard)", "B (Male, Standard)"],
                        "ko": ["A (Female, Standard)", "B (Male, Standard)"],
                        "zh": ["A (Female, Standard)", "B (Male, Standard)"],
                        "ar": ["A (Female, Standard)", "B (Male, Standard)"],
                        "hi": ["A (Female, Standard)", "B (Male, Standard)"]
                    }
                    voice_options = fallback_voices.get(lang_prefix, ["D (Female, Standard)"])
                    voice_display_map = {voice: f"{bcp47_code}-Standard-{voice.split(' ')[0]}" for voice in voice_options}
                elif not is_google_tts_configured():
                    st.warning("⚠️ Google Cloud Text-to-Speech authentication failed. Using fallback voices.")
                    # Provide language-specific fallback voices when auth fails
                    bcp47_code = _get_bcp47_code(lang)
                    lang_prefix = bcp47_code.split('-')[0] if bcp47_code else "en"
                    fallback_voices = {
                        "en": ["Emma (Female, Standard)", "Liam (Male, Standard)"],
                        "es": ["Maria (Female, Standard)", "Carlos (Male, Standard)"],
                        "fr": ["Sophie (Female, Standard)", "Pierre (Male, Standard)"],
                        "de": ["Anna (Female, Standard)", "Max (Male, Standard)"],
                        "it": ["Giulia (Female, Standard)", "Marco (Male, Standard)"],
                        "pt": ["Ana (Female, Standard)", "João (Male, Standard)"],
                        "ru": ["Olga (Female, Standard)", "Dmitri (Male, Standard)"],
                        "ja": ["Yumi (Female, Standard)", "Hiroshi (Male, Standard)"],
                        "ko": ["Ji-yeon (Female, Standard)", "Min-jun (Male, Standard)"],
                        "cmn": ["Li (Female, Standard)", "Wang (Male, Standard)"],
                        "ar": ["Fatima (Female, Standard)", "Ahmed (Male, Standard)"],
                        "hi": ["Priya (Female, Standard)", "Raj (Male, Standard)"],
                        "nl": ["Eva (Female, Standard)", "Jan (Male, Standard)"],
                        "sv": ["Ingrid (Female, Standard)", "Erik (Male, Standard)"],
                        "da": ["Freja (Female, Standard)", "Magnus (Male, Standard)"],
                        "no": ["Astrid (Female, Standard)", "Bjørn (Male, Standard)"],
                        "fi": ["Aino (Female, Standard)", "Eero (Male, Standard)"],
                        "pl": ["Zofia (Female, Standard)", "Adam (Male, Standard)"],
                        "cs": ["Marie (Female, Standard)", "Jan (Male, Standard)"],
                        "sk": ["Lucia (Female, Standard)", "Peter (Male, Standard)"],
                        "hu": ["Anna (Female, Standard)", "Béla (Male, Standard)"],
                        "tr": ["Ayşe (Female, Standard)", "Mehmet (Male, Standard)"],
                        "el": ["Maria (Female, Standard)", "Dimitris (Male, Standard)"],
                        "he": ["Rachel (Female, Standard)", "David (Male, Standard)"],
                        "th": ["Siriporn (Female, Standard)", "Somchai (Male, Standard)"],
                        "vi": ["Lan (Female, Standard)", "Minh (Male, Standard)"],
                        "id": ["Siti (Female, Standard)", "Ahmad (Male, Standard)"],
                        "ms": ["Aisyah (Female, Standard)", "Muhammad (Male, Standard)"],
                        "fil": ["Maria (Female, Standard)", "Juan (Male, Standard)"],
                        "uk": ["Oksana (Female, Standard)", "Oleksiy (Male, Standard)"],
                        "bg": ["Maria (Female, Standard)", "Ivan (Male, Standard)"],
                        "hr": ["Ana (Female, Standard)", "Marko (Male, Standard)"],
                        "sr": ["Ana (Female, Standard)", "Marko (Male, Standard)"],
                        "sl": ["Ana (Female, Standard)", "Janez (Male, Standard)"],
                        "et": ["Liisi (Female, Standard)", "Jaan (Male, Standard)"],
                        "lv": ["Līga (Female, Standard)", "Jānis (Male, Standard)"],
                        "lt": ["Ona (Female, Standard)", "Jonas (Male, Standard)"],
                        "ro": ["Maria (Female, Standard)", "Ion (Male, Standard)"],
                        "mt": ["Maria (Female, Standard)", "Joseph (Male, Standard)"],
                        "is": ["Guðrún (Female, Standard)", "Jón (Male, Standard)"],
                        "ga": ["Siobhán (Female, Standard)", "Seán (Male, Standard)"],
                        "cy": ["Megan (Female, Standard)", "Rhys (Male, Standard)"],
                        "sq": ["Ana (Female, Standard)", "Arben (Male, Standard)"],
                        "mk": ["Marija (Female, Standard)", "Aleksandar (Male, Standard)"],
                        "bs": ["Aida (Female, Standard)", "Adnan (Male, Standard)"],
                        "az": ["Aygün (Female, Standard)", "Rəsul (Male, Standard)"],
                        "ka": ["Nino (Female, Standard)", "Giorgi (Male, Standard)"],
                        "hy": ["Ani (Female, Standard)", "Armen (Male, Standard)"],
                        "mn": ["Sarangerel (Female, Standard)", "Bat-Erdene (Male, Standard)"],
                        "kk": ["Aigül (Female, Standard)", "Nurlan (Male, Standard)"],
                        "uz": ["Gulnora (Female, Standard)", "Rustam (Male, Standard)"],
                        "ky": ["Aida (Female, Standard)", "Asan (Male, Standard)"],
                        "tg": ["Zuhra (Female, Standard)", "Rustam (Male, Standard)"],
                        "tk": ["Aýgül (Female, Standard)", "Myrat (Male, Standard)"],
                        "tt": ["Aygül (Female, Standard)", "Ildar (Male, Standard)"],
                        "cv": ["Anna (Female, Standard)", "Ivan (Male, Standard)"],
                        "ba": ["Aygül (Female, Standard)", "Rustem (Male, Standard)"],
                        "xh": ["Nomhle (Female, Standard)", "Siyabonga (Male, Standard)"],
                        "zu": ["Nomusa (Female, Standard)", "Sipho (Male, Standard)"],
                        "af": ["Anna (Female, Standard)", "Jan (Male, Standard)"],
                        "st": ["Mpho (Female, Standard)", "Thabo (Male, Standard)"],
                        "tn": ["Mpho (Female, Standard)", "Thabo (Male, Standard)"],
                        "ts": ["Mpho (Female, Standard)", "Thabo (Male, Standard)"],
                        "ss": ["Nomvula (Female, Standard)", "Sibusiso (Male, Standard)"],
                        "ve": ["Mpho (Female, Standard)", "Thabo (Male, Standard)"],
                        "nr": ["Nomhle (Female, Standard)", "Siyabonga (Male, Standard)"],
                        "sw": ["Asha (Female, Standard)", "Jafari (Male, Standard)"],
                        "am": ["Meseret (Female, Standard)", "Dawit (Male, Standard)"],
                        "ti": ["Senait (Female, Standard)", "Habtom (Male, Standard)"],
                        "om": ["Amina (Female, Standard)", "Ahmed (Male, Standard)"],
                        "so": ["Amina (Female, Standard)", "Ahmed (Male, Standard)"],
                        "rw": ["Jeanne (Female, Standard)", "Jean (Male, Standard)"],
                        "lg": ["Nakato (Female, Standard)", "Kato (Male, Standard)"],
                        "ny": ["Grace (Female, Standard)", "John (Male, Standard)"],
                        "sn": ["Rumbidzai (Female, Standard)", "Tafadzwa (Male, Standard)"],
                        "st": ["Mpho (Female, Standard)", "Thabo (Male, Standard)"],
                        "tn": ["Mpho (Female, Standard)", "Thabo (Male, Standard)"],
                        "ts": ["Mpho (Female, Standard)", "Thabo (Male, Standard)"],
                        "ss": ["Nomvula (Female, Standard)", "Sibusiso (Male, Standard)"],
                        "ve": ["Mpho (Female, Standard)", "Thabo (Male, Standard)"],
                        "nr": ["Nomhle (Female, Standard)", "Siyabonga (Male, Standard)"]
                    }
                    # Map descriptive names to voice IDs
                    voice_name_to_id = {
                        # English
                        "Emma (Female, Standard)": "D", "Liam (Male, Standard)": "C",
                        # Spanish
                        "Maria (Female, Standard)": "A", "Carlos (Male, Standard)": "B",
                        # French
                        "Sophie (Female, Standard)": "A", "Pierre (Male, Standard)": "B",
                        # German
                        "Anna (Female, Standard)": "A", "Max (Male, Standard)": "B",
                        # Italian
                        "Giulia (Female, Standard)": "A", "Marco (Male, Standard)": "B",
                        # Portuguese
                        "Ana (Female, Standard)": "A", "João (Male, Standard)": "B",
                        # Russian
                        "Olga (Female, Standard)": "A", "Dmitri (Male, Standard)": "B",
                        # Japanese
                        "Yumi (Female, Standard)": "A", "Hiroshi (Male, Standard)": "B",
                        # Korean
                        "Ji-yeon (Female, Standard)": "A", "Min-jun (Male, Standard)": "B",
                        # Chinese
                        "Li (Female, Standard)": "C", "Wang (Male, Standard)": "B",
                        # Arabic
                        "Fatima (Female, Standard)": "A", "Ahmed (Male, Standard)": "B",
                        # Hindi
                        "Priya (Female, Standard)": "A", "Raj (Male, Standard)": "B",
                        # Dutch
                        "Eva (Female, Standard)": "A", "Jan (Male, Standard)": "B",
                        # Swedish
                        "Ingrid (Female, Standard)": "A", "Erik (Male, Standard)": "B",
                        # Danish
                        "Freja (Female, Standard)": "A", "Magnus (Male, Standard)": "B",
                        # Norwegian
                        "Astrid (Female, Standard)": "A", "Bjørn (Male, Standard)": "B",
                        # Finnish
                        "Aino (Female, Standard)": "A", "Eero (Male, Standard)": "B",
                        # Polish
                        "Zofia (Female, Standard)": "A", "Adam (Male, Standard)": "B",
                        # Czech
                        "Marie (Female, Standard)": "A", "Jan (Male, Standard)": "B",
                        # Slovak
                        "Lucia (Female, Standard)": "A", "Peter (Male, Standard)": "B",
                        # Hungarian
                        "Anna (Female, Standard)": "A", "Béla (Male, Standard)": "B",
                        # Turkish
                        "Ayşe (Female, Standard)": "A", "Mehmet (Male, Standard)": "B",
                        # Greek
                        "Maria (Female, Standard)": "A", "Dimitris (Male, Standard)": "B",
                        # Hebrew
                        "Rachel (Female, Standard)": "A", "David (Male, Standard)": "B",
                        # Thai
                        "Siriporn (Female, Standard)": "A", "Somchai (Male, Standard)": "B",
                        # Vietnamese
                        "Lan (Female, Standard)": "A", "Minh (Male, Standard)": "B",
                        # Indonesian
                        "Siti (Female, Standard)": "A", "Ahmad (Male, Standard)": "B",
                        # Malay
                        "Aisyah (Female, Standard)": "A", "Muhammad (Male, Standard)": "B",
                        # Filipino
                        "Maria (Female, Standard)": "A", "Juan (Male, Standard)": "B",
                        # Ukrainian
                        "Oksana (Female, Standard)": "A", "Oleksiy (Male, Standard)": "B",
                        # Bulgarian
                        "Maria (Female, Standard)": "A", "Ivan (Male, Standard)": "B",
                        # Croatian
                        "Ana (Female, Standard)": "A", "Marko (Male, Standard)": "B",
                        # Serbian
                        "Ana (Female, Standard)": "A", "Marko (Male, Standard)": "B",
                        # Slovenian
                        "Ana (Female, Standard)": "A", "Janez (Male, Standard)": "B",
                        # Estonian
                        "Liisi (Female, Standard)": "A", "Jaan (Male, Standard)": "B",
                        # Latvian
                        "Līga (Female, Standard)": "A", "Jānis (Male, Standard)": "B",
                        # Lithuanian
                        "Ona (Female, Standard)": "A", "Jonas (Male, Standard)": "B",
                        # Romanian
                        "Maria (Female, Standard)": "A", "Ion (Male, Standard)": "B",
                        # Maltese
                        "Maria (Female, Standard)": "A", "Joseph (Male, Standard)": "B",
                        # Icelandic
                        "Guðrún (Female, Standard)": "A", "Jón (Male, Standard)": "B",
                        # Irish
                        "Siobhán (Female, Standard)": "A", "Seán (Male, Standard)": "B",
                        # Welsh
                        "Megan (Female, Standard)": "A", "Rhys (Male, Standard)": "B",
                        # Albanian
                        "Ana (Female, Standard)": "A", "Arben (Male, Standard)": "B",
                        # Macedonian
                        "Marija (Female, Standard)": "A", "Aleksandar (Male, Standard)": "B",
                        # Bosnian
                        "Aida (Female, Standard)": "A", "Adnan (Male, Standard)": "B",
                        # Azerbaijani
                        "Aygün (Female, Standard)": "A", "Rəsul (Male, Standard)": "B",
                        # Georgian
                        "Nino (Female, Standard)": "A", "Giorgi (Male, Standard)": "B",
                        # Armenian
                        "Ani (Female, Standard)": "A", "Armen (Male, Standard)": "B",
                        # Mongolian
                        "Sarangerel (Female, Standard)": "A", "Bat-Erdene (Male, Standard)": "B",
                        # Kazakh
                        "Aigül (Female, Standard)": "A", "Nurlan (Male, Standard)": "B",
                        # Uzbek
                        "Gulnora (Female, Standard)": "A", "Rustam (Male, Standard)": "B",
                        # Kyrgyz
                        "Aida (Female, Standard)": "A", "Asan (Male, Standard)": "B",
                        # Tajik
                        "Zuhra (Female, Standard)": "A", "Rustam (Male, Standard)": "B",
                        # Turkmen
                        "Aýgül (Female, Standard)": "A", "Myrat (Male, Standard)": "B",
                        # Tatar
                        "Aygül (Female, Standard)": "A", "Ildar (Male, Standard)": "B",
                        # Chuvash
                        "Anna (Female, Standard)": "A", "Ivan (Male, Standard)": "B",
                        # Bashkir
                        "Aygül (Female, Standard)": "A", "Rustem (Male, Standard)": "B",
                        # Xhosa
                        "Nomhle (Female, Standard)": "A", "Siyabonga (Male, Standard)": "B",
                        # Zulu
                        "Nomusa (Female, Standard)": "A", "Sipho (Male, Standard)": "B",
                        # Afrikaans
                        "Anna (Female, Standard)": "A", "Jan (Male, Standard)": "B",
                        # Sesotho
                        "Mpho (Female, Standard)": "A", "Thabo (Male, Standard)": "B",
                        # Setswana
                        "Mpho (Female, Standard)": "A", "Thabo (Male, Standard)": "B",
                        # Xitsonga
                        "Mpho (Female, Standard)": "A", "Thabo (Male, Standard)": "B",
                        # Siswati
                        "Nomvula (Female, Standard)": "A", "Sibusiso (Male, Standard)": "B",
                        # Venda
                        "Mpho (Female, Standard)": "A", "Thabo (Male, Standard)": "B",
                        # Ndebele
                        "Nomhle (Female, Standard)": "A", "Siyabonga (Male, Standard)": "B",
                        # Swahili
                        "Asha (Female, Standard)": "A", "Jafari (Male, Standard)": "B",
                        # Amharic
                        "Meseret (Female, Standard)": "A", "Dawit (Male, Standard)": "B",
                        # Tigrinya
                        "Senait (Female, Standard)": "A", "Habtom (Male, Standard)": "B",
                        # Oromo
                        "Amina (Female, Standard)": "A", "Ahmed (Male, Standard)": "B",
                        # Somali
                        "Amina (Female, Standard)": "A", "Ahmed (Male, Standard)": "B",
                        # Kinyarwanda
                        "Jeanne (Female, Standard)": "A", "Jean (Male, Standard)": "B",
                        # Luganda
                        "Nakato (Female, Standard)": "A", "Kato (Male, Standard)": "B",
                        # Chichewa
                        "Grace (Female, Standard)": "A", "John (Male, Standard)": "B",
                        # Shona
                        "Rumbidzai (Female, Standard)": "A", "Tafadzwa (Male, Standard)": "B"
                    }
                    voice_options = list(voice_name_to_id.keys())
                    voice_display_map = {}
                    for display_name in voice_options:
                        voice_id = voice_name_to_id[display_name]
                        bcp47_code = _get_bcp47_code(lang)
                        if bcp47_code.startswith('zh'):
                            voice_name = f"cmn-CN-Standard-{voice_id}"
                        else:
                            voice_name = f"{bcp47_code}-Standard-{voice_id}"
                        voice_display_map[display_name] = voice_name
                else:
                    voice_options, is_fallback, voice_display_map = get_google_voices_for_language(lang)

                # Get current selection or default to first option
                current_display = getattr(st.session_state, 'selected_voice_display', voice_options[0])
                selected_voice_idx = voice_options.index(current_display) if current_display in voice_options else 0

                st.markdown("**Voice**")
                selected_voice_display = st.selectbox(
                    label="Voice Selection",
                    options=voice_options,
                    index=selected_voice_idx,
                    help="Choose the Google TTS voice for audio generation. Shows all available voices for your selected language.",
                    label_visibility="collapsed",
                    disabled=not (GOOGLE_TTS_AVAILABLE and is_google_tts_configured())
                )

                # Store both display name and actual voice name
                st.session_state.selected_voice_display = selected_voice_display
                st.session_state.selected_voice = voice_display_map.get(selected_voice_display, "en-US-Standard-D")

            except ImportError as e:
                st.error(f"Google TTS not configured. Please set up Google API key in API Setup. Error: {e}")
                st.session_state.selected_voice = "en-US-Standard-D"
                st.session_state.selected_voice_display = "D (Female, Standard)"
        with col_speed:
            st.markdown("**Audio Speed**")
            audio_speed = st.slider(
                label="Audio Speed",
                min_value=0.5,
                max_value=1.5,
                value=st.session_state.audio_speed,
                step=0.1,
                help="0.5 = very slow, 0.8 = learner-friendly (recommended), 1.0 = normal, 1.5 = fast",
                label_visibility="collapsed"
            )
            st.session_state.audio_speed = audio_speed

    # Voice Cost Comparison Table - Full Width Below Audio Settings
    with st.container():
        st.markdown("---")
        st.markdown("### 💰 Voice Cost Comparison")
        st.markdown("*Understand the cost and quality trade-offs for different voice types*")

        # Voice data for expandable cards
        voice_data = [
            {
                "name": "Standard",
                "cost": "$0.000016",
                "quality": "Good",
                "best_for": "Default choice, cost-effective",
                "recommendation": "✅ DEFAULT FOR ALL LANGUAGES - Balanced quality & cost",
                "is_default": True
            },
            {
                "name": "Chirp3",
                "cost": "$0.000004",
                "quality": "Good",
                "best_for": "Budget-conscious users",
                "recommendation": "Good alternative - lowest cost",
                "is_default": False
            },
            {
                "name": "Chirp3 HD",
                "cost": "$0.00002",
                "quality": "Higher",
                "best_for": "Premium audio, professional content",
                "recommendation": "Optional - 25% quality improvement at 5x cost",
                "is_default": False
            },
            {
                "name": "Wavenet",
                "cost": "$0.000032",
                "quality": "High",
                "best_for": "Natural speech, accessibility",
                "recommendation": "Premium option - 2x cost of Standard",
                "is_default": False
            },
            {
                "name": "Neural2",
                "cost": "$0.000024",
                "quality": "Very High",
                "best_for": "Most natural, immersive learning",
                "recommendation": "Luxury option - highest quality",
                "is_default": False
            }
        ]

        # Voice Cost Comparison Table - Full Width


        # Voice data for comparison table
        voice_comparison_data = {
            "Voice Type": ["Standard", "Chirp3", "Chirp3 HD", "Wavenet", "Neural2"],
            "Cost per Character": ["$0.000016", "$0.000004", "$0.00002", "$0.000032", "$0.000024"],
            "Quality Level": ["Good", "Good", "Higher", "High", "Very High"],
            "Best For": ["Default choice, cost-effective", "Budget-conscious users", "Premium audio, professional", "Natural speech, accessibility", "Most natural, immersive learning"],
            "Recommendation": ["✅ DEFAULT FOR ALL LANGUAGES", "Good alternative - lowest cost", "Optional - 25% quality improvement", "Premium option - 2x cost", "Luxury option - highest quality"]
        }

        # Always show comparison table
        st.markdown("**Voice Comparison Table:**")

        # Create the comparison table
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown("**Voice Type**")
            for voice in voice_comparison_data["Voice Type"]:
                if voice == "Standard":
                    st.markdown(f"🔹 **{voice}**")
                else:
                    st.markdown(f"🔸 {voice}")

        with col2:
            st.markdown("**Cost/Char**")
            for cost in voice_comparison_data["Cost per Character"]:
                st.markdown(f"`{cost}`")

        with col3:
            st.markdown("**Quality**")
            for quality in voice_comparison_data["Quality Level"]:
                st.markdown(f"⭐ {quality}")

        with col4:
            st.markdown("**Best For**")
            for use_case in voice_comparison_data["Best For"]:
                st.markdown(f"🎯 {use_case}")

        with col5:
            st.markdown("**Recommendation**")
            for rec in voice_comparison_data["Recommendation"]:
                st.markdown(rec)

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
            st.rerun()

    # Scroll to top after all content is rendered
    st.markdown("""
    <script>
        setTimeout(function() {
            window.scrollTo({top: 0, behavior: 'smooth'});
        }, 1000);
    </script>
    """, unsafe_allow_html=True)