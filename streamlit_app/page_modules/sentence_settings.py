# pages/sentence_settings.py - Sentence settings page for the language learning app

import streamlit as st
import logging
import pandas as pd
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
        "Malayalam": "ml-IN",
        "Malay": "ms-MY",
        "Tamil": "ta-IN",
        "Telugu": "te-IN",
        "Kannada": "kn-IN",
        "Bengali": "bn-IN",
        "Gujarati": "gu-IN",
        "Marathi": "mr-IN",
        "Urdu": "ur-IN",
        
        # Other languages - using closest supported alternatives for unsupported languages
        "Afrikaans": "af-ZA",
        "Amharic": "am-ET",
        "Azerbaijani": "az-AZ",  # Not supported - keep for compatibility
        "Basque": "eu-ES",
        "Catalan": "ca-ES",
        "Estonian": "et-EE",
        "Georgian": "ka-GE",  # Not supported - keep for compatibility
        "Galician": "gl-ES",
        "Icelandic": "is-IS",
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
        "Somali": "so-SO",
        "Zulu": "zu-ZA",  # Not supported - keep for compatibility
        "Burmese": "my-MM",  # Not supported - keep for compatibility
        "Javanese": "jv-ID",  # Not supported - keep for compatibility
        "Sundanese": "su-ID",  # Not supported - keep for compatibility
        "Uzbek": "uz-UZ",  # Not supported - keep for compatibility

# NEED TO BE REMOVED LATER - these languages are not supported by Google TTS but we want to keep them in the dropdown for compatibility with existing users who may have selected them before
        "Albanian": "sq-AL",
        "Welsh": "cy-GB",
        "Irish": "ga-IE",
        "Persian": "fa-IR",
        "Pashto": "ps-AF",
    }

    return bcp47_map.get(language_name, "en-US")


