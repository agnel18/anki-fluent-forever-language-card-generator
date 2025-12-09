"""
Fluent Forever Anki Card Generator - Streamlit GUI (v3)
Production-ready with full generation workflow
"""

import streamlit as st
import yaml
import os
from pathlib import Path
import pandas as pd
from core_functions import (
    generate_complete_deck,
    create_zip_export,
    create_apkg_export,
)
from frequency_utils import (
    get_available_frequency_lists,
    load_frequency_list,
    BATCH_PRESETS,
    validate_word_list,
    get_csv_template,
    parse_uploaded_word_file,
    get_words_with_ranks,
)
from db_manager import (
    get_words_paginated,
    search_words,
    mark_words_completed,
    get_completed_words,
    get_word_stats,
    log_generation,
)
from firebase_manager import (
    get_session_id,
    sync_progress_to_firebase,
    load_progress_from_firebase,
    save_settings_to_firebase,
    log_generation_to_firebase,
)

# ============================================================================
# PAGE CONFIG & STYLING
# ============================================================================

st.set_page_config(
    page_title="Fluent Forever Anki Generator",
    page_icon="🌍",
    layout="wide",
)

st.markdown("""
<style>
    body { font-size: 16px !important; }
    .stButton > button {
        background-color: #238636 !important;
        color: #ffffff !important;
        font-size: 1.1rem !important;
        padding: 0.75rem 1.5rem !important;
        font-weight: bold !important;
    }
    .stProgress > div > div > div > div {
        background-color: #58a6ff !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE
# ============================================================================

if "page" not in st.session_state:
    st.session_state.page = "api_setup"
if "groq_api_key" not in st.session_state:
    st.session_state.groq_api_key = ""
if "pixabay_api_key" not in st.session_state:
    st.session_state.pixabay_api_key = ""
if "current_batch_size" not in st.session_state:
    st.session_state.current_batch_size = 5

if "loaded_words" not in st.session_state:
    st.session_state.loaded_words = {}

if "current_lang_words" not in st.session_state:
    st.session_state.current_lang_words = []

if "completed_words" not in st.session_state:
    st.session_state.completed_words = {}  # {language: [list of completed words]}

if "selection_mode" not in st.session_state:
    st.session_state.selection_mode = "range"  # range, manual, search

# Global settings defaults
if "difficulty" not in st.session_state:
    st.session_state.difficulty = "intermediate"  # beginner, intermediate, advanced
if "sentence_length_range" not in st.session_state:
    st.session_state.sentence_length_range = (6, 16)
if "sentences_per_word" not in st.session_state:
    st.session_state.sentences_per_word = 10
if "track_progress" not in st.session_state:
    st.session_state.track_progress = True
if "audio_speed" not in st.session_state:
    st.session_state.audio_speed = 0.8
if "audio_pitch" not in st.session_state:
    st.session_state.audio_pitch = 0  # in Hz, range: -20 to +20
if "selected_voice" not in st.session_state:
    st.session_state.selected_voice = None
if "selected_voice_display" not in st.session_state:
    st.session_state.selected_voice_display = None
if "first_run_complete" not in st.session_state:
    st.session_state.first_run_complete = False

# Database and Firebase
if "session_id" not in st.session_state:
    st.session_state.session_id = get_session_id()
if "current_page" not in st.session_state:
    st.session_state.current_page = {}

config_path = Path(__file__).parent / "languages.yaml"
with open(config_path, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

all_languages = config["all_languages"]

def get_secret(key: str, default: str = "") -> str:
    try:
        return st.secrets.get(key, os.getenv(key, default))
    except:
        return os.getenv(key, default)

# ============================================================================
# PAGE 1: API SETUP
# ============================================================================

if st.session_state.page == "api_setup":
    st.markdown("# 🌍 Language Learning Anki Deck Generator")
    st.markdown("Create custom Anki decks in minutes | Free, no data stored")
    st.divider()
    
    st.markdown("## 🔐 API Keys Setup")
    st.markdown("""
    **How it works:**
    1. You enter your API keys in this form
    2. They stay in your browser's temporary memory (session only)
    3. We use them ONLY to make API calls on YOUR behalf
    4. Your keys are NEVER stored anywhere
    5. When you close this tab, keys are automatically deleted
    
    **Important privacy notes:**
    - ✅ Your API keys are YOUR responsibility
    - ✅ Your data stays with you (nothing uploaded)
    - ✅ You control API usage and costs
    - ✅ You can regenerate keys anytime
    """)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🤖 Groq API Key")
        st.markdown("""
        **What it's for:** Generate sentences in your language
        
        **Get free key:**
        1. https://console.groq.com/keys
        2. Create account (free)
        3. Generate new API key
        4. Copy & paste below
        """)
        groq_key = st.text_input("Groq API Key", type="password", placeholder="gsk_...")
    
    with col2:
        st.markdown("### 🖼️ Pixabay API Key")
        st.markdown("""
        **What it's for:** Download images for each word
        
        **Get free key:**
        1. https://pixabay.com/api/docs/
        2. Create account (free)
        3. Find API key in dashboard
        4. Copy & paste below
        """)
        pixabay_key = st.text_input("Pixabay API Key", type="password", placeholder="53606933-...")
    
    st.divider()
    
    # Check for environment variables
    groq_env = get_secret("GROQ_API_KEY", "")
    pixabay_env = get_secret("PIXABAY_API_KEY", "")
    
    if groq_env and pixabay_env and not groq_key:
        st.info("ℹ️ **Development Mode Detected** - Your API keys were auto-loaded from .env file")
        groq_key = groq_env
        pixabay_key = pixabay_env
    
    st.divider()
    
    if st.button("🚀 Let's Go!", use_container_width=True):
        if not groq_key:
            st.error("❌ Please enter your Groq API key")
        elif not pixabay_key:
            st.error("❌ Please enter your Pixabay API key")
        else:
            st.session_state.groq_api_key = groq_key
            st.session_state.pixabay_api_key = pixabay_key
            st.session_state.page = "main"
            st.session_state.scroll_to_top = True
            st.rerun()

# ============================================================================
# PAGE 2: MAIN APP
# ============================================================================

elif st.session_state.page == "main":
    
    # Ensure we start at the top after navigating from the API screen
    if st.session_state.get('scroll_to_top', False):
        st.markdown('<script>window.scrollTo(0, 0);</script>', unsafe_allow_html=True)
        st.session_state.scroll_to_top = False
    
    col1, col2, col3 = st.columns([4, 1, 1])
    with col1:
        st.markdown("# 🌍 Language Learning Anki Deck Generator")
    with col2:
        if st.button("🔐 Change Keys"):
            st.session_state.page = "api_setup"
            st.rerun()
    with col3:
        settings_pop = st.popover("⚙️ Settings", help="Adjust difficulty, sentence length, audio, and tracking", use_container_width=True)
        with settings_pop:
            st.markdown("### Global Settings")
            st.session_state.difficulty = st.radio(
                "Difficulty",
                ["beginner", "intermediate", "advanced"],
                index=["beginner", "intermediate", "advanced"].index(st.session_state.difficulty),
                help="Beginner uses shorter sentences and simpler vocab; Advanced leans into longer, more complex structures.",
            )
            st.session_state.sentence_length_range = st.slider(
                "Sentence length (words)",
                min_value=4,
                max_value=30,
                value=st.session_state.sentence_length_range,
                step=1,
                help="Min and max words per sentence",
            )
            st.session_state.sentences_per_word = st.slider(
                "Sentences per word",
                min_value=3,
                max_value=15,
                value=st.session_state.sentences_per_word,
                step=1,
                help="How many sentences to generate per word",
            )
            st.session_state.track_progress = st.checkbox(
                "Track progress (mark generated words as completed)",
                value=st.session_state.track_progress,
            )
            st.session_state.audio_speed = st.slider(
                "Audio speed",
                min_value=0.5,
                max_value=1.5,
                value=st.session_state.audio_speed,
                step=0.1,
                help="0.5 = slow, 1.0 = normal, 1.5 = fast",
            )
            st.caption("Voice and pitch are chosen in Step 3 (Audio Settings).")
    
    st.divider()
    
    # Step 1: Language
    st.markdown("## 📋 Step 1: Select Language")
    lang_names = [lang["name"] for lang in all_languages]
    col_lang, col_available = st.columns([3, 1])
    with col_lang:
        selected_lang = st.selectbox("Which language do you want to learn?", lang_names)
    
    available_lists = get_available_frequency_lists()
    max_words = available_lists.get(selected_lang, 5000)
    with col_available:
        st.metric("Available", f"{max_words:,} words")
    
    st.divider()
    
    # Step 2: Select words (batch + list combined)
    st.markdown("## 📚 Step 2: Select Your Words")
    st.markdown("**We pull from frequency lists so you start with the most useful words first.**")
    
    # Info about frequency lists - moved right after description
    with st.expander("📖 What is a Frequency List?", expanded=False):
        st.markdown("""
        A **Frequency List** contains the most commonly used words in a language, ranked by how often they appear in real conversations, books, movies, and other sources.
        
        **Why use it?**
        - Focus on words you'll actually encounter
        - Learn vocabulary efficiently (top 1,000 words = ~80% of everyday language)
        - Build a strong foundation for real communication
        
        **Example:** In Spanish, "the" (el/la) is word #1, "and" (y) is word #2, "to" (a) is word #3, etc.
        """)
    st.info("For your first run, try 1 word. After that, keep batches around 5–10 to respect rate limits.")
    
    # Initialize page tracking
    if selected_lang not in st.session_state.current_page:
        st.session_state.current_page[selected_lang] = 1
    
    # Get completed words and stats
    completed = get_completed_words(selected_lang)
    stats = get_word_stats(selected_lang)
    
    # Display stats
    col1, col2, col3 = st.columns(3)
    col1.metric("Total words", stats.get("total", 0))
    col2.metric("Completed", stats.get("completed", 0))
    col3.metric("Remaining", stats.get("remaining", 0))

    st.divider()

    # ========================================================================
    # FREQUENCY LIST SELECTION & CUSTOM IMPORT
    # ========================================================================
    
    st.markdown("### Pick from **Top Words Used in** " + selected_lang)
    
    # Create tabs: Frequency List vs Custom Import
    tab_frequency, tab_custom = st.tabs(["📊 Frequency List", "📥 Import Your Own Words"])
    
    with tab_frequency:
        # Pagination settings
        page_size = 25
        current_page = st.session_state.current_page[selected_lang]
        
        # Get words with ranks
        words_df, total_words = get_words_with_ranks(selected_lang, page=current_page, page_size=page_size)
        total_pages = (total_words + page_size - 1) // page_size
        
        # Display words in a clean table with checkboxes
        st.markdown("#### Select words to include in your deck:")
        
        # Create columns for display
        col_rank, col_word, col_select, col_status = st.columns([0.8, 1.5, 1.2, 0.8])
        
        with col_rank:
            st.write("**Rank**")
        with col_word:
            st.write("**Word**")
        with col_select:
            st.write("**Select**")
        with col_status:
            st.write("**Status**")
        
        st.divider()
        
        selected_words = []
        
        # Display each word with checkbox
        for idx, row in words_df.iterrows():
            col_rank, col_word, col_select, col_status = st.columns([0.8, 1.5, 1.2, 0.8])
            
            with col_rank:
                st.write(f"#{row['Rank']}")
            
            with col_word:
                st.write(row['Word'])
            
            with col_select:
                is_selected = st.checkbox(
                    "Select",
                    key=f"word_select_{selected_lang}_{row['Word']}_{idx}",
                    label_visibility="collapsed"
                )
                if is_selected:
                    selected_words.append(row['Word'])
            
            with col_status:
                if row['Completed']:
                    st.write("✅")
        
        st.divider()
        
        # Pagination controls (below word table)
        start_rank = (current_page - 1) * page_size + 1
        end_rank = min(current_page * page_size, total_words)
        st.markdown(f"**Top {start_rank}–{end_rank}** | Page {current_page} of {total_pages}")
        
        col_prev, col_next, col_jump = st.columns([1, 1, 2])
        
        with col_prev:
            if st.button("⬅️ Previous", key="prev_page"):
                if current_page > 1:
                    st.session_state.current_page[selected_lang] -= 1
                    st.rerun()
        
        with col_next:
            if st.button("Next ➡️", key="next_page"):
                if current_page < total_pages:
                    st.session_state.current_page[selected_lang] += 1
                    st.rerun()
        
        with col_jump:
            if total_pages > 1:
                jump_page = st.number_input("Jump to page", min_value=1, max_value=total_pages, value=current_page, key="jump_page")
                if jump_page != current_page:
                    st.session_state.current_page[selected_lang] = jump_page
                    st.rerun()
        
        # Search within frequency list
        st.divider()
        st.markdown("#### 🔍 Search for specific words:")
        search_term = st.text_input("Search", placeholder="e.g., 'water', 'love', 'cat'...", key="word_search")
        
        if search_term:
            search_results = search_words(selected_lang, search_term, limit=50)
            if search_results:
                st.markdown(f"**Found {len(search_results)} matching words:**")
                
                # Build dataframe for search results with ranks
                search_data = []
                for word in search_results:
                    # Get rank from database
                    from db_manager import get_word_rank
                    rank = get_word_rank(selected_lang, word)
                    search_data.append({
                        'Rank': rank,
                        'Word': word,
                        'Completed': '✓' if word in completed else ''
                    })
                
                search_df = pd.DataFrame(search_data)
                
                # Display search results
                col_rank, col_word, col_select, col_status = st.columns([0.8, 1.5, 1.2, 0.8])
                
                with col_rank:
                    st.write("**Rank**")
                with col_word:
                    st.write("**Word**")
                with col_select:
                    st.write("**Select**")
                with col_status:
                    st.write("**Status**")
                
                st.divider()
                
                for idx, row in search_df.iterrows():
                    col_rank, col_word, col_select, col_status = st.columns([0.8, 1.5, 1.2, 0.8])
                    
                    with col_rank:
                        st.write(f"#{row['Rank']}" if row['Rank'] else "—")
                    
                    with col_word:
                        st.write(row['Word'])
                    
                    with col_select:
                        is_selected = st.checkbox(
                            "Select",
                            key=f"word_search_select_{selected_lang}_{row['Word']}_{idx}",
                            label_visibility="collapsed"
                        )
                        if is_selected:
                            selected_words.append(row['Word'])
                    
                    with col_status:
                        if row['Completed']:
                            st.write("✅")
            else:
                st.info("No words found matching your search")
    
    # ========================================================================
    # CUSTOM WORD IMPORT TAB
    # ========================================================================
    
    with tab_custom:
        st.markdown("""
        **Import your own list of words** for exams, specific topics, or custom learning needs.
        
        **Example use cases:**
        - 🇨🇳 HSK Word Lists (Chinese proficiency test)
        - 📚 Exam prep (DELF, DELE, etc.)
        - 🎯 Domain-specific vocabulary (medical, business, etc.)
        - 📋 Custom topic lists
        """)
        
        st.divider()
        
        # Template download
        csv_template = get_csv_template()
        st.download_button(
            label="📥 Download CSV Template",
            data=csv_template,
            file_name="word_list_template.csv",
            mime="text/csv",
            help="Download and fill in with your own words"
        )
        
        st.markdown("**Expected format:** One word per line (plain text, CSV, or XLSX)")
        st.code("\n".join(csv_template.split('\n')[0:4]), language="text")
        
        st.divider()
        
        # File uploader
        st.markdown("**Upload your word list:**")
        uploaded_file = st.file_uploader(
            "Choose CSV or XLSX file",
            type=['csv', 'xlsx', 'xls'],
            key="custom_words_upload",
            help="First column will be used as word list"
        )
        
        if uploaded_file:
            custom_words, parse_msg = parse_uploaded_word_file(uploaded_file)
            st.info(parse_msg)
            
            if custom_words:
                is_valid, validation_msg = validate_word_list(custom_words)
                st.info(validation_msg)
                
                if is_valid:
                    st.markdown(f"#### Words from custom list ({len(custom_words)})")
                    
                    # Display custom words with selection
                    col_rank, col_word, col_select = st.columns([0.8, 1.5, 1.2])
                    
                    with col_rank:
                        st.write("**#**")
                    with col_word:
                        st.write("**Word**")
                    with col_select:
                        st.write("**Select**")
                    
                    st.divider()
                    
                    for custom_idx, word in enumerate(custom_words, 1):
                        col_rank, col_word, col_select = st.columns([0.8, 1.5, 1.2])
                        
                        with col_rank:
                            st.write(f"{custom_idx}")
                        
                        with col_word:
                            st.write(word)
                        
                        with col_select:
                            is_selected = st.checkbox(
                                "Select",
                                key=f"custom_word_select_{word}_{custom_idx}",
                                label_visibility="collapsed"
                            )
                            if is_selected:
                                if word not in selected_words:
                                    selected_words.append(word)
    
    # ========================================================================
    # SELECTION SUMMARY
    # ========================================================================
    
    st.divider()

    if selected_words:
        est_sentences = len(selected_words) * st.session_state.sentences_per_word
        st.markdown("### ⏱️ Rate Limit Monitor")
        st.caption("Stay under ~10 words per run unless you know your rate limits.*")
        col_a, col_b = st.columns(2)
        with col_a:
            st.metric("Selected words", len(selected_words))
        with col_b:
            st.metric("Est. API calls", f"{est_sentences} sentences / {est_sentences} images")
        if not st.session_state.first_run_complete and len(selected_words) > 1:
            st.warning("First run? Stick to 1 word to verify keys and audio.")
        elif len(selected_words) > 10:
            st.warning("That’s a big batch. Consider 5–10 words to avoid rate limits/timeouts.")
    
    if selected_words:
        st.success(f"✅ Selected: **{len(selected_words)} words**")
        with st.expander("View selected words"):
            st.write(", ".join(selected_words))
    else:
        st.info("📝 Select words from the frequency list or import your own")
    
    st.divider()
    
    # Step 3: Audio Settings
    st.markdown("## ⚙️ Step 3: Audio Settings")
    
    col_speed, col_pitch, col_voice = st.columns(3)
    
    with col_speed:
        audio_speed = st.slider(
            "🎵 Audio Speed",
            min_value=0.5,
            max_value=1.5,
            value=st.session_state.audio_speed,
            step=0.1,
            help="0.5 = very slow, 0.8 = learner-friendly (recommended), 1.0 = normal, 1.5 = fast"
        )
        st.session_state.audio_speed = audio_speed

    with col_pitch:
        audio_pitch = st.slider(
            "🎚️ Pitch",
            min_value=-20,
            max_value=20,
            value=st.session_state.audio_pitch,
            step=1,
            help="Pitch in Hz. Negative = lower, positive = higher (-20Hz to +20Hz)."
        )
        st.session_state.audio_pitch = audio_pitch
    
    with col_voice:
        # Get available voices for the language
        voice_options = {
            "Spanish": ["es-ES-ElviraNeural (Female)", "es-ES-AlvaroNeural (Male)", "es-MX-DaliaNeural (Female MX)"],
            "French": ["fr-FR-DeniseNeural (Female)", "fr-FR-HenriNeural (Male)"],
            "German": ["de-DE-KatjaNeural (Female)", "de-DE-ConradNeural (Male)"],
            "Italian": ["it-IT-IsabellaNeural (Female)", "it-IT-DiegoNeural (Male)"],
            "Portuguese": ["pt-BR-FranciscaNeural (Female)", "pt-BR-AntonioNeural (Male)"],
            "Russian": ["ru-RU-SvetlanaNeural (Female)", "ru-RU-DmitryNeural (Male)"],
            "Japanese": ["ja-JP-NanamiNeural (Female)", "ja-JP-KeitaNeural (Male)"],
            "Korean": ["ko-KR-SoonBokNeural (Female)", "ko-KR-InJoonNeural (Male)"],
            "Chinese (Simplified)": ["zh-CN-XiaoxiaoNeural (Female)", "zh-CN-YunxiNeural (Male)"],
            "Mandarin Chinese": ["zh-CN-XiaoxiaoNeural (Female)", "zh-CN-YunxiNeural (Male)"],
            "Arabic": ["ar-SA-LeenNeural (Female)", "ar-SA-HamedNeural (Male)"],
            "Hindi": ["hi-IN-SwaraNeural (Female)", "hi-IN-MadhurNeural (Male)"],
            "English": ["en-US-AvaNeural (Female)", "en-US-AndrewNeural (Male)", "en-GB-SoniaNeural (Female UK)"],
        }
        
        available_voices = voice_options.get(selected_lang, ["Auto-detect"])
        default_voice_display = st.session_state.selected_voice_display
        if default_voice_display and default_voice_display not in available_voices:
            default_voice_display = available_voices[0]

        selected_voice_display = st.selectbox(
            "🎤 Voice",
            options=available_voices,
            index=available_voices.index(default_voice_display) if default_voice_display in available_voices else 0,
            help="Select the voice for audio generation"
        )
        
        # Extract actual voice code from display name
        selected_voice = selected_voice_display.split(" (")[0] if "(" in selected_voice_display else None
        st.session_state.selected_voice_display = selected_voice_display
        st.session_state.selected_voice = selected_voice

    st.caption(
        f"Difficulty: **{st.session_state.difficulty}**, Sentences/word: **{st.session_state.sentences_per_word}**, "
        f"Length: **{st.session_state.sentence_length_range[0]}-{st.session_state.sentence_length_range[1]} words**, "
        f"Audio: **{st.session_state.audio_speed}x, {st.session_state.audio_pitch:+d}% pitch**, "
        f"Tracking: {'On' if st.session_state.track_progress else 'Off'}"
    )
    
    st.divider()
    
    # Step 4: Generate
    st.markdown("## ✨ Step 4: Generate Your Deck")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        if st.button(
            f"🚀 Generate Deck ({len(selected_words)} words)",
            use_container_width=True,
            disabled=len(selected_words) == 0
        ):
            # Show API estimates
            st.info(f"""
            📊 **API Usage Estimate:**
            - **Groq API calls:** ~{len(selected_words)} (1 per word for sentences)
            - **Pixabay API calls:** ~{len(selected_words) * st.session_state.sentences_per_word} (1 per sentence)
            - **Total images:** {len(selected_words) * st.session_state.sentences_per_word}
            
            Generation will begin in a moment...
            """)
            st.info("Scroll down to see the progress log.")
            st.session_state.page = "generating"
            st.session_state.selected_lang = selected_lang
            st.session_state.selected_words = selected_words
            st.rerun()
    
    with col2:
        if st.button("ℹ️ Help", use_container_width=True):
            st.session_state.page = "help"
            st.rerun()

# ============================================================================
# PAGE 3: GENERATING
# ============================================================================

elif st.session_state.page == "generating":
    
    # Auto-scroll to top of page with smooth animation
    st.markdown('<script>window.scrollTo({top: 0, behavior: "smooth"});</script>', unsafe_allow_html=True)
    
    st.markdown("# ⚙️ Generating Your Deck")
    st.markdown(f"**Language:** {st.session_state.selected_lang} | **Words:** {len(st.session_state.selected_words)}")
    st.divider()
    
    # Progress indicators - these will update in real-time
    progress_container = st.container()
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
        detail_text = st.empty()
        messages_container = st.container()
    
    try:
        # Create output directory
        import tempfile
        output_dir = tempfile.mkdtemp(prefix="anki_deck_")
        
        num_words = len(st.session_state.selected_words)
        total_sentences = num_words * st.session_state.sentences_per_word
        
        # Progress callback function - maintain cumulative log without repetition
        progress_log = []
        steps_completed = set()  # Track which steps have been logged
        
        def update_progress(step: int, message: str, details: str = ""):
            # Only add step once to log
            if step not in steps_completed:
                progress_log.append(f"✓ Step {step}/5: {message}")
                steps_completed.add(step)
                # Display cumulative log
                with messages_container:
                    st.write("\n".join(progress_log))
            
            # Always update status and details
            status_text.info(f"**Step {step}/5:** {message}")
            if step <= 5:
                progress_pct = min(0.95, (step / 5.0))
                progress_bar.progress(progress_pct)
            if details:
                detail_text.markdown(details)
        
        # Step 1: Generate sentences
        update_progress(1, "📝 Generating sentences with AI...", 
                       f"Processing {num_words} words, {st.session_state.sentences_per_word} sentences each...")
        
        # Run complete deck generation with progress callback
        result = generate_complete_deck(
            words=st.session_state.selected_words,
            language=st.session_state.selected_lang,
            groq_api_key=st.session_state.groq_api_key,
            pixabay_api_key=st.session_state.pixabay_api_key,
            output_dir=output_dir,
            num_sentences=st.session_state.sentences_per_word,
            min_length=st.session_state.sentence_length_range[0],
            max_length=st.session_state.sentence_length_range[1],
            difficulty=st.session_state.difficulty,
            audio_speed=st.session_state.audio_speed,
            pitch=st.session_state.audio_pitch,
            voice=st.session_state.selected_voice,
            all_words=st.session_state.loaded_words.get(st.session_state.selected_lang, []),
            progress_callback=update_progress,
        )
        
        if not result["success"]:
            raise Exception(result["error"])
        
        # Step 4: Generate IPA transcriptions
        update_progress(4, "🔤 Adding phonetic transcriptions (IPA)...",
                       "Generating pronunciation guides (AI + epitran fallback)")
        
        # Step 5: Create .apkg file
        update_progress(5, "📦 Creating Anki deck package (.apkg)...",
                       "Packaging cards with 3 learning modes (Listening, Production, Reading)")
        
        # Read TSV to get rows for .apkg
        import pandas as pd
        from core_functions import create_apkg_export
        
        df = pd.read_csv(
            result["tsv_path"],
            sep="\t",
            header=None,
            names=["file_name", "word", "meaning", "sentence", "ipa", "english", "audio", "image", "image_keywords", "tags"]
        )
        
        rows_for_apkg = []
        for _, row in df.iterrows():
            rows_for_apkg.append({
                "file_name": row["file_name"],
                "word": row["word"],
                "meaning": row["meaning"],
                "sentence": row["sentence"],
                "ipa": row["ipa"],
                "english": row["english"],
                "audio": row["audio"],
                "image": row["image"],
                "image_keywords": row["image_keywords"],
            })
        
        # Create .apkg file
        apkg_output = Path(output_dir) / f"{st.session_state.selected_lang}_Deck.apkg"
        created_ok = create_apkg_export(
            rows=rows_for_apkg,
            media_dir=result["media_dir"],
            output_apkg=str(apkg_output),
            language=st.session_state.selected_lang,
            deck_name=st.session_state.selected_lang
        )

        if (not created_ok) or (not apkg_output.exists()):
            raise FileNotFoundError(f".apkg was not created at {apkg_output}")
        
        # Complete
        progress_bar.progress(1.0)
        status_text.success("✅ **Deck generation complete!**")
        detail_text.markdown(f"Created {num_words} notes with {num_words * 3} cards (3 cards per word)")
        
        # Celebrate! Show balloons
        st.balloons()
        
        # Scroll to top after generation completes with smooth animation
        st.markdown('<script>window.scrollTo({top: 0, behavior: "smooth"});</script>', unsafe_allow_html=True)

        st.session_state.first_run_complete = True

        # Track progress if enabled (save to database and Firebase)
        if st.session_state.track_progress and st.session_state.selected_lang != "Custom":
            # Save to SQLite database
            mark_words_completed(st.session_state.selected_lang, st.session_state.selected_words)
            log_generation(
                st.session_state.session_id,
                st.session_state.selected_lang,
                len(st.session_state.selected_words),
                len(st.session_state.selected_words) * st.session_state.sentences_per_word
            )
            
            # Sync to Firebase
            completed_words = get_completed_words(st.session_state.selected_lang)
            stats = get_word_stats(st.session_state.selected_lang)
            sync_progress_to_firebase(st.session_state.session_id, st.session_state.selected_lang, completed_words, stats)
            log_generation_to_firebase(
                st.session_state.session_id,
                st.session_state.selected_lang,
                len(st.session_state.selected_words),
                len(st.session_state.selected_words) * st.session_state.sentences_per_word
            )
        
        # Read and store .apkg for download
        with open(apkg_output, "rb") as f:
            st.session_state.apkg_file = f.read()
            st.session_state.apkg_filename = apkg_output.name
        
        # Scroll to download section
        st.markdown('<script>window.scrollTo(0, document.body.scrollHeight);</script>', unsafe_allow_html=True)
        
        st.session_state.page = "complete"
        st.rerun()
        
    except Exception as e:
        st.error(f"❌ **Error:** {str(e)}")
        st.error(f"**Details:** {type(e).__name__}")
        
        if st.button("← Back to Main"):
            st.session_state.page = "main"
            st.rerun()

# ============================================================================
# PAGE 4: COMPLETE
# ============================================================================

elif st.session_state.page == "complete":
    
    st.markdown("# ✅ Your Anki Deck is Ready!")
    total_cards = len(st.session_state.selected_words) * 3  # 3 cards per word
    st.markdown(f"**{len(st.session_state.selected_words)} words** • **{total_cards} cards** (3 learning modes per word) • **Ready to import!**")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📥 Download Your Deck")
        st.markdown("""
        Your .apkg file includes:
        - ✅ All flashcards with 3 card types each
        - ✅ Audio files (embedded)
        - ✅ Images (embedded)
        - ✅ IPA transcriptions
        - ✅ Image search keywords
        
        **3 Card Types:**
        1. 🎧 **Listening**: Hear → Understand
        2. 💬 **Production**: English → Speak target language
        3. 📖 **Reading**: Read → Comprehend
        """)
        
        if "apkg_file" in st.session_state and st.session_state.apkg_file:
            st.download_button(
                label="⬇️ Download Anki Deck (.apkg)",
                data=st.session_state.apkg_file,
                file_name=st.session_state.get("apkg_filename", f"{st.session_state.selected_lang.replace(' ', '_')}_deck.apkg"),
                mime="application/octet-stream",
                use_container_width=True
            )
    
    with col2:
        st.markdown("### 📖 How to Import")
        st.markdown(f"""
        **Super Easy! Just 2 steps:**
        
        1. **Double-click** the downloaded .apkg file
        2. Anki opens and imports automatically! ✨
        
        **Or manually:**
        1. Open Anki
        2. File → Import...
        3. Select the .apkg file
        4. Click Import
        
        **All done!** Your {st.session_state.selected_lang} deck with {total_cards} cards is ready to study.
        
        Cards include audio, images, and phonetic guides (IPA) for pronunciation.
        """)
    
    st.divider()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Generate Another", use_container_width=True):
            st.session_state.page = "main"
            st.rerun()
    with col2:
        if st.button("🔐 Change Keys", use_container_width=True):
            st.session_state.page = "api_setup"
            st.rerun()
    with col3:
        if st.button("ℹ️ Help", use_container_width=True):
            st.session_state.page = "help"
            st.rerun()

# ============================================================================
# PAGE 5: UPLOAD CSV
# ============================================================================

elif st.session_state.page == "upload":
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("# 📥 Upload Your Own Words")
    with col2:
        if st.button("← Back"):
            st.session_state.page = "main"
            st.rerun()
    
    st.divider()
    
    csv_template = get_csv_template()
    st.download_button(
        label="📋 Download CSV Template",
        data=csv_template,
        file_name="word_list_template.csv",
        mime="text/csv",
        use_container_width=True
    )
    
    st.divider()
    
    uploaded_file = st.file_uploader("Choose CSV or XLSX file", type=["csv", "xlsx"])
    
    if uploaded_file:
        try:
            if uploaded_file.type == "text/csv":
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            
            words = df.iloc[:, 0].dropna().tolist()
            words = [str(w).strip() for w in words if w]
            
            is_valid, message = validate_word_list(words)
            
            if is_valid:
                st.success(message)
                col1, col2 = st.columns(2)
                col1.metric("Words", len(words))
                col2.metric("Ready", "✅")
                
                st.divider()
                
                if st.button("🚀 Generate from Custom Words", use_container_width=True):
                    st.session_state.selected_lang = "Custom"
                    st.session_state.selected_words = words
                    st.session_state.page = "generating"
                    st.rerun()
            else:
                st.error(message)
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ============================================================================
# PAGE 6: HELP
# ============================================================================

elif st.session_state.page == "help":
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("# ℹ️ Help & FAQ")
    with col2:
        if st.button("← Back"):
            st.session_state.page = "main"
            st.rerun()
    
    st.divider()
    
    st.markdown("""
    ## What does this app do?
    
    Creates custom Anki decks by:
    1. **Selecting words** from frequency lists
    2. **Generating sentences** in your language (Groq AI)
    3. **Creating audio** at 0.8x speed (learner-friendly)
    4. **Downloading images** (Pixabay)
    5. **Creating Anki files** ready to import
    
    ## Cost?
    **Completely FREE!**
    - Groq: Free tier
    - Pixabay: Free tier (5,000 images/day)
    
    ## How long?
    - 5 words: 5-10 min
    - 10 words: 10-15 min
    - 20 words: 20-30 min
    
    ## Privacy?
    Your data stays with you, nothing stored on our servers.
    
    ## Errors?
    1. Check API keys
    2. Check internet
    3. Try 3-5 words first
    4. Refresh & try again
    """)
