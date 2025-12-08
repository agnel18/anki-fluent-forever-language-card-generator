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
)
from frequency_utils import (
    get_available_frequency_lists,
    load_frequency_list,
    BATCH_PRESETS,
    validate_word_list,
    get_csv_template,
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
    
    st.markdown("### 🎵 Google Cloud TTS (Optional Fallback)")
    
    # Check if Google TTS credentials exist
    creds_file = Path(__file__).parent.parent / "languagelearning-480303-93748916f7bd.json"
    google_tts_ready = creds_file.exists()
    
    if google_tts_ready:
        st.success("✅ Google Cloud TTS is configured! (Will auto-use as fallback if Edge TTS fails)")
    else:
        with st.expander("📖 Setup Google Cloud TTS (Optional but Recommended)", expanded=False):
            st.markdown("""
            **What it's for:** Backup audio generation if Edge TTS fails
            
            **Why optional?** Edge TTS usually works fine. Google TTS is just a safety net.
            
            **Setup Instructions (5 minutes):**
            
            1. **Create Google Cloud Account**
               - Go to https://console.cloud.google.com
               - Click "Create Project"
               - Name it: "Language Learning" (or anything)
               - Click Create
            
            2. **Enable Text-to-Speech API**
               - Search for "Text-to-Speech API" in the search bar
               - Click on it
               - Click "ENABLE"
               - Wait 30 seconds for it to activate
            
            3. **Create Service Account**
               - Go to https://console.cloud.google.com/iam-admin/serviceaccounts
               - Click "Create Service Account"
               - Name: `language-learning-tts`
               - Click "Create and Continue"
               - Click "Continue" again (skip optional steps)
               - Click "Done"
            
            4. **Create JSON Key**
               - You'll see your service account listed
               - Click on it (the email address)
               - Click "KEYS" tab at the top
               - Click "Add Key" → "Create new key"
               - Choose "JSON"
               - Click "Create"
               - A file will download: `service-account-key.json`
            
            5. **Rename & Place File**
               - Rename the downloaded file to: `languagelearning-480303-93748916f7bd.json`
               - Move it to the main project folder
               - Location should be: `d:\\Language Learning\\LanguagLearning\\languagelearning-480303-93748916f7bd.json`
               - **Then restart the app** (refresh this page)
            
            **That's it!** Google TTS will auto-activate as fallback.
            
            **Cost:** Free tier includes 1 million characters/month. Usually enough unless generating thousands of decks.
            """)
    
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
            st.rerun()

# ============================================================================
# PAGE 2: MAIN APP
# ============================================================================

elif st.session_state.page == "main":
    
    col1, col2 = st.columns([4, 1])
    with col1:
        st.markdown("# 🌍 Language Learning Anki Deck Generator")
    with col2:
        if st.button("🔐 Change Keys"):
            st.session_state.page = "api_setup"
            st.rerun()
    
    st.divider()
    
    # Step 1: Language
    st.markdown("## 📋 Step 1: Select Language")
    lang_names = [lang["name"] for lang in all_languages]
    selected_lang = st.selectbox("Which language do you want to learn?", lang_names)
    
    available_lists = get_available_frequency_lists()
    max_words = available_lists.get(selected_lang, 5000)
    col1, col2 = st.columns([3, 1])
    col2.metric("Available", f"{max_words:,} words")
    
    st.divider()
    
    # Step 2: Batch size
    st.markdown("## ⏱️ Step 2: Choose Batch Size")
    st.markdown("*(10 sentences per word)*")
    
    batch_options = []
    batch_values = []
    for batch_size, info in BATCH_PRESETS.items():
        label = f"{info['emoji']} {batch_size} words • {info['time_estimate']}"
        batch_options.append(label)
        batch_values.append(batch_size)
    
    selected_batch_idx = batch_values.index(st.session_state.current_batch_size)
    selected_batch_label = st.radio("Select batch size:", batch_options, index=selected_batch_idx, label_visibility="collapsed")
    selected_batch_size = batch_values[batch_options.index(selected_batch_label)]
    st.session_state.current_batch_size = selected_batch_size
    
    st.divider()
    
    # Step 3: Select words
    st.markdown("## 📚 Step 3: Select Your Words")
    
    # Load words for this language (cached)
    if selected_lang not in st.session_state.loaded_words:
        with st.spinner(f"Loading {selected_lang} word list..."):
            try:
                all_words = load_frequency_list(selected_lang, limit=1000)
                # Header row is already skipped in load_frequency_list()
                if not all_words:
                    st.warning(f"⚠️ No word list found for {selected_lang}")
                    all_words = [f"word_{i}" for i in range(1, 51)]
                st.session_state.loaded_words[selected_lang] = all_words
            except Exception as e:
                st.error(f"❌ Error loading words: {str(e)}")
                all_words = [f"word_{i}" for i in range(1, 51)]
                st.session_state.loaded_words[selected_lang] = all_words
    
    all_words = st.session_state.loaded_words[selected_lang]
    completed = st.session_state.completed_words.get(selected_lang, [])
    remaining = [w for w in all_words if w not in completed]
    
    st.markdown(f"**Total words:** {len(all_words)} | **Completed:** {len(completed)} | **Remaining:** {len(remaining)}")
    
    # Selection Mode Tabs
    tab1, tab2, tab3 = st.tabs(["🎯 Range-Based", "🔍 Manual Pick", "⚡ Quick Options"])
    
    selected_words = []
    
    # ============================================================================
    # TAB 1: RANGE-BASED SELECTION
    # ============================================================================
    with tab1:
        st.markdown("**Select words by frequency rank**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            mode = st.radio(
                "Which words?",
                ["Top (most common)", "Skip completed", "Custom range"],
                label_visibility="collapsed"
            )
        
        if mode == "Top (most common)":
            batch_start = 0
            batch_end = min(selected_batch_size, len(all_words))
            display_words = all_words[batch_start:batch_end]
            st.markdown(f"**Words 1-{batch_end}** (Most common first)")
            
        elif mode == "Skip completed":
            if len(completed) > 0:
                batch_end = min(len(completed) + selected_batch_size, len(all_words))
                display_words = all_words[len(completed):batch_end]
                st.markdown(f"**Words {len(completed)+1}-{batch_end}** (After your last completed words)")
            else:
                batch_end = min(selected_batch_size, len(all_words))
                display_words = all_words[0:batch_end]
                st.info("📝 You haven't completed any words yet. Starting from the beginning!")
        
        else:  # Custom range
            st.markdown("**Enter custom range:**")
            col1, col2 = st.columns(2)
            with col1:
                start = st.number_input("Start from word #", min_value=1, max_value=len(all_words), value=1, key="range_start")
            with col2:
                num_words = st.number_input("How many words?", min_value=1, max_value=100, value=5, key="range_count")
            
            batch_start = start - 1
            batch_end = min(start - 1 + num_words, len(all_words))
            display_words = all_words[batch_start:batch_end]
            st.markdown(f"**Words {start}-{batch_end}** ({batch_end - batch_start} words total)")
        
        # Show checkboxes
        st.markdown("*Select which words:*")
        cols = st.columns(5)
        for idx, word in enumerate(display_words):
            with cols[idx % 5]:
                is_completed = word in completed
                checkbox_label = f"{word}"
                if is_completed:
                    checkbox_label += " ✓"
                
                if st.checkbox(checkbox_label, key=f"range_{word}_{idx}"):
                    selected_words.append(word)
    
    # ============================================================================
    # TAB 2: MANUAL PICK
    # ============================================================================
    with tab2:
        st.markdown("**Search and manually select any words**")
        
        search_term = st.text_input(
            "Search for words:",
            placeholder="e.g., 'water', 'love', 'cat'...",
            key="word_search"
        )
        
        if search_term:
            search_lower = search_term.lower()
            filtered = [w for w in all_words if search_lower in w.lower()]
            st.markdown(f"**Found {len(filtered)} matching words:**")
        else:
            filtered = all_words[:50]  # Show first 50 if no search
            st.markdown(f"**Showing first 50 words (type to search):**")
        
        cols = st.columns(5)
        for idx, word in enumerate(filtered):
            with cols[idx % 5]:
                is_completed = word in completed
                checkbox_label = f"{word}"
                if is_completed:
                    checkbox_label += " ✓"
                
                if st.checkbox(checkbox_label, key=f"manual_{word}_{idx}"):
                    selected_words.append(word)
    
    # ============================================================================
    # TAB 3: QUICK OPTIONS
    # ============================================================================
    with tab3:
        st.markdown("**Quick selection presets**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🔥 Top 10 (Most Common)", use_container_width=True):
                selected_words = all_words[:10]
                st.success(f"✅ Selected top 10 words")
        
        with col2:
            if st.button("📈 Next 10 (11-20)", use_container_width=True):
                selected_words = all_words[10:20]
                st.success(f"✅ Selected words 11-20")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🎲 Random 10 Words", use_container_width=True):
                import random
                selected_words = random.sample(all_words, min(10, len(all_words)))
                st.success(f"✅ Selected 10 random words")
        
        with col2:
            if len(completed) > 0:
                if st.button(f"⏭️ Continue ({len(completed)} done)", use_container_width=True):
                    start_idx = len(completed)
                    end_idx = min(len(completed) + 10, len(all_words))
                    selected_words = all_words[start_idx:end_idx]
                    st.success(f"✅ Continuing from word {start_idx+1}")
            else:
                st.info("📝 No progress yet. Complete some words first!")
    
    # Summary
    st.divider()
    if selected_words:
        st.success(f"✅ Selected: **{len(selected_words)} words**")
        with st.expander("View selected words"):
            st.write(", ".join(selected_words))
    else:
        st.info(f"📝 Select words from one of the tabs above")
    
    st.divider()
    
    # Step 4: Audio Settings
    st.markdown("## ⚙️ Step 4: Audio Settings")
    
    col_speed, col_voice = st.columns(2)
    
    with col_speed:
        audio_speed = st.slider(
            "🎵 Audio Speed",
            min_value=0.5,
            max_value=1.5,
            value=0.8,
            step=0.1,
            help="0.5 = very slow, 0.8 = learner-friendly (recommended), 1.0 = normal, 1.5 = fast"
        )
    
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
        
        available_voices = voice_options.get(language, ["Auto-detect"])
        selected_voice_display = st.selectbox(
            "🎤 Voice",
            options=available_voices,
            help="Select the voice for audio generation"
        )
        
        # Extract actual voice code from display name
        selected_voice = selected_voice_display.split(" (")[0] if "(" in selected_voice_display else None
    
    st.divider()
    
    # Step 5: Generate
    st.markdown("## ✨ Step 5: Generate Your Deck")
    
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.button(
            f"🚀 Generate Deck ({len(selected_words)} words)",
            use_container_width=True,
            disabled=len(selected_words) == 0
        ):
            st.session_state.page = "generating"
            st.session_state.selected_lang = selected_lang
            st.session_state.selected_words = selected_words
            st.rerun()
    
    with col2:
        if st.button("📥 Upload CSV", use_container_width=True):
            st.session_state.page = "upload"
            st.rerun()
    
    with col3:
        if st.button("ℹ️ Help", use_container_width=True):
            st.session_state.page = "help"
            st.rerun()

# ============================================================================
# PAGE 3: GENERATING
# ============================================================================

elif st.session_state.page == "generating":
    
    st.markdown("# ⚙️ Generating Your Deck")
    st.markdown(f"**Language:** {st.session_state.selected_lang} | **Words:** {len(st.session_state.selected_words)}")
    st.divider()
    
    progress_bar = st.progress(0, text="Starting generation...")
    status_text = st.empty()
    
    try:
        # Create output directory
        import tempfile
        output_dir = tempfile.mkdtemp(prefix="anki_deck_")
        
        # Run complete deck generation
        status_text.info("🚀 **Starting deck generation...**")
        st.write("This will generate sentences, audio, images, and create your Anki deck.")
        
        result = generate_complete_deck(
            words=st.session_state.selected_words,
            language=st.session_state.selected_lang,
            groq_api_key=st.session_state.groq_api_key,
            pixabay_api_key=st.session_state.pixabay_api_key,
            output_dir=output_dir,
            num_sentences=10,
            audio_speed=audio_speed,
            voice=selected_voice,
            all_words=st.session_state.loaded_words.get(st.session_state.selected_lang, []),
        )
        
        if not result["success"]:
            raise Exception(result["error"])
        
        # Update progress
        progress_bar.progress(90, text="Finalizing ZIP file...")
        status_text.info("📦 **Step 4/4:** Creating final ZIP export...")
        
        # Create ZIP file
        zip_output = Path(output_dir) / "AnkiDeck.zip"
        create_zip_export(
            tsv_path=result["tsv_path"],
            media_dir=result["media_dir"],
            output_zip=str(zip_output),
        )
        
        # Complete
        progress_bar.progress(100, text="Complete!")
        status_text.empty()
        
        st.success("✅ **Your Anki deck is ready!**")
        
        # Read and store ZIP for download
        with open(zip_output, "rb") as f:
            st.session_state.zip_file = f.read()
        
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
    st.markdown(f"**{len(st.session_state.selected_words)} words** • **{len(st.session_state.selected_words) * 10} sentences** • **Ready to import**")
    st.divider()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📥 Download")
        st.markdown("""
        Your ZIP file contains:
        - ✅ ANKI_IMPORT.tsv
        - ✅ Audio files (MP3s)
        - ✅ Images (JPGs)
        """)
        
        if "zip_file" in st.session_state and st.session_state.zip_file:
            st.download_button(
                label="⬇️ Download Anki Deck",
                data=st.session_state.zip_file,
                file_name=f"{st.session_state.selected_lang.replace(' ', '_')}_deck.zip",
                mime="application/zip",
                use_container_width=True
            )
    
    with col2:
        st.markdown("### 📖 How to Import")
        st.markdown("""
        1. Open Anki
        2. File → Import...
        3. Select ANKI_IMPORT.tsv
        4. Click Import
        5. Your deck appears! ✨
        
        Images & audio auto-import.
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