def initialize_sentence_settings_state():
    """
    Initialize all required session state variables for the sentence settings page.
    Respect per-language defaults that were loaded in Step 1.
    """
    # Only set defaults if they don't already exist from per-language settings
    if "sentence_length_range" not in st.session_state:
        st.session_state.sentence_length_range = (8, 12)
    if "sentences_per_word" not in st.session_state:
        st.session_state.sentences_per_word = 5
    if "difficulty" not in st.session_state:
        st.session_state.difficulty = "beginner"
    if "enable_topics" not in st.session_state:
        st.session_state.enable_topics = False
    if "selected_topics" not in st.session_state:
        st.session_state.selected_topics = []
    if "custom_topics" not in st.session_state:
        st.session_state.custom_topics = []
    if "audio_speed" not in st.session_state:
        st.session_state.audio_speed = 0.8

    # Voice - only set default if per-language settings haven't already loaded one
    if "selected_voice" not in st.session_state or "selected_voice_display" not in st.session_state:
        lang = st.session_state.get("selected_language", "English")
        # FULL default_voice_map for all 77 languages (from languages.yaml)
        # Key = language name exactly as shown in the app
        # Value = (voice_code, display_name)
        default_voice_map = {
            "English": ("en-US-AvaNeural", "AvaNeural (Female)"),
            "Spanish": ("es-ES-ElviraNeural", "ElviraNeural (Female)"),
            "French": ("fr-FR-DeniseNeural", "DeniseNeural (Female)"),
            "German": ("de-DE-Neural2-B", "Neural2-B (Male)"),
            "Italian": ("it-IT-IsabellaNeural", "IsabellaNeural (Female)"),
            "Portuguese": ("pt-BR-FranciscaNeural", "FranciscaNeural (Female)"),
            "Russian": ("ru-RU-DmitryNeural", "DmitryNeural (Male)"),
            "Japanese": ("ja-JP-NanamiNeural", "NanamiNeural (Female)"),
            "Korean": ("ko-KR-SunHiNeural", "SunHiNeural (Female)"),
            "Chinese (Simplified)": ("zh-CN-XiaoxiaoNeural", "XiaoxiaoNeural (Female)"),
            "Chinese (Traditional)": ("zh-TW-HsiaoChenNeural", "HsiaoChenNeural (Female)"),
            "Arabic": ("ar-SA-ZariyahNeural", "ZariyahNeural (Female)"),
            "Hindi": ("hi-IN-SwatiNeural", "SwatiNeural (Female)"),
            "Bengali": ("bn-IN-TithiNeural", "TithiNeural (Female)"),
            "Telugu": ("te-IN-ValluvasalaNeural", "ValluvasalaNeural (Female)"),
            "Tamil": ("ta-IN-VeenaNeural", "VeenaNeural (Female)"),
            "Marathi": ("mr-IN-AnanyaNeural", "AnanyaNeural (Female)"),
            "Gujarati": ("gu-IN-AarohiNeural", "AarohiNeural (Female)"),
            "Turkish": ("tr-TR-EmelNeural", "EmelNeural (Female)"),
            "Vietnamese": ("vi-VN-HoaiMyNeural", "HoaiMyNeural (Female)"),
            "Polish": ("pl-PL-ZofiaNeural", "ZofiaNeural (Female)"),
            "Dutch": ("nl-NL-MayaNeural", "MayaNeural (Female)"),
            "Swedish": ("sv-SE-SofieNeural", "SofieNeural (Female)"),
            "Greek": ("el-GR-AthinaNeural", "AthinaNeural (Female)"),
            "Czech": ("cs-CZ-VlastaNeural", "VlastaNeural (Female)"),
            "Hungarian": ("hu-HU-NoemiNeural", "NoemiNeural (Female)"),
            "Romanian": ("ro-RO-AleaNeural", "AleaNeural (Female)"),
            "Thai": ("th-TH-PremwadeeNeural", "PremwadeeNeural (Female)"),
            "Indonesian": ("id-ID-GadisNeural", "GadisNeural (Female)"),
            "Malayalam": ("ml-IN-Standard-A", "Standard-A (Female)"),
            "Ukrainian": ("uk-UA-OstapNeural", "OstapNeural (Male)"),
            "Afrikaans": ("af-ZA-WillemNeural", "WillemNeural (Male)"),
            "Albanian": ("sq-AL-IlseNeural", "IlseNeural (Female)"),
            "Amharic": ("am-ET-MekdesNeural", "MekdesNeural (Female)"),
            "Armenian": ("hy-AM-AnahitNeural", "AnahitNeural (Female)"),
            "Azerbaijani": ("az-AZ-BanuNeural", "BanuNeural (Female)"),
            "Bulgarian": ("bg-BG-KrystalNeural", "KrystalNeural (Female)"),
            "Catalan": ("ca-ES-JoanaNeural", "JoanaNeural (Female)"),
            "Welsh": ("cy-GB-NiaNeural", "NiaNeural (Female)"),
            "Danish": ("da-DK-ChristelNeural", "ChristelNeural (Female)"),
            "Estonian": ("et-EE-AnuNeural", "AnuNeural (Female)"),
            "Finnish": ("fi-FI-NooraNeural", "NooraNeural (Female)"),
            "Galician": ("gl-ES-RosamariaNeural", "RosamariaNeural (Female)"),
            "Georgian": ("ka-GE-EkaNeural", "EkaNeural (Female)"),
            "Hebrew": ("he-IL-HilaNeural", "HilaNeural (Female)"),
            "Icelandic": ("is-IS-GudrunNeural", "GudrunNeural (Female)"),
            "Irish": ("ga-IE-OrlaNeural", "OrlaNeural (Female)"),
            "Latvian": ("lv-LV-EvitaNeural", "EvitaNeural (Female)"),
            "Lithuanian": ("lt-LT-LiepaNeural", "LiepaNeural (Female)"),
            "Macedonian": ("mk-MK-MarijaNeural", "MarijaNeural (Female)"),
            "Norwegian": ("nb-NO-PernilleNeural", "PernilleNeural (Female)"),
            "Persian": ("fa-IR-DilaNeural", "DilaNeural (Female)"),
            "Slovak": ("sk-SK-VioletaNeural", "VioletaNeural (Female)"),
            "Slovenian": ("sl-SI-PetraNeural", "PetraNeural (Female)"),
            "Serbian": ("sr-RS-SophieNeural", "SophieNeural (Female)"),
            "Bosnian": ("bs-BA-GoranNeural", "GoranNeural (Male)"),
            "Basque": ("eu-ES-AinhoaNeural", "AinhoaNeural (Female)"),
            "Belarusian": ("be-BY-NatashaSergeyevichNeural", "NatashaSergeyevichNeural (Female)"),
            "Burmese": ("my-MM-NilarNeural", "NilarNeural (Female)"),
            "Croatian": ("hr-HR-GabrijelaNeural", "GabrijelaNeural (Female)"),
            "Kannada": ("kn-IN-GaganNeural", "GaganNeural (Male)"),
            "Kazakh": ("kk-KZ-AigulNeural", "AigulNeural (Female)"),
            "Khmer": ("km-KH-PisethNeural", "PisethNeural (Male)"),
            "Lao": ("lo-LA-ChanthavongNeural", "ChanthavongNeural (Male)"),
            "Malay": ("ms-MY-OsmanNeural", "OsmanNeural (Male)"),
            "Maltese": ("mt-MT-GraceNeural", "GraceNeural (Female)"),
            "Mongolian": ("mn-MN-BataaNeural", "BataaNeural (Male)"),
            "Nepali": ("ne-NP-HemkalaNeural", "HemkalaNeural (Female)"),
            "Pashto": ("ps-AF-GulNawazNeural", "GulNawazNeural (Male)"),
            "Sinhala": ("si-LK-SameeraNeural", "SameeraNeural (Male)"),
            "Somali": ("so-SO-MuuseNeural", "MuuseNeural (Male)"),
            "Sundanese": ("su-ID-JajangNeural", "JajangNeural (Male)"),
            "Swahili": ("sw-KE-RafikiNeural", "RafikiNeural (Male)"),
            "Urdu": ("ur-IN-GulNeural", "GulNeural (Female)"),
            "Uzbek": ("uz-UZ-MadinaNeural", "MadinaNeural (Female)"),
            "Zulu": ("zu-ZA-ThandoNeural", "ThandoNeural (Female)"),
            "Javanese": ("jv-ID-DimasNeural", "DimasNeural (Male)"),
        }
        default_voice, default_voice_display = default_voice_map.get(lang, ("en-US-Standard-D", "D (Female, Standard)"))
        if "selected_voice" not in st.session_state:
            st.session_state.selected_voice = default_voice
        if "selected_voice_display" not in st.session_state:
            st.session_state.selected_voice_display = default_voice_display

