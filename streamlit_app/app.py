"""
Fluent Forever Anki Card Generator - Streamlit GUI
Production-ready, accessible for ages 10-90
"""

import streamlit as st
import yaml
import os
from pathlib import Path
import tempfile
from datetime import datetime
import pandas as pd
from core_functions import (
    generate_sentences,
    generate_audio,
    generate_images_pixabay,
    create_anki_tsv,
    create_zip_export,
    estimate_api_costs,
    get_available_voices,
    parse_csv_upload,
)

# ============================================================================
# PAGE CONFIG & STYLING
# ============================================================================

st.set_page_config(
    page_title="Fluent Forever Anki Generator",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# High contrast dark theme with large fonts
st.markdown("""
<style>
    :root {
        --base-font-size: 16px;
    }
    
    body {
        font-size: var(--base-font-size);
        background-color: #0e1117;
        color: #e6edf3;
    }
    
    /* High contrast colors */
    .stTitle {
        font-size: 2.5rem !important;
        font-weight: bold;
        color: #58a6ff;
    }
    
    .stMarkdown h1 {
        font-size: 2.2rem !important;
        color: #58a6ff;
    }
    
    .stMarkdown h2 {
        font-size: 1.8rem !important;
        color: #79c0ff;
    }
    
    .stMarkdown h3 {
        font-size: 1.4rem !important;
        color: #a5d6ff;
    }
    
    .stButton > button {
        font-size: 1.1rem !important;
        padding: 0.8rem 1.6rem !important;
        background-color: #238636 !important;
        color: white !important;
        border-radius: 6px !important;
        border: 2px solid #3fb950 !important;
    }
    
    .stButton > button:hover {
        background-color: #2ea043 !important;
        border-color: #56d364 !important;
    }
    
    .stSelectbox, .stSlider, .stFileUploader, .stTextInput {
        font-size: 1.05rem !important;
    }
    
    .stInfo, .stSuccess, .stWarning, .stError {
        font-size: 1.1rem !important;
        padding: 1.2rem !important;
    }
    
    /* Accessible colors for colorblind users */
    .stInfo {
        background-color: #0550ae !important;
        border-color: #79c0ff !important;
    }
    
    .stSuccess {
        background-color: #1f6feb !important;
        border-color: #58a6ff !important;
    }
    
    .stWarning {
        background-color: #8b4513 !important;
        border-color: #d9a040 !important;
    }
    
    .stError {
        background-color: #da3633 !important;
        border-color: #f85149 !important;
    }
    
    .stTooltip {
        font-size: 0.95rem !important;
    }
    
    .metric-box {
        background-color: #161b22;
        border: 2px solid #30363d;
        border-radius: 8px;
        padding: 1.2rem;
        margin: 0.8rem 0;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# LOAD CONFIGURATION
# ============================================================================

@st.cache_resource
def load_languages():
    """Load language configuration from YAML."""
    yaml_path = Path(__file__).parent / "languages.yaml"
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

languages_config = load_languages()
top_5 = languages_config["top_5"]
all_languages = languages_config["all_languages"]
ui_strings_all = languages_config["ui_strings"]

# ============================================================================
# SESSION STATE & UTILS
# ============================================================================

if "app_language" not in st.session_state:
    st.session_state.app_language = "en"

if "generated_data" not in st.session_state:
    st.session_state.generated_data = None

def t(key: str) -> str:
    """Translate UI string."""
    lang = st.session_state.app_language
    if lang not in ui_strings_all:
        lang = "en"
    return ui_strings_all[lang].get(key, key)

# ============================================================================
# SIDEBAR: API KEYS & SETTINGS
# ============================================================================

with st.sidebar:
    st.markdown("## 🔑 API Keys & Settings", unsafe_allow_html=True)
    
    # Language selector (top 5 + all)
    st.markdown("### UI Language")
    lang_options = ["English", "Español", "Français", "हिन्दी", "中文"]
    lang_codes = ["en", "es", "fr", "hi", "zh"]
    selected_lang_idx = st.selectbox(
        "Select interface language:",
        range(len(lang_options)),
        format_func=lambda i: lang_options[i],
        key="lang_select"
    )
    st.session_state.app_language = lang_codes[selected_lang_idx]
    
    st.divider()
    
    # API Key inputs
    st.markdown("### Groq API")
    st.info(t("groq_info"))
    groq_key = st.text_input(
        t("groq_api_key"),
        type="password",
        value=st.secrets.get("GROQ_API_KEY", ""),
        key="groq_input"
    )
    
    st.markdown("### Pixabay API")
    st.info(t("pixabay_info"))
    pixabay_key = st.text_input(
        t("pixabay_api_key"),
        type="password",
        value=st.secrets.get("PIXABAY_API_KEY", ""),
        key="pixabay_input"
    )
    
    st.info("📢 Edge TTS is free and requires no API key!")
    
    st.divider()
    
    # Generation settings
    st.markdown("### " + t("settings"))
    
    num_sentences = st.slider(
        t("num_sentences"),
        min_value=1,
        max_value=20,
        value=10,
        step=1,
        help="More sentences = more variety in contexts"
    )
    
    min_length = st.slider(
        t("sentence_length_min"),
        min_value=3,
        max_value=10,
        value=5,
    )
    
    max_length = st.slider(
        t("sentence_length_max"),
        min_value=min_length + 1,
        max_value=30,
        value=20,
    )
    
    difficulty = st.selectbox(
        t("difficulty"),
        ["beginner", "intermediate", "advanced"],
        help="Complexity of sentence structures and vocabulary"
    )
    
    st.divider()
    
    # TTS Settings
    st.markdown("### 🔊 Audio Settings")
    
    playback_speed = st.slider(
        "Playback Speed",
        min_value=0.5,
        max_value=2.0,
        value=0.8,
        step=0.1,
        help="0.8 is recommended for language learners"
    )
    
    st.markdown("### Randomize Voice")
    randomize_voice = st.checkbox("Randomize within language", value=False)
    
    st.divider()
    
    # Image settings
    st.markdown("### 🖼️ Image Settings")
    randomize_images = st.checkbox("Randomize image selection", value=True)

# ============================================================================
# MAIN CONTENT
# ============================================================================

# Header
st.markdown(f"# {t('title')}", unsafe_allow_html=True)
st.markdown(f"### {t('subtitle')}")

# Language selector (main)
st.markdown(f"## {t('select_language')}")

col1, col2 = st.columns([1, 2])

with col1:
    st.markdown("**Most Spoken (Quick Start)**")
    top_5_names = [lang["name"] for lang in top_5]
    top_5_codes = [lang["code"] for lang in top_5]
    selected_top_5 = st.selectbox(
        label="Top 5",
        options=range(len(top_5)),
        format_func=lambda i: f"{top_5[i]['flag']} {top_5[i]['name']} ({top_5[i]['speakers']})",
        key="top_5_select"
    )
    selected_lang_code = top_5_codes[selected_top_5]
    selected_lang_name = top_5_names[selected_top_5]

with col2:
    st.markdown("**All 109 Languages**")
    all_names = [lang["name"] for lang in all_languages]
    all_codes = [lang["code"] for lang in all_languages]
    selected_all = st.selectbox(
        label="Full List",
        options=range(len(all_languages)),
        format_func=lambda i: all_languages[i]["name"],
        key="all_lang_select"
    )
    selected_lang_code = all_codes[selected_all]
    selected_lang_name = all_languages[selected_all]["name"]

# Voice selection
available_voices = get_available_voices(selected_lang_code)
if randomize_voice:
    import random
    default_voice = random.choice(available_voices)
else:
    default_voice = available_voices[0]

selected_voice = st.selectbox(
    t("voice"),
    options=available_voices,
    index=0 if not randomize_voice else random.randint(0, len(available_voices)-1)
)

st.divider()

# ============================================================================
# WORD INPUT
# ============================================================================

st.markdown(f"## {t('word_input_section')}")

input_method = st.radio(
    "How would you like to enter words?",
    ["Single Word", "Upload CSV", "Frequency List"],
    horizontal=True
)

words_to_process = []

if input_method == "Single Word":
    col1, col2 = st.columns(2)
    with col1:
        word = st.text_input(t("word_label"), placeholder="e.g., 'casa', 'hola'")
    with col2:
        meaning = st.text_input(t("meaning_label"), placeholder="e.g., 'house', 'hello'")
    
    if word and meaning:
        words_to_process = [{"word": word, "meaning": meaning}]

elif input_method == "Upload CSV":
    st.markdown(f"**{t('csv_info')}**")
    csv_file = st.file_uploader("Choose CSV file", type=["csv"])
    
    if csv_file:
        words_to_process = parse_csv_upload(csv_file.read())
        st.success(f"✅ Loaded {len(words_to_process)} words")

elif input_method == "Frequency List":
    # TODO: Load frequency lists from Excel files
    st.info("Frequency list feature coming soon! For now, use 'Single Word' or 'Upload CSV'")

st.divider()

# ============================================================================
# COST CALCULATOR
# ============================================================================

st.markdown(f"## {t('cost_calculator')}")

if words_to_process:
    costs = estimate_api_costs(len(words_to_process), num_sentences)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Sentences",
            costs["total_sentences"],
            f"@ {num_sentences} per word"
        )
    
    with col2:
        st.metric(
            "Images",
            costs["total_images"],
            "From Pixabay"
        )
    
    with col3:
        st.metric(
            "Pixabay Requests",
            costs["pixabay_requests"],
            "Free: 5,000/day"
        )
    
    with col4:
        st.metric(
            "Groq Tokens",
            f"~{costs['groq_tokens_est']:,}",
            "Monitor at console.groq.com"
        )
    
    st.info(
        f"✅ **Safe for free tier**: {costs['pixabay_requests']} image requests "
        f"(limit 5,000/day) | {costs['groq_tokens_est']:,} Groq tokens (unlimited free)"
    )

st.divider()

# ============================================================================
# DEMO BUTTON
# ============================================================================

if st.button(f"📚 {t('demo_button')}", use_container_width=True):
    st.info("Demo: Generating 1 sentence in English...")
    
    try:
        if not groq_key:
            st.error("❌ Groq API key required for demo")
        else:
            sentences = generate_sentences(
                word="house",
                meaning="a building for living",
                language="English",
                num_sentences=1,
                min_length=5,
                max_length=15,
                difficulty="beginner",
                groq_api_key=groq_key,
            )
            
            if sentences:
                st.success(f"✅ Generated sentence:")
                st.json(sentences[0])
                
                # Try audio
                audio_files = generate_audio(
                    sentences=[sentences[0]["sentence"]],
                    voice=selected_voice,
                    output_dir=Path(tempfile.gettempdir()) / "demo_audio",
                    batch_name="demo",
                    rate=playback_speed,
                )
                
                if audio_files:
                    st.success("✅ Audio generated!")
                    audio_path = Path(tempfile.gettempdir()) / "demo_audio" / audio_files[0]
                    st.audio(str(audio_path))
            else:
                st.error("❌ Failed to generate sentence. Check Groq API key.")
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")

st.divider()

# ============================================================================
# GENERATE BUTTON
# ============================================================================

if words_to_process:
    if st.button(f"✨ {t('generate_button')}", use_container_width=True):
        progress_placeholder = st.empty()
        
        try:
            if not groq_key or not pixabay_key:
                st.error("❌ Groq and Pixabay API keys required")
            else:
                with st.spinner(t("generating")):
                    generated_data = []
                    
                    for idx, word_info in enumerate(words_to_process):
                        progress_placeholder.progress((idx) / len(words_to_process))
                        
                        word = word_info["word"]
                        meaning = word_info["meaning"]
                        
                        # Generate sentences
                        sentences = generate_sentences(
                            word=word,
                            meaning=meaning,
                            language=selected_lang_name,
                            num_sentences=num_sentences,
                            min_length=min_length,
                            max_length=max_length,
                            difficulty=difficulty,
                            groq_api_key=groq_key,
                        )
                        
                        if not sentences:
                            st.warning(f"⚠️ Failed to generate sentences for '{word}'")
                            continue
                        
                        # Generate audio
                        sentences_text = [s["sentence"] for s in sentences]
                        with tempfile.TemporaryDirectory() as tmpdir:
                            audio_dir = Path(tmpdir) / "audio"
                            audio_files = generate_audio(
                                sentences=sentences_text,
                                voice=selected_voice,
                                output_dir=str(audio_dir),
                                batch_name=f"{idx+1:03d}_{word}",
                                rate=playback_speed,
                            )
                            
                            # Generate images
                            english_sentences = [s["english_translation"] for s in sentences]
                            image_dir = Path(tmpdir) / "images"
                            image_files = generate_images_pixabay(
                                queries=english_sentences,
                                output_dir=str(image_dir),
                                batch_name=f"{idx+1:03d}_{word}",
                                pixabay_api_key=pixabay_key,
                                randomize=randomize_images,
                            )
                            
                            generated_data.append({
                                "word": word,
                                "meaning": meaning,
                                "sentences": sentences,
                                "audio_files": audio_files,
                                "image_files": image_files,
                                "audio_dir": str(audio_dir),
                                "image_dir": str(image_dir),
                            })
                    
                    progress_placeholder.progress(1.0)
                    
                    if generated_data:
                        st.session_state.generated_data = generated_data
                        st.success(f"✅ Generated {len(generated_data)} word(s)")
                    else:
                        st.error("❌ No data generated. Check API keys and try again.")
        
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# ============================================================================
# DOWNLOAD SECTION
# ============================================================================

if st.session_state.generated_data:
    st.divider()
    st.markdown("## 📥 Download Your Anki Deck")
    
    # Create TSV + ZIP
    with tempfile.TemporaryDirectory() as tmpdir:
        tsv_path = Path(tmpdir) / "ANKI_IMPORT.tsv"
        zip_path = Path(tmpdir) / "AnkiDeck.zip"
        
        # Collect all audio/image files
        all_audio_files = {}
        all_image_files = {}
        
        for word_data in st.session_state.generated_data:
            word = word_data["word"]
            for i, audio_file in enumerate(word_data["audio_files"]):
                key = f"{word}_{i+1}"
                all_audio_files[key] = Path(word_data["audio_dir"]) / audio_file
            
            for i, image_file in enumerate(word_data["image_files"]):
                key = f"{word}_{i+1}"
                all_image_files[key] = Path(word_data["image_dir"]) / image_file
        
        # Create TSV
        create_anki_tsv(st.session_state.generated_data, str(tsv_path))
        
        # Create ZIP
        create_zip_export(
            str(tsv_path),
            str(Path(st.session_state.generated_data[0]["audio_dir"]).parent),
            str(Path(st.session_state.generated_data[0]["image_dir"]).parent),
            str(zip_path),
        )
        
        # Download button
        with open(zip_path, "rb") as f:
            st.download_button(
                label=f"📥 {t('download_zip')}",
                data=f.read(),
                file_name=f"AnkiDeck_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip",
                mime="application/zip",
                use_container_width=True,
            )

st.divider()

# ============================================================================
# ANKI INSTRUCTIONS
# ============================================================================

st.markdown(f"## {t('anki_instructions')}")

col1, col2, col3 = st.columns([1, 1, 1])

with col1:
    st.markdown(f"**{t('instruction_1')}**")
    st.markdown(f"**{t('instruction_2')}**")
    st.markdown(f"**{t('instruction_3')}**")

with col2:
    st.markdown(f"**{t('instruction_4')}**")
    st.markdown(f"**{t('instruction_5')}**")

with col3:
    st.markdown(f"**{t('instruction_6')}**")

st.info(
    "💡 **Tip**: Your Anki media folder is usually located at:\n"
    "- Windows: `C:\\Users\\<YourUsername>\\AppData\\Roaming\\Anki2\\User 1\\collection.media`\n"
    "- Mac: `~/Library/Application Support/Anki2/User 1/collection.media`\n"
    "- Linux: `~/.local/share/Anki2/User 1/collection.media`"
)

st.divider()

st.markdown("---")
st.markdown(
    "Made with ❤️ for language learners | "
    "[GitHub](https://github.com/agnel18/anki-fluent-forever-language-card-generator)"
)
