# Fluent Forever Anki Language Card Generator

Generate professional language learning cards for Anki with sentences, audio, images, and IPA transliterations. **Support for 109 languages** with frequency word lists, dynamic language selection, and intelligent sentence generation using **Groq (llama-3.3-70b)** or Google Gemini.

**Based on the [Fluent Forever method](https://fluent-forever.com/) by Gabriel Wyner** - A proven language learning system using spaced repetition, personalized sentences, and multi-sensory memory techniques.

📖 **Book:** [Fluent Forever: How to Learn Any Language Fast and Never Forget It](https://www.amazon.com/Fluent-Forever-Learn-Language-Forget/dp/0385348118) by Gabriel Wyner

## About This Repository

- Language-agnostic pipeline (109 frequency lists included) with one-click language selection.
- Packaged Anki note-type: `Anki Language Template/Language Learning Template.apkg` (no manual setup; works for any language).
- Modernized media pipeline: Gemini sentences, soundoftext audio, Pexels thumbnails via English translation, restartable scripts.
- Outputs ready for Anki import: TSV + media under `FluentForever_{Language}_Perfect/`.

## Features

- 🤖 **AI-Powered Sentences**: Uses **Groq llama-3.3-70b** by default (set `USE_GROQ=1`) with Google Gemini fallback; generates **10 natural sentences per word**
- ✅ **All Use Cases Covered**: Different grammatical contexts, tenses, formality levels, and real-world usage
- 🌍 **109 Languages Supported**: Instantly switch between any language with 1 command
- 📋 **Built-in Frequency Lists**: Curated most-common-words lists for all languages (ready to use)
- 🔊 **Audio**: Downloads native speaker audio from **Google Cloud Text-to-Speech** via service account (fallback: soundoftext.com)
- 🖼️ **Images**: Downloads clean thumbnail images from **Pexels** (uses English translation for better results)
- 📝 **IPA Transliteration**: Includes International Phonetic Alphabet for pronunciation
- 📊 **Progress Tracking**: Tracks processing status for each word
- 🔄 **Restartable**: Each script is independent and can be restarted without losing work
- ⚙️ **Language-Agnostic**: Works with any language's frequency list

### Image Download (Pexels) – Setup, Benefits, and Ethics

- **Setup:** Add your Pexels API key to `.env` (kept out of git).
   ```
   PEXELS_API_KEY=your_pexels_key_here
   ```
- **How it works:** Script 3 (`3_download_images.py`) searches **Pexels** with the **English translation** of each sentence and downloads a **thumbnail** (`tiny`) to keep downloads light and fast.
- **Rate limits:** Pexels free tier is roughly **~200 requests/hour**. A full deck (6,250 images) should be run in batches (e.g., 200–400 images, pause 1–2 hours, then continue) to avoid throttling.
- **Ethical use:** Respect the rate limits, avoid excessive retries, and keep usage to personal learning. Using thumbnails reduces bandwidth impact on Pexels and speeds up your workflow.

### API Rate Limits (Quick Overview)

- **Groq (Sentence Generation)**: No daily cap; billed per token. Start with batch=1, scale to 3-5 after testing.
- **Google Gemini (Fallback)**: 1,500 requests/day; stops immediately on quota hit (429 error).
- **Google TTS (Audio)**: 1M characters/month free tier (covers full 625-word deck at ~312k chars).
- **Pexels (Images)**: ~200 requests/hour; batches of 50-100 images recommended with 1-2 hour pauses.

See **API Costs & Rate Limits** section below for detailed safety mechanisms and batch workflow recommendations.

## Why Use This Script?

### The Fluent Forever Method: Smart, Not Hard

The **Fluent Forever method** by Gabriel Wyner is proven to accelerate language acquisition through:
- **Spaced Repetition**: Review cards at optimal intervals for long-term retention
- **Personalized Sentences**: Learn words in context, not isolation
- **Multi-Sensory Learning**: Combine text, audio, and images for stronger memory
- **Frequency-Based Learning**: Start with the most common words (80/20 rule)

### Why Automate Card Creation?

**Without this script:**
- ⏳ Creating 1 card manually: 5-10 minutes (find sentence, record/download audio, find image, format)
- 📚 Creating 625 Fluent Forever words × 10 sentences = **6,250 cards**
- ⏱️ Total manual time: **520-1,040 hours** of tedious copy-paste work
- 😫 Burnout risk: Extremely high—most learners quit before finishing

**With this script:**
- ⚡ Creating 1 card automatically: **45 seconds** (fully automated)
- 📚 6,250 cards = **~52 hours** of mostly unattended runtime
- 🎯 Your time investment: **2-3 hours** (setup + review + import)
- ✅ More time for what matters: **immersion, speaking practice, and actual learning**

### Focus on Real Learning

By automating card creation, you can spend your time on activities that truly matter:

1. **🎧 Immersion**: Watch TV shows, YouTube videos, and movies in your target language
2. **🎙️ Podcasts**: Listen to native speakers while commuting or exercising
3. **📖 Reading**: Consume books, articles, and social media in the target language
4. **💬 Speaking Practice**: Use iTalki, HelloTalk, or language exchange partners
5. **📝 Grammar Study**: Focus on understanding structure, not creating flashcards
6. **🎯 Anki Reviews**: Spend your study time reviewing cards, not making them

**Research shows**: Active immersion and output practice accelerate fluency far more than card creation. This script handles the busywork so you can focus on real language exposure.

## 🌍 Multi-Language Support: 109 Languages Ready to Go!

This tool supports **109 languages** with pre-made frequency word lists. No need to find or format data yourself!

### Supported Languages

**Complete List (109 total):**
Afrikaans, Albanian, Amharic, Arabic, Armenian, Azerbaijani, Basque, Belarusian, Bengali, Bosnian, Bulgarian, Burmese, Catalan, Cebuano, Chichewa, Chinese (Simplified), Chinese (Traditional), Corsican, Croatian, Czech, Danish, Dutch, English, Esperanto, Estonian, Finnish, French, Frisian, Galician, Georgian, German, Greek, Gujarati, Haitian Creole, Hausa, Hawaiian, Hebrew, Hindi, Hmong, Hungarian, Icelandic, Igbo, Indonesian, Irish, Italian, Japanese, Javanese, Kannada, Kazakh, Khmer, Kinyarwanda, Korean, Kurdish, Kyrgyz, Lao, Latin, Latvian, Lithuanian, Luxembourgish, Macedonian, Malagasy, Malay, Malayalam, Maltese, Maori, Marathi, Mongolian, Nepali, Norwegian, Odia, Pashto, Persian, Polish, Portuguese, Punjabi, Romanian, Russian, Samoan, Scots Gaelic, Serbian, Sesotho, Shona, Sindhi, Sinhala, Slovak, Slovenian, Somali, Spanish, Sundanese, Swahili, Swedish, Tagalog, Tajik, Tamil, Tatar, Telugu, Thai, Turkish, Turkmen, Ukrainian, Urdu, Uyghur, Uzbek, Vietnamese, Welsh, Xhosa, Yiddish, Yoruba, Zulu

### Frequency Word Lists Source

All frequency lists come from: **[most-common-words-multilingual](https://github.com/frekwencja/most-common-words-multilingual)**

Credits: Data sourced from publicly available language corpora and frequency analysis.

### How to Use Any Language

The new **language selection system** makes it trivial to switch languages:

#### Step 1: Run Language Selector (First Time Only)

```bash
python 0_select_language.py
```

You'll see:
```
🌍 FLUENT FOREVER - LANGUAGE SELECTION
============================================================

✅ Found 109 languages available

  1. Afrikaans (AF)
  2. Albanian (SQ)
  ...
 71. Malayalam (ML)
 ...
109. Zulu (ZU)

Enter language number (1-109): 71
```

Select your language, and the system will:
- ✅ Load the frequency list automatically
- ✅ Create `language_config.txt` with your language settings
- ✅ Create output folder: `FluentForever_{Language}_Perfect/`

#### Step 2: Generate Cards

```bash
# Generate 10 sentences per word (all use cases)
python 1_generate_sentences.py

# Repeat for all 625 words
python 1_generate_sentences.py
python 1_generate_sentences.py
# ... etc
```

That's it! Everything else works the same.

### Example: Learning Malayalam

Complete walkthrough: See **[MALAYALAM_USE_CASE.md](MALAYALAM_USE_CASE.md)**

### Example: Learning Spanish

```bash
# 1. Select language
python 0_select_language.py
# Choose: 96. Spanish (ES)

# 2. Generate sentences
for i in {1..625}; do python 1_generate_sentences.py; done

# 3. Download audio (Spanish support excellent!)
for i in {1..625}; do python 2_download_audio.py; done

# 4. Download images
for i in {1..625}; do python 3_download_images.py; done

# 5. Create TSV
python 4_create_anki_tsv.py

# 6. Import to Anki (6,250 cards!)
```

### Adapting to Your Language

If your language isn't in the list, you can:

1. Find a frequency list online (Wiktionary has many)
2. Create an Excel file: `{Language} Word` | `Meaning` | `Status`
3. Update `language_config.txt` manually:
   ```
   language_name=Your Language
   language_code=YL
   frequency_file=/path/to/your/file.xlsx
   output_dir=FluentForever_Your_Language_Perfect
   ```
4. Run the scripts normally

## How Sentence Generation Works (10 Sentences = Maximum Benefit)

### Why 10 Sentences Per Word?

**Token Efficiency:** Each API call generates 10 sentences, maximizing the use of your Gemini API tokens.
- Before: 5 sentences per call = 625 words × 1 call = 625 API calls
- Now: 10 sentences per call = 625 words × 0.5 calls ≈ 313 API calls
- **50% fewer API calls, 2x more cards!**

### All Use Cases Covered

Each set of 10 sentences covers:

1. **Grammatical roles**: Subject, object, predicate, indirect object
2. **Tenses/moods**: Present, past, future, conditional, subjunctive
3. **Formality levels**: Formal, informal, colloquial, slang
4. **Real-world contexts**: Daily life, work, school, academic, idioms
5. **Different sentence structures**: Simple, compound, complex

Example for Malayalam word "വീട്" (veet - house):
- Simple: "വീട് വലുതാണ്" (The house is big)
- Possessive: "എന്റെ വീട് പ്രകാശമയമാണ്" (My house is bright)
- Locative: "വീട്ടിൽ ആളുകൾ ഉണ്ട്" (There are people in the house)
- ... and 7 more examples

This ensures you learn **all uses** of each word, not just one basic example!

---

## Quick Start for Other Languages

This tool is now **completely language-agnostic**:

### Quick Start for Other Languages

1. **Update Script 1** (`1_generate_sentences.py`):
   ```python
   # Line ~65: Change the language name and IPA requirement
   prompt = f"""
   You are a {YOUR_LANGUAGE} language expert. Generate 5 example sentences using the word "{word}" ({meaning}).
   Each sentence must:
   - Use the word naturally in {YOUR_LANGUAGE} context
   - Be 5-12 words long
   - Include IPA transliteration for {YOUR_LANGUAGE} pronunciation
   - Have an accurate English translation
   """
   ```

2. **Update Script 2** (`2_download_audio.py`):
   - **Option A**: Keep soundoftext.com (supports 50+ languages)
     ```python
     # Line ~35: Change voice selection
     voice_dropdown = driver.find_element(By.ID, "voice")
     voice_dropdown.send_keys("{LANGUAGE_CODE}")  # e.g., "Spanish", "French", "Japanese"
     ```
   - **Option B**: Use Google TTS or Azure TTS for better quality (requires code changes)

3. **Update Script 3** (`3_download_images.py`):
   - No changes needed! Image search works for any language
   - Optionally adjust search keywords for better results:
     ```python
     # Line ~80: Add language-specific context
     search_query = f"{english_sentence} pure image {YOUR_LANGUAGE} culture"
     ```

4. **Update Excel File**:
   - Rename `Arabic Frequency Word List.xlsx` → `{Language} Frequency Word List.xlsx`
   - Add your target language's most common words (find frequency lists online)
   - Keep same columns: `Word`, `English Meaning`, `Status`

5. **Update Output Folder**:
   ```python
   # In all scripts: Change folder name
   OUTPUT_DIR = "FluentForever_{YOUR_LANGUAGE}_Perfect"
   ```

### Language-Specific Considerations

**For Non-Latin Scripts** (Arabic, Japanese, Chinese, Russian, etc.):
- ✅ Script already handles Unicode correctly
- ✅ IPA transliteration automatically generated by Groq/Gemini
- ✅ Google TTS supports **200+ languages** (primary); fallback: soundoftext.com (~50 languages)

**For Tonal Languages** (Chinese, Vietnamese, Thai):
- ✅ IPA includes tone markers
- ✅ Google TTS produces native-quality audio with proper tone inflection
- ⚠️ Always test first word; audio quality varies by language

**For Languages with Dialects** (Spanish, Arabic, Chinese):
- 🔧 **Groq/Gemini prompting**: Specify dialect in prompt ("Mexican Spanish", "Egyptian Arabic", "Mandarin Chinese")
- 🔧 **Google TTS voice selection**: Supported dialects are auto-detected by language (e.g., `es-ES` for Spain Spanish, `es-MX` for Mexican)
- 💡 Test first word with your desired dialect before full batch

**Google TTS Language Support**:
- Covers **200+ languages and dialects** including all major language families
- Auto-detects dialect/region from language code (e.g., `pt-BR` for Brazilian Portuguese)
- Fallback: If Google TTS doesn't support your language, use `python 2_download_audio_soundoftext.py` (supports ~50 languages)

### Example: Adapting to Spanish

1. Update prompt in Script 1:
   ```python
   prompt = f"You are a Spanish language expert. Generate 5 example sentences using '{word}' ({meaning})..."
   ```
2. Update voice in Script 2: `voice_dropdown.send_keys("Spanish")`
3. Rename Excel: `Spanish Frequency Word List.xlsx`
4. Add Spanish frequency words (e.g., "el", "de", "que", "y", "a"...)
5. Update output folder: `FluentForever_Spanish_Perfect`

**Total adaptation time: 10-15 minutes** ⚡

### Resources for Frequency Lists

- **Free**: Wiktionary frequency lists (most languages)
- **Book**: "Fluent Forever" by Gabriel Wyner (includes 625-word lists for major languages)
- **Paid**: Routledge Frequency Dictionaries (academic-quality lists)
- **Online**: Use Corpus databases (e.g., OPUS for parallel corpora)

## System Requirements

- Python 3.10+
- Internet connection
- **Groq API key** (recommended default for sentence generation)
- **Google Gemini API key** (optional fallback; free tier 1,500 req/day)
- **Google Cloud Text-to-Speech service account JSON** (required for audio generation)
   - ⚠️ Billing must be enabled once; free tier covers the whole deck (~312k chars of 1M free)
   - 💡 **No card?** Use the fallback script: `python 2_download_audio_soundoftext.py` (selenium-based)
- **Pexels API key** (free tier - required for image downloads)
- Google Chrome browser (only if using soundoftext fallback)

## Installation

### 1. Clone the Repository
```bash
git clone https://github.com/agnel18/anki-fluent-forever-language-card-generator.git
cd anki-fluent-forever-language-card-generator
```

> 💡 **Note:** This repo previously shipped Arabic sample outputs. If you want a clean start, remove the old sample files listed below.

### 2. Create Python Virtual Environment
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

### 3. Install Dependencies

**Option A: Using requirements.txt (recommended)**
```bash
pip install -r requirements.txt
```

**Option B: Manual installation**
```bash
pip install google-generativeai google-cloud-texttospeech pandas openpyxl python-dotenv requests

# Only if using soundoftext.com fallback (no credit/debit card):
pip install selenium webdriver-manager
```

### 4. Set Up API Keys

#### 4a. Google Gemini API Key (Required - Sentence Generation)

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikeys)
2. Click "Create API Key"
3. Copy your API key

#### 4b. Google Text-to-Speech API (Required - Audio Generation)

📚 **Official Documentation**: [Google Cloud Text-to-Speech](https://cloud.google.com/text-to-speech?hl=en_GB)

**Step-by-Step Instructions:**

1. **Go to Google Cloud Console**
   - Visit: [https://console.cloud.google.com/](https://console.cloud.google.com/)
   - Sign in with your Google account

2. **Create a New Project** (or select existing)
   - Click the project dropdown at the top
   - Click **"New Project"**
   - Name it (e.g., "Anki Language Learning")
   - Click **"Create"**

3. **Enable Billing** ⚠️ **REQUIRED (even for free tier)**
   - Go to **"Billing"** in the left sidebar
   - Click **"Link a Billing Account"**
   - Add your credit/debit card details
   - ✅ Don't worry: You won't be charged if you stay within free tier limits (see below)

4. **Enable Cloud Text-to-Speech API**
   - Go to **"APIs & Services"** → **"Library"**
   - Search for **"Cloud Text-to-Speech API"**
   - Click on it, then click **"Enable"**

5. **Create Service Account & Download JSON Key**
   - Go to **"APIs & Services"** → **"Credentials"**
   - Click **"Create Credentials"** → **"Service Account"**
   - Enter service account details (e.g., name: "language-learning-tts")
   - Click **"Create and Continue"**
   - Click **"Continue"** on permissions page (optional)
   - Click **"Done"**
   - Click the service account you just created
   - Go to **"Keys"** tab → **"Add Key"** → **"Create new key"**
   - Select **"JSON"** format
   - **JSON key file downloads** → Save it

6. **Add JSON Key to Project Folder**
   - Move the downloaded JSON file to: `LanguagLearning/` folder
   - The code will automatically find it (e.g., `languagelearning-480303-0225aa1c8383.json`)
   - ✅ JSON file is protected in `.gitignore` (never committed to git)

⚠️ **IMPORTANT - Stay Within Free Tier Limits**:
- **Free Tier**: 1 million characters per month
- **Your Usage**: ~312,500 characters for full 625-word deck
- **Stay Safe**: Follow the batch recommendations in "API Costs & Rate Limits" section
- **Monitor**: Check usage at [Google Cloud Console → Billing](https://console.cloud.google.com/billing)

💡 **No credit/debit card?** Use the fallback script:
```bash
python 2_download_audio_soundoftext.py  # Uses soundoftext.com (selenium-based)
```

#### 4c. Pexels API Key (Required - Image Downloads)

1. Go to [Pexels API](https://www.pexels.com/api/)
2. Click "Get Started" and create a free account
3. Copy your API key from the dashboard

#### 4d. Create `.env` File

Create a `.env` file in the workspace root with:
```
# Sentence generation
USE_GROQ=1                     # 1 = use Groq (recommended), empty/0 = use Gemini
GROQ_API_KEY=your_groq_key_here
GOOGLE_API_KEY=your_gemini_api_key_here  # Only used if USE_GROQ is empty/0

# Images
PEXELS_API_KEY=your_pexels_api_key_here

# Audio
AUDIO_SPEED=0.8                # 0.5–2.0 supported; 0.8 is learner-friendly
```
Place your Google Cloud **service account JSON** for Text-to-Speech in `LanguagLearning/`. The scripts auto-detect any `*.json` there; you can also point `GOOGLE_APPLICATION_CREDENTIALS` to the file if you prefer.

### 5. Set Up Anki Template (Beginner-Friendly)

**Option A: Use Pre-Made Template** (Recommended for beginners)

1. Open Anki
2. Click **File** → **Import**
3. Navigate to `LanguagLearning/Anki Language Template/`
4. Select `Language Learning Template.apkg`
5. Click **Open**
6. ✅ Done! You now have the note type and card styling ready for any language

**Option B: Create From Scratch** (Advanced users)

See [ANKI_SETUP.md](ANKI_SETUP.md) for detailed manual setup instructions.

### 6. Prepare Input Excel File

> ⚠️ **Important:** If you want to start fresh or adapt to another language, delete any old sample artifacts (e.g., `FluentForever_Arabic_Perfect/*` outputs) and create/rename your own frequency list.

Create `<Language> Frequency Word List.xlsx` in `LanguagLearning/` folder with columns:
- **Word**: The target-language word
- **English Meaning**: English translation
- **Status**: Leave empty (will be auto-populated)

Example:
| Word | English Meaning | Status |
|------|-----------------|--------|
| hola | hello | |
| casa | house | |
| libro | book | |

## Workflow

The system uses a **5-step pipeline**:

### Quick Start (Current Setup)

- `USE_GROQ=1` (Groq llama-3.3-70b for sentences), `AUDIO_SPEED=0.8`, `.json` service account for TTS placed in `LanguagLearning/`.
- Run in order:
   1) `python 0_select_language.py`
   2) `python 1_generate_sentences.py` (default batch=1; raise with `$env:BATCH_WORDS="3"` after a test word)
   3) `python 2_download_audio.py`
   4) `python 3_download_images.py`
   5) `python 4_create_anki_tsv.py`
- Import `FluentForever_{Language}_Perfect/ANKI_IMPORT.tsv` into Anki, then copy `audio/` and `images/` files into Anki media folder.

### Step 0: Select Your Language (One-Time Setup)

```bash
python 0_select_language.py
```

Choose from **109 languages**. The system will:
- Load the pre-made frequency word list
- Create `language_config.txt` with your language settings
- Create output folder: `FluentForever_{Language}_Perfect/`

**Example:**
```
python 0_select_language.py
→ Select: 71. Malayalam (ML)
→ Output: FluentForever_Malayalam_Perfect/
```

### Script 1: Generate Sentences (`1_generate_sentences.py`)

Generates **10 natural sentences** for each word using **Groq (llama-3.3-70b)** by default (`USE_GROQ=1`). If `USE_GROQ` is empty/0, it falls back to **Google Gemini** (subject to daily quota).

- Reads next word with empty Status
- Generates 10 sentences covering different grammatical contexts, tenses, formality levels
- Saves to `working_data.xlsx` for review
- Updates Status → `sentences_done`

**Safety defaults:** Batch size = 1 word (env `BATCH_WORDS` overridable), max 3 retries with backoff (4s/8s/16s), stops immediately on quota/rate-limit/billing errors.

**Run:**
```bash
python 1_generate_sentences.py
# Increase batch cautiously after testing a word or two:
$env:BATCH_WORDS="3"; python 1_generate_sentences.py
```

### Script 2: Download Audio (`2_download_audio.py`)

Downloads native speaker audio using **Google Cloud Text-to-Speech** with a **service account JSON** placed in `LanguagLearning/` (auto-detected). Fallback: `2_download_audio_soundoftext.py` if you cannot enable billing.

- Finds words with Status=`sentences_done`
- Generates audio at **0.8x speed** (recommended for language learners)
- Saves to `FluentForever_{Language}_Perfect/audio/`
- Updates Sound column with `[sound:filename.mp3]`
- Updates Status → `audio_done`

**Audio Speed Options:**
```bash
# Default (0.8x - slower for learners, recommended):
python 2_download_audio.py

# Custom speed (0.5 = very slow, 1.0 = normal, 2.0 = fast):
$env:AUDIO_SPEED="1.0"; python 2_download_audio.py
```

**Fallback Option (No Credit/Debit Card):**
```bash
# Uses soundoftext.com (selenium-based, slower but free):
python 2_download_audio_soundoftext.py
```

**Run:**
```bash
python 2_download_audio.py
```

### Script 3: Download Images (`3_download_images.py`)
Downloads clean thumbnail images from **Pexels** using the **English translation** of each sentence (better relevance, lower bandwidth).
- Finds words with Status=`audio_done`
- Queries Pexels with the English translation; downloads thumbnail (`tiny`) to save bandwidth
- Saves to `FluentForever_{Language}_Perfect/images/`
- Updates Image column with `<img src="filename.jpg">`
- (Rate limits) Free tier is ~200 requests/hour → run in batches if needed

**Run:**
```bash
python LanguagLearning/3_download_images.py
```

### Script 4: Create Anki TSV (`4_create_anki_tsv.py`)
Exports completed cards to TSV format for Anki import.
- Finds all rows with both Sound and Image populated
- Exports to `ANKI_IMPORT.tsv` (tab-separated values)
- Updates all processed words → Status `complete`
- Ready to import into Anki

**Run:**
```bash
python LanguagLearning/4_create_anki_tsv.py
```

## Data Flow

```
<Language> Frequency Word List.xlsx
           ↓
    Script 1: Sentences
           ↓
    working_data.xlsx (review here!)
           ↓
    Script 2: Audio
           ↓
   FluentForever_{Language}_Perfect/audio/
           ↓
    Script 3: Images
           ↓
   FluentForever_{Language}_Perfect/images/
           ↓
    Script 4: TSV Export
           ↓
    ANKI_IMPORT.tsv
           ↓
    Import into Anki!
```

## Folder Structure

```
LanguagLearning/
├── 0_select_language.py
├── 1_generate_sentences.py
├── 2_download_audio.py                      ⭐ DEFAULT (Google TTS)
├── 2_download_audio_soundoftext.py          💡 FALLBACK (no card required)
├── 3_download_images.py
├── 4_create_anki_tsv.py
├── sync_counts.py                            🔧 UTILITY (sync progress)
├── reset_images.py                           🔧 UTILITY (reset images)
├── README.md
├── ANKI_SETUP.md
├── .env                                      🔒 KEEP SECRET!
├── language_config.txt                       📝 AUTO-GENERATED
├── 109 Languages Frequency Word Lists/
│   ├── Malayalam (ML).xlsx
│   ├── Spanish (ES).xlsx
│   ├── Chinese (ZH).xlsx
│   └── ... (109 total)
├── Anki Language Template/
│   ├── Language Learning Template.apkg      ⭐ PRE-MADE TEMPLATE
│   └── CREATE_TEMPLATE.md
└── FluentForever_{Language}_Perfect/
    ├── working_data.xlsx
    ├── ANKI_IMPORT.tsv
    ├── audio/
    │   ├── 0001_word_01.mp3
    │   ├── 0001_word_02.mp3
    │   └── ... (10 per word)
    └── images/
        ├── 0001_word_01.jpg
        ├── 0001_word_02.jpg
        └── ... (10 per word)
```

## Anki Setup (For Complete Beginners)

### Step 1: Install Anki (if you haven't already)

1. Go to [https://apps.ankiweb.net/](https://apps.ankiweb.net/)
2. Download Anki for your operating system:
   - **Windows**: Click "Download" for Windows
   - **Mac**: Click "Download" for Mac
   - **Linux**: Click "Download" for Linux
3. Run the installer and follow the prompts
4. Open Anki
5. (Optional) Create a free AnkiWeb account to sync cards across devices

### Step 2: Import the Pre-Made Template (Easiest Method!)

This repository includes a ready-to-use Anki template file. **No manual setup required!**

1. In Anki, click **File** → **Import**
2. Navigate to this project folder: `LanguagLearning/Anki Arabic Template/`
3. Select **Language Learning Template.apkg**
4. Click **Open** (or **Import**)
5. ✅ Done! You now have an **Arabic** deck with pre-configured fields and card styling

**What's included in the template:**
- ✅ Note type with 8 fields (File Name, Word, Meaning, Sentence, IPA, Translation, Sound, Image)
- ✅ Front/back card templates optimized for language learning
- ✅ Styling that works for both left-to-right and right-to-left languages (rename the deck after import)

### Step 3: Import Your Generated Cards

After running scripts 1-4, you'll have `ANKI_IMPORT.tsv` ready to import. See the **Usage Example** section below for import instructions.

---

**Advanced Users:** Want to customize the template or create your own from scratch? See [ANKI_SETUP.md](ANKI_SETUP.md) for detailed manual setup instructions

3. **Import TSV**:
   - File → **Import**
   - Select `ANKI_IMPORT.tsv`
   - Choose the note type from the template (preloaded by `Language Learning Template.apkg`)
   - Select your target-language deck
   - Click **Import**

### Import Media Files

After importing TSV, you need to add the audio and image files:

1. In Anki, click **Tools** → **Check Media**
2. Click **View Files** to open the media folder
3. In your file explorer, navigate to `FluentForever_{Language}_Perfect/audio/`
4. Select all MP3 files (Ctrl+A)
5. Copy them (Ctrl+C)
6. Go back to Anki's media folder
7. Paste (Ctrl+V)
8. Repeat for images from `FluentForever_{Language}_Perfect/images/`

⚠️ **Important**: Copy the individual files, NOT the folders!

## Usage Example

```bash
# Activate virtual environment
.\.venv\Scripts\activate

# Generate sentences for word 1
python LanguagLearning/1_generate_sentences.py
# Output: sentences_done status, 5 rows in working_data.xlsx

# Generate sentences for words 2-10 (repeat script 10 times, or create a loop)
python LanguagLearning/1_generate_sentences.py
python LanguagLearning/1_generate_sentences.py
# ... etc

# After all words have sentences, download audio for all
python LanguagLearning/2_download_audio.py
python LanguagLearning/2_download_audio.py
# ... repeat until audio_done for all words

# Then download images for all
python LanguagLearning/3_download_images.py
python LanguagLearning/3_download_images.py
# ... repeat until images_done for all words

# Finally, generate Anki TSV
python LanguagLearning/4_create_anki_tsv.py

# Import ANKI_IMPORT.tsv into Anki following instructions above
```

## Troubleshooting

### "No rows with Status=sentences_done"
- Run script 1 first to generate sentences
- Check your `<Language> Frequency Word List.xlsx` has empty Status column

### Audio download fails (Google TTS)
- **Authentication error**: Verify GOOGLE_APPLICATION_CREDENTIALS environment variable is set
- **Service account error**: Ensure Text-to-Speech API is enabled in Google Cloud Console
- **Credit/debit card required**: Google TTS API requires card on file (even though free)
- **No card? Use fallback**: `python 2_download_audio_soundoftext.py` (selenium-based)
- Check internet connection

### Audio download fails (soundoftext.com fallback)
- Check internet connection
- soundoftext.com may be temporarily down, try again later
- If many requests in a row, wait 1–2 minutes and rerun
- Chrome driver issues: Update Chrome browser or reinstall webdriver-manager

### Image download fails
- Ensure `PEXELS_API_KEY` is set in `.env`
- Check internet connection
- Pexels free tier rate limit is ~200 requests/hour; wait and rerun if you hit it
- Some words may simply have no good results; add manually if needed

### Permission denied on Excel
- Close Excel files before running scripts
- Files are locked while open in Excel

### Media files don't show in Anki
- Ensure file paths in TSV match actual filenames
- Copy individual files to collection.media folder (not folders)
- Run **Tools** → **Check Media** again

## Output Fields

Each Anki card contains:

| Field | Example | Format |
|-------|---------|--------|
| File Name | 0001_word_01 | {freq:04d}_{word}_{sentence:02d} |
| What is the Word? | palabra | Target word |
| Meaning of the Word | word | English translation |
| Sentence | La palabra es útil. | Target-language sentence |
| IPA Transliteration | /paˈlaβɾa/ | IPA pronunciation |
| English Translation | The word is useful. | English translation |
| Sound | [sound:0001_word_01.mp3] | Anki sound tag |
| Image | <img src="0001_word_01.jpg"> | Anki image tag |

## API Costs & Rate Limits

### 🛡️ Built-in Safety Features

**All scripts include protection against:**
- ✅ **Max 3 retry attempts** per item with backoff (4s → 8s → 16s)
- ✅ **Automatic quota/rate/billing detection** - stops immediately when limit hit
- ✅ **Default batch size = 1 word** (env `BATCH_WORDS` to override cautiously)
- ✅ **Clear error messages** - explains what went wrong and how to fix

**You are protected from:**
- ❌ Account bans
- ❌ Unexpected charges
- ❌ Quota exhaustion
- ❌ Rate limit violations

### Groq API (Sentence Generation - Default)
- **Model**: llama-3.3-70b-versatile
- **Quota**: No daily cap; billed per token (see Groq pricing)
- **Safety**: Same retry/backoff; still stops on unexpected errors
- **Recommendation**: Start with batch=1, then 3-5 after verifying quality

### Google Gemini API (Sentence Generation - Fallback)
- **Free Tier**: 15 requests per minute, 1,500 requests per day
- **Safety**: Stops immediately on quota hit (429/insufficient-quota), max 3 retries for transient errors
- **Recommendation**: Keep batch low (1-3) to avoid hitting daily quota

### Google Text-to-Speech API (Audio)
- **Free Tier**: 1 million characters per month
- **Average**: ~50 characters per sentence
- **625 words × 10 sentences = 6,250 sentences × 50 chars = 312,500 characters**
- **Cost**: $0 (well within free tier) when billing is enabled once
- **Safety**: Stops on billing/quota errors; retries with backoff for transient issues
- **Recommendation**: Batch size 1-5 words until confident; monitor console usage if scaling

### Pexels API (Images)
- **Free Tier**: ~200 requests per hour
- **Safety**: Script stops immediately on rate limit (429 error)
- **Recommendation**: Generate 50-100 images per session, pause 1-2 hours
- **625 words × 10 images = 6,250 images**: Spread over multiple sessions

### Optimal Batch Workflow

**Recommended: 5-10 words per day** (sustainable long-term)

| Pace | Duration | Notes |
|------|----------|-------|
| **5 words/day** | ~125 days | Very safe, low quota risk, fits into daily routine |
| **10 words/day** | ~62 days | Moderate pace, easy to scale API costs |
| **25 words/day** | ~25 days | Aggressive; batch=5, monitor Groq/TTS usage |
| **50+ words/day** | <25 days | Expert only; manage Pexels rate limits carefully |

**Example: 5 Words/Day Workflow**

Each day (takes ~10-15 minutes actual work; 45 mins unattended):
```bash
# Morning (2 min)
$env:BATCH_WORDS="5"; python 1_generate_sentences.py

# Mid-day (5 mins unattended)
python 2_download_audio.py

# Afternoon (7 mins unattended, respects Pexels rate limit)
python 3_download_images.py

# Once per 50 words (~10 days):
python 4_create_anki_tsv.py
# Import to Anki!
```

**Scaling Example: 625 Words in ~3 Months**
- Batch 5 words/day × 125 days ≈ 4 months
- Or batch 10 words/day × 62 days ≈ 2 months (faster, still safe)
- Or use 25-50/day on weekends, 5/day on weekdays (balanced)

---

**Legacy: Day-Based Workflow (Reference)**

**Day 1-12**: Generate sentences (50-100 words/day)
```bash
$env:BATCH_WORDS="50"; python 1_generate_sentences.py
```

**Day 13**: Generate all audio (1 session, ~3-4 hours)
```bash
$env:BATCH_WORDS="625"; python 2_download_audio.py
```

**Day 14-19**: Generate all images (6 sessions, 100 words each)
```bash
# Session 1:
$env:BATCH_WORDS="100"; python 3_download_images.py
# Wait 1-2 hours
# Session 2:
$env:BATCH_WORDS="100"; python 3_download_images.py
# ... repeat 6 times total
```

**Total Time**: 19 days, mostly unattended
**Total Cost**: $0

## Tips & Best Practices

### Script Usage

1. **Review working_data.xlsx** before running script 2
   - Check if sentences are appropriate
   - Delete any rows you don't want
   - Status won't update until all 5 are present

2. **Run scripts in order** (1→2→3→4)
   - Each script depends on previous status

3. **Test on small batch first**
   - Try 2-3 words before full workflow

4. **Close Excel files** before running scripts
   - Prevents file lock errors

5. **Check media folder** before importing into Anki
   - Ensure audio/images are present and named correctly

### Learning Strategy

6. **Let the script run in the background**
   - Scripts 2 & 3 can run unattended
   - Use this time for immersion: watch Netflix, listen to podcasts
   - Check progress every 30 minutes

7. **Batch process efficiently**
   - Generate sentences for 50 words (Script 1: ~5 minutes)
   - Run Script 2 for all 50 words (unattended, ~12 minutes)
   - Run Script 3 for all 50 words (unattended, ~17 minutes)
   - Import to Anki and START LEARNING

8. **Prioritize review over creation**
   - 30 minutes of Anki reviews > 30 minutes of card creation
   - This script automates creation so you can focus on actual learning

9. **Use Anki mobile app**
   - Review cards during commute, waiting in line, etc.
   - Audio works on mobile (great for pronunciation practice)

10. **Combine with immersion**
    - After learning 100 words: start watching kids' shows
    - After 300 words: try podcasts for learners
    - After 625 words: dive into native content (news, TV, books)

## Performance

**Per Word Timing:**
- Script 0 (Select Language): One-time setup, ~30 seconds
- Script 1 (Generate 10 Sentences): ~10 seconds per word (token-optimized batch calls)
- Script 2 (Download 10 Audio Files): ~25 seconds per word
- Script 3 (Download 10 Images): ~35 seconds per word
- Script 4 (Create TSV): ~2 seconds total

**Total per word: ~70 seconds**

**Total for 625 words (Fluent Forever deck):**
- Time investment: ~7 hours of *unattended* runtime
- Your actual work: ~30 minutes setup + review
- Output: 6,250 professional Anki cards (10x more than before!)

**API Costs:**
- Google Gemini: FREE (generous rate limits)
- Audio download: FREE
- Image download: FREE
- **Total project cost: $0**

## Credits

This project is inspired by and based on the **Fluent Forever method** created by **Gabriel Wyner**.

- 📖 **Book:** [Fluent Forever: How to Learn Any Language Fast and Never Forget It](https://www.amazon.com/Fluent-Forever-Learn-Language-Forget/dp/0385348118)
- 🌐 **Website:** [fluent-forever.com](https://fluent-forever.com/)
- 👤 **Author:** Gabriel Wyner

This tool automates the card creation process described in the Fluent Forever book, making the method accessible to everyone for free.

## License

MIT License - Feel free to use and modify for personal use

**Note:** This is an independent open-source project and is not officially affiliated with Fluent Forever or Gabriel Wyner. Please support the original work by purchasing the book.

## Contributing

Improvements welcome! Feel free to:
- **Share your language adaptations** (Spanish, French, Japanese, etc.)
- Create language-specific prompt templates for better sentence quality
- Add alternative TTS providers (Google TTS, Azure, ElevenLabs)
- Optimize Selenium automation for faster processing
- Improve image quality selection algorithms
- Build a GUI for non-technical users
- Create pre-made .apkg template files for different languages

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review script comments for debugging
3. Check that all dependencies are installed
4. Verify API key is set correctly in .env

---

**Happy Learning! 🚀**