def render_sentence_settings_page():
    """Render the sentence settings page."""
    initialize_sentence_settings_state()
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
                        "hi": ["A (Female, Standard)", "B (Male, Standard)"],
                        "ml": ["A (Female, Standard)", "B (Male, Standard)"],
                        "ta": ["A (Female, Standard)", "B (Male, Standard)"],
                        "te": ["A (Female, Standard)", "B (Male, Standard)"],
                        "kn": ["A (Female, Standard)", "B (Male, Standard)"],
                        "bn": ["A (Female, Standard)", "B (Male, Standard)"],
                        "gu": ["A (Female, Standard)", "B (Male, Standard)"],
                        "mr": ["A (Female, Standard)", "B (Male, Standard)"],
                        "pa": ["A (Female, Standard)", "B (Male, Standard)"],
                        "th": ["A (Female, Standard)", "B (Male, Standard)"],
                        "vi": ["A (Female, Standard)", "B (Male, Standard)"],
                        "id": ["A (Female, Standard)", "B (Male, Standard)"],
                        "ms": ["A (Female, Standard)", "B (Male, Standard)"],
                        "nl": ["A (Female, Standard)", "B (Male, Standard)"],
                        "pl": ["A (Female, Standard)", "B (Male, Standard)"],
                        "sv": ["A (Female, Standard)", "B (Male, Standard)"],
                        "da": ["A (Female, Standard)", "B (Male, Standard)"],
                        "no": ["A (Female, Standard)", "B (Male, Standard)"],
                        "fi": ["A (Female, Standard)", "B (Male, Standard)"],
                        "tr": ["A (Female, Standard)", "B (Male, Standard)"],
                        "hu": ["A (Female, Standard)", "B (Male, Standard)"],
                        "cs": ["A (Female, Standard)", "B (Male, Standard)"],
                        "el": ["A (Female, Standard)", "B (Male, Standard)"],
                        "uk": ["A (Female, Standard)", "B (Male, Standard)"],
                        # Add any extra 2-letter codes here if your languages.yaml has more obscure languages
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
                        "zh": ["Li (Female, Standard)", "Wang (Male, Standard)"],
                        "ar": ["Fatima (Female, Standard)", "Ahmed (Male, Standard)"],
                        "hi": ["Priya (Female, Standard)", "Raj (Male, Standard)"],

                        "bn": ["A (Female, Standard)", "B (Male, Standard)"],
                        "te": ["A (Female, Standard)", "B (Male, Standard)"],
                        "ta": ["A (Female, Standard)", "B (Male, Standard)"],
                        "mr": ["A (Female, Standard)", "B (Male, Standard)"],
                        "gu": ["A (Female, Standard)", "B (Male, Standard)"],
                        "kn": ["A (Female, Standard)", "B (Male, Standard)"],
                        "ml": ["A (Female, Standard)", "B (Male, Standard)"],
                        "ur": ["A (Female, Standard)", "B (Male, Standard)"],

                        "tr": ["Ayşe (Female, Standard)", "Mehmet (Male, Standard)"],
                        "vi": ["Lan (Female, Standard)", "Minh (Male, Standard)"],
                        "pl": ["Zofia (Female, Standard)", "Adam (Male, Standard)"],
                        "nl": ["Eva (Female, Standard)", "Jan (Male, Standard)"],
                        "sv": ["Ingrid (Female, Standard)", "Erik (Male, Standard)"],
                        "el": ["Maria (Female, Standard)", "Dimitris (Male, Standard)"],
                        "cs": ["Marie (Female, Standard)", "Jan (Male, Standard)"],
                        "hu": ["Anna (Female, Standard)", "Béla (Male, Standard)"],
                        "ro": ["Maria (Female, Standard)", "Ion (Male, Standard)"],
                        "th": ["Siriporn (Female, Standard)", "Somchai (Male, Standard)"],
                        "id": ["Siti (Female, Standard)", "Ahmad (Male, Standard)"],
                        "uk": ["Oksana (Female, Standard)", "Oleksiy (Male, Standard)"],

                        "af": ["Anna (Female, Standard)", "Jan (Male, Standard)"],
                        "sq": ["A (Female, Standard)", "B (Male, Standard)"],
                        "am": ["Meseret (Female, Standard)", "Dawit (Male, Standard)"],
                        "az": ["A (Female, Standard)", "B (Male, Standard)"],
                        "bg": ["Maria (Female, Standard)", "Ivan (Male, Standard)"],
                        "ca": ["A (Female, Standard)", "B (Male, Standard)"],
                        "cy": ["A (Female, Standard)", "B (Male, Standard)"],
                        "da": ["Freja (Female, Standard)", "Magnus (Male, Standard)"],
                        "et": ["Liisi (Female, Standard)", "Jaan (Male, Standard)"],
                        "fi": ["Aino (Female, Standard)", "Eero (Male, Standard)"],
                        "gl": ["A (Female, Standard)", "B (Male, Standard)"],
                        "ka": ["A (Female, Standard)", "B (Male, Standard)"],
                        "he": ["Rachel (Female, Standard)", "David (Male, Standard)"],
                        "is": ["Guðrún (Female, Standard)", "Jón (Male, Standard)"],
                        "ga": ["A (Female, Standard)", "B (Male, Standard)"],
                        "lv": ["Līga (Female, Standard)", "Jānis (Male, Standard)"],
                        "lt": ["Ona (Female, Standard)", "Jonas (Male, Standard)"],
                        "mk": ["A (Female, Standard)", "B (Male, Standard)"],
                        "nb": ["Astrid (Female, Standard)", "Bjørn (Male, Standard)"],
                        "fa": ["A (Female, Standard)", "B (Male, Standard)"],
                        "sk": ["Lucia (Female, Standard)", "Peter (Male, Standard)"],
                        "sl": ["Ana (Female, Standard)", "Janez (Male, Standard)"],
                        "sr": ["Ana (Female, Standard)", "Marko (Male, Standard)"],
                        "bs": ["A (Female, Standard)", "B (Male, Standard)"],
                        "my": ["A (Female, Standard)", "B (Male, Standard)"],
                        "hr": ["Ana (Female, Standard)", "Marko (Male, Standard)"],
                        "kk": ["A (Female, Standard)", "B (Male, Standard)"],
                        "km": ["A (Female, Standard)", "B (Male, Standard)"],
                        "lo": ["A (Female, Standard)", "B (Male, Standard)"],
                        "ms": ["Aisyah (Female, Standard)", "Muhammad (Male, Standard)"],
                        "mt": ["A (Female, Standard)", "B (Male, Standard)"],
                        "mn": ["A (Female, Standard)", "B (Male, Standard)"],
                        "ne": ["A (Female, Standard)", "B (Male, Standard)"],
                        "ps": ["A (Female, Standard)", "B (Male, Standard)"],
                        "si": ["A (Female, Standard)", "B (Male, Standard)"],
                        "so": ["A (Female, Standard)", "B (Male, Standard)"],
                        "su": ["A (Female, Standard)", "B (Male, Standard)"],
                        "sw": ["Asha (Female, Standard)", "Jafari (Male, Standard)"],
                        "uz": ["A (Female, Standard)", "B (Male, Standard)"],
                        "zu": ["Nomusa (Female, Standard)", "Sipho (Male, Standard)"],
                        "jv": ["A (Female, Standard)", "B (Male, Standard)"]
                    }
                    # Map descriptive names to voice IDs
                    voice_name_to_id = {
                        # English
                        "English - Emma (Female, Standard)": "D", "English - Liam (Male, Standard)": "C",

                        # Spanish
                        "Spanish - Maria (Female, Standard)": "A", "Spanish - Carlos (Male, Standard)": "B",

                        # French
                        "French - Sophie (Female, Standard)": "A", "French - Pierre (Male, Standard)": "B",

                        # German
                        "German - Anna (Female, Standard)": "A", "German - Max (Male, Standard)": "B",

                        # Italian
                        "Italian - Giulia (Female, Standard)": "A", "Italian - Marco (Male, Standard)": "B",

                        # Portuguese
                        "Portuguese - Ana (Female, Standard)": "A", "Portuguese - João (Male, Standard)": "B",

                        # Russian
                        "Russian - Olga (Female, Standard)": "A", "Russian - Dmitri (Male, Standard)": "B",

                        # Japanese
                        "Japanese - Yumi (Female, Standard)": "A", "Japanese - Hiroshi (Male, Standard)": "B",

                        # Korean
                        "Korean - Ji-yeon (Female, Standard)": "A", "Korean - Min-jun (Male, Standard)": "B",

                        # Chinese
                        "Chinese - Li (Female, Standard)": "C", "Chinese - Wang (Male, Standard)": "B",

                        # Arabic
                        "Arabic - Fatima (Female, Standard)": "A", "Arabic - Ahmed (Male, Standard)": "B",

                        # Hindi
                        "Hindi - Priya (Female, Standard)": "A", "Hindi - Raj (Male, Standard)": "B",

                        # Bengali
                        "Bengali - A (Female, Standard)": "A", "Bengali - B (Male, Standard)": "B",

                        # Telugu
                        "Telugu - A (Female, Standard)": "A", "Telugu - B (Male, Standard)": "B",

                        # Tamil
                        "Tamil - A (Female, Standard)": "A", "Tamil - B (Male, Standard)": "B",

                        # Marathi
                        "Marathi - A (Female, Standard)": "A", "Marathi - B (Male, Standard)": "B",

                        # Gujarati
                        "Gujarati - A (Female, Standard)": "A", "Gujarati - B (Male, Standard)": "B",

                        # Kannada
                        "Kannada - A (Female, Standard)": "A", "Kannada - B (Male, Standard)": "B",

                        # Malayalam
                        "Malayalam - A (Female, Standard)": "A", "Malayalam - B (Male, Standard)": "B",

                        # Urdu
                        "Urdu - A (Female, Standard)": "A", "Urdu - B (Male, Standard)": "B",

                        # Turkish
                        "Turkish - Ayşe (Female, Standard)": "A", "Turkish - Mehmet (Male, Standard)": "B",

                        # Vietnamese
                        "Vietnamese - Lan (Female, Standard)": "A", "Vietnamese - Minh (Male, Standard)": "B",

                        # Polish
                        "Polish - Zofia (Female, Standard)": "A", "Polish - Adam (Male, Standard)": "B",

                        # Dutch
                        "Dutch - Eva (Female, Standard)": "A", "Dutch - Jan (Male, Standard)": "B",

                        # Swedish
                        "Swedish - Ingrid (Female, Standard)": "A", "Swedish - Erik (Male, Standard)": "B",

                        # Greek
                        "Greek - Maria (Female, Standard)": "A", "Greek - Dimitris (Male, Standard)": "B",

                        # Czech
                        "Czech - Marie (Female, Standard)": "A", "Czech - Jan (Male, Standard)": "B",

                        # Hungarian
                        "Hungarian - Anna (Female, Standard)": "A", "Hungarian - Béla (Male, Standard)": "B",

                        # Romanian
                        "Romanian - Maria (Female, Standard)": "A", "Romanian - Ion (Male, Standard)": "B",

                        # Thai
                        "Thai - Siriporn (Female, Standard)": "A", "Thai - Somchai (Male, Standard)": "B",

                        # Indonesian
                        "Indonesian - Siti (Female, Standard)": "A", "Indonesian - Ahmad (Male, Standard)": "B",

                        # Ukrainian
                        "Ukrainian - Oksana (Female, Standard)": "A", "Ukrainian - Oleksiy (Male, Standard)": "B",

                        # Afrikaans
                        "Afrikaans - Anna (Female, Standard)": "A", "Afrikaans - Jan (Male, Standard)": "B",

                        # Albanian
                        "Albanian - A (Female, Standard)": "A", "Albanian - B (Male, Standard)": "B",

                        # Amharic
                        "Amharic - Meseret (Female, Standard)": "A", "Amharic - Dawit (Male, Standard)": "B",

                        # Azerbaijani
                        "Azerbaijani - A (Female, Standard)": "A", "Azerbaijani - B (Male, Standard)": "B",

                        # Bulgarian
                        "Bulgarian - Maria (Female, Standard)": "A", "Bulgarian - Ivan (Male, Standard)": "B",

                        # Catalan
                        "Catalan - A (Female, Standard)": "A", "Catalan - B (Male, Standard)": "B",

                        # Welsh
                        "Welsh - A (Female, Standard)": "A", "Welsh - B (Male, Standard)": "B",

                        # Danish
                        "Danish - Freja (Female, Standard)": "A", "Danish - Magnus (Male, Standard)": "B",

                        # Estonian
                        "Estonian - Liisi (Female, Standard)": "A", "Estonian - Jaan (Male, Standard)": "B",

                        # Finnish
                        "Finnish - Aino (Female, Standard)": "A", "Finnish - Eero (Male, Standard)": "B",

                        # Galician
                        "Galician - A (Female, Standard)": "A", "Galician - B (Male, Standard)": "B",

                        # Georgian
                        "Georgian - A (Female, Standard)": "A", "Georgian - B (Male, Standard)": "B",

                        # Hebrew
                        "Hebrew - Rachel (Female, Standard)": "A", "Hebrew - David (Male, Standard)": "B",

                        # Icelandic
                        "Icelandic - Guðrún (Female, Standard)": "A", "Icelandic - Jón (Male, Standard)": "B",

                        # Irish
                        "Irish - A (Female, Standard)": "A", "Irish - B (Male, Standard)": "B",

                        # Latvian
                        "Latvian - Līga (Female, Standard)": "A", "Latvian - Jānis (Male, Standard)": "B",

                        # Lithuanian
                        "Lithuanian - Ona (Female, Standard)": "A", "Lithuanian - Jonas (Male, Standard)": "B",

                        # Macedonian
                        "Macedonian - A (Female, Standard)": "A", "Macedonian - B (Male, Standard)": "B",

                        # Norwegian
                        "Norwegian - Astrid (Female, Standard)": "A", "Norwegian - Bjørn (Male, Standard)": "B",

                        # Persian
                        "Persian - A (Female, Standard)": "A", "Persian - B (Male, Standard)": "B",

                        # Slovak
                        "Slovak - Lucia (Female, Standard)": "A", "Slovak - Peter (Male, Standard)": "B",

                        # Slovenian
                        "Slovenian - Ana (Female, Standard)": "A", "Slovenian - Janez (Male, Standard)": "B",

                        # Serbian
                        "Serbian - Ana (Female, Standard)": "A", "Serbian - Marko (Male, Standard)": "B",

                        # Bosnian
                        "Bosnian - A (Female, Standard)": "A", "Bosnian - B (Male, Standard)": "B",

                        # Burmese
                        "Burmese - A (Female, Standard)": "A", "Burmese - B (Male, Standard)": "B",

                        # Kazakh
                        "Kazakh - A (Female, Standard)": "A", "Kazakh - B (Male, Standard)": "B",

                        # Khmer
                        "Khmer - A (Female, Standard)": "A", "Khmer - B (Male, Standard)": "B",

                        # Lao
                        "Lao - A (Female, Standard)": "A", "Lao - B (Male, Standard)": "B",

                        # Malay
                        "Malay - Aisyah (Female, Standard)": "A", "Malay - Muhammad (Male, Standard)": "B",

                        # Maltese
                        "Maltese - A (Female, Standard)": "A", "Maltese - B (Male, Standard)": "B",

                        # Mongolian
                        "Mongolian - A (Female, Standard)": "A", "Mongolian - B (Male, Standard)": "B",

                        # Nepali
                        "Nepali - A (Female, Standard)": "A", "Nepali - B (Male, Standard)": "B",

                        # Pashto
                        "Pashto - A (Female, Standard)": "A", "Pashto - B (Male, Standard)": "B",

                        # Sinhala
                        "Sinhala - A (Female, Standard)": "A", "Sinhala - B (Male, Standard)": "B",

                        # Somali
                        "Somali - A (Female, Standard)": "A", "Somali - B (Male, Standard)": "B",

                        # Sundanese
                        "Sundanese - A (Female, Standard)": "A", "Sundanese - B (Male, Standard)": "B",

                        # Swahili
                        "Swahili - Asha (Female, Standard)": "A", "Swahili - Jafari (Male, Standard)": "B",

                        # Uzbek
                        "Uzbek - A (Female, Standard)": "A", "Uzbek - B (Male, Standard)": "B",

                        # Zulu
                        "Zulu - Nomusa (Female, Standard)": "A", "Zulu - Sipho (Male, Standard)": "B",

                        # Javanese
                        "Javanese - A (Female, Standard)": "A", "Javanese - B (Male, Standard)": "B"
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

                if is_fallback:
                    st.warning(
                        "Only default voices are available. Check your Google TTS API key and rotate it if needed."
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
            "Voice Type": ["🔹 Standard", "🔸 Chirp3", "🔸 Chirp3 HD", "🔸 Wavenet", "🔸 Neural2"],
            "Cost/Char": ["$0.000016", "$0.000004", "$0.00002", "$0.000032", "$0.000024"],
            "Quality": ["⭐ Good", "⭐ Good", "⭐ Higher", "⭐ High", "⭐ Very High"],
            "Best For": ["🎯 Default choice, cost-effective", "🎯 Budget-conscious users", "🎯 Premium audio, professional", "🎯 Natural speech, accessibility", "🎯 Most natural, immersive learning"],
            "Recommendation": ["✅ DEFAULT FOR ALL LANGUAGES", "Good alternative - lowest cost", "Optional - 25% quality improvement", "Premium option - 2x cost", "Luxury option - highest quality"]
        }

        # Always show comparison table
        st.markdown("**Voice Comparison Table:**")

        # Create DataFrame for scrollable table
        df = pd.DataFrame(voice_comparison_data)

        # Display as scrollable table
        st.dataframe(
            df,
            width='stretch',
            hide_index=True,
            column_config={
                "Voice Type": st.column_config.TextColumn("Voice Type", width="medium"),
                "Cost/Char": st.column_config.TextColumn("Cost/Char", width="small"),
                "Quality": st.column_config.TextColumn("Quality", width="small"),
                "Best For": st.column_config.TextColumn("Best For", width="large"),
                "Recommendation": st.column_config.TextColumn("Recommendation", width="large")
            }
        )

    with st.container():
        st.markdown("---")
        st.markdown(f"**Audio Preview:** {st.session_state.audio_speed}x speed, **Voice:** {st.session_state.selected_voice_display}")

    st.markdown("---")

    st.markdown("---")

    # === GLOBAL DEFAULTS MANAGEMENT (single shared JSON file) ===
    # Safe initialization to prevent the previous error
    if "per_language_settings" not in st.session_state:
        st.session_state.per_language_settings = {}

    current_lang = st.session_state.get("selected_language", "this language")

    st.markdown("### 💾 Persist These Settings for Future Sessions")
    st.caption("All languages share one global JSON file. Changes here update the master file.")

    col_save, col_download = st.columns([1.6, 1])

    with col_save:
        if st.button(
            f"💾 Save These Settings as Defaults for **{current_lang}**",
            type="secondary",
            use_container_width=True,
            key="save_as_defaults_btn"
        ):
            st.session_state.per_language_settings[current_lang] = {
                "sentence_length_range": st.session_state.sentence_length_range,
                "sentences_per_word": st.session_state.sentences_per_word,
                "difficulty": st.session_state.difficulty,
                "selected_voice": st.session_state.get("selected_voice", ""),
                "selected_voice_display": st.session_state.get("selected_voice_display", ""),
                "audio_speed": st.session_state.audio_speed
            }
            st.success(f"✅ Saved for **{current_lang}** and updated the global defaults file")
            st.rerun()

    with col_download:
        if st.button("📤 Download Global Defaults JSON", use_container_width=True):
            import json
            data = json.dumps(st.session_state.per_language_settings, indent=2, ensure_ascii=False)
            st.download_button(
                label="⬇️ Download language_defaults.json",
                data=data,
                file_name="language_defaults.json",
                mime="application/json",
                key="global_download_from_step3"
            )

    st.caption("💡 Full backup / restore + summary of all languages is in **Settings → Per-Language Default Output Settings**")

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