# 🌍 Fluent Forever Anki Language Card Generator

**Professional language learning cards in minutes, not months.**

Generate complete Anki decks with AI-powered sentences, native audio, beautiful images, and word meanings—**for 109 languages**. Built with ⚡ **SQLite performance** and a **no-code GUI** for anyone to use.

Based on the **[Fluent Forever method](https://fluent-forever.com/)** by Gabriel Wyner—a proven system using spaced repetition, personalized sentences, and multi-sensory learning.

---

## 🚀 Quick Start (5 Minutes)

### Option 1: GUI (Recommended for Everyone)

**No coding needed!** Just open the app and click.

```bash
cd LanguagLearning
streamlit run streamlit_app/app_v3.py
```

**Then:**
1. Select language
2. Choose batch size
3. Pick words
4. Generate deck
5. Import to Anki ✅

### Option 2: Command Line (Advanced Users)

For advanced control over scripts:

```bash
# Generate sentences
python 1_generate_sentences.py --language Spanish --words 50

# Download audio
python 2_download_audio.py

# Download images
python 3_download_images.py

# Create Anki deck
python 4_create_anki_tsv.py
```

See [Command Line Guide](#command-line-guide) below for details.

---

## ✨ Key Features

### 🎯 **Intelligent & Fast**
- ⚡ **SQLite Database**: 20-200x faster than Excel files
- 📄 **Paginated UI**: Browse 1000+ words smoothly (25 words/page with frequency ranks)
- 🔍 **Instant Search**: Find words in <5ms
- 💾 **Persistent Progress**: Resume where you left off
- 📤 **Custom Word Import**: Upload your own CSV/XLSX word lists

### 🤖 **AI-Powered Content**
- **Groq llama-3.3-70b**: Generates 10 natural sentences per word
- **Smart Context**: Different tenses, formality levels, real-world usage
- **Word Meanings**: Auto-generated definitions with explanations
- 📚 Example: "el" → "the (definite article, used to refer to a specific noun)"
- **IPA Phonetic Transcriptions**: Hybrid AI + epitran fallback for 20+ languages
- **Keyword Extraction**: AI extracts image search keywords from sentences for better image relevance

### 🔊 **Professional Audio**
- **Edge TTS**: High-quality native speaker audio (primary)
- **Google Cloud TTS**: Automatic fallback if Edge TTS fails
- **User Controls**: Adjust speed (0.5x - 1.5x) and select voice (male/female)
- **Result**: 15-24 KB MP3 files per sentence

### 🖼️ **Beautiful Images**
- **Pixabay API**: 50M+ professional photos
- **Smart Search**: Uses extracted keywords for better relevance (improved from full sentences)
- **Top-3 Selection**: Only best images selected
- **Fast Delivery**: 47-135 KB JPGs per image

### 📊 **Complete Tracking & Detailed Progress**
- ✅ Persistent progress (survives app restarts)
- 📈 Statistics: Words learned, completion %, generation history
- ☁️ Optional Firebase cloud sync (multi-session)
- 🎯 Track which words you've completed
- **Real-time Progress Messages**: See exactly what's happening (word-by-word updates)
- **Auto-scroll to Generation**: Jump to top when generation starts

### 🎴 **Professional Anki Cards**
- **3 Card Types Per Word**: Listening (audio recognition), Production (English to target), Reading (comprehension)
- **.apkg Export**: Direct Anki format (no ZIP extraction needed)
- **Dark/Light Mode Support**: Cards auto-adapt to Anki's theme using CSS variables
- **Embedded Media**: Audio and images packaged in single file
- **9 Fields**: Word, Meaning, Sentence, IPA, English, Audio, Image, Keywords, Tags

### 🌍 **109 Languages**
All with frequency-sorted word lists:

**European:** Spanish, French, German, Italian, Portuguese, Russian, Polish, Dutch, Greek, Swedish, Norwegian, Danish, Finnish, Czech, Hungarian, Romanian, Bulgarian, Croatian, Serbian, Ukrainian, Lithuanian, Latvian, Estonian, Albanian, Macedonian, Icelandic, Irish, Welsh, Basque, Catalan, Galician

**Asian:** Mandarin Chinese, Cantonese, Japanese, Korean, Hindi, Bengali, Tamil, Telugu, Kannada, Malayalam, Marathi, Gujarati, Punjabi, Urdu, Thai, Vietnamese, Indonesian, Tagalog, Malay, Burmese, Khmer, Lao, Sinhala, Nepali, Azerbaijani, Kazakh, Kyrgyz, Tajik, Uzbek, Turkmen, Mongolian, Armenian, Georgian, Hebrew, Arabic, Persian, Pashto, Kurdish, Turkish

**African:** Swahili, Yoruba, Igbo, Hausa, Amharic, Somali, Shona, Zulu, Xhosa, Sesotho, Malagasy, Kinyarwanda

**Other:** English, Latin, Esperanto, Yiddish, and more...

---

## 📋 How It Works

### Architecture

```
┌─────────────────────────────────────────┐
│      🎨 Streamlit GUI (app_v3.py)       │
│   Beautiful, intuitive, no code needed  │
└──────────────────┬──────────────────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
    ⚡ SQLite DB         🤖 Groq API
    (word lists)      (sentences, meanings)
        │                     │
        └──────────┬──────────┘
                   │
        ┌──────────┴──────────┐
        │                     │
    🔊 Edge TTS           🖼️ Pixabay
   (primary audio)      (beautiful images)
        │                     │
        └─────────┬───────────┘
                  │
           📝 Anki TSV
         (ready to import)
```

### Workflow

```
SELECT LANGUAGE
    ↓
CHOOSE BATCH SIZE (5-50 words)
    ↓
SELECT WORDS (paginated with frequency ranks, searchable, or upload custom CSV/XLSX)
    ↓
CONFIGURE SETTINGS
    ├─ Difficulty: Beginner/Intermediate/Advanced
    ├─ Sentence Length: 4-30 words per sentence
    ├─ Sentences Per Word: 3-15 examples
    ├─ Audio Speed: 0.5x - 1.5x
    └─ Voice: Male/Female per language
    ↓
GENERATE DECK (automatic with detailed progress)
    ├─ Step 1: Generate sentences with AI (Groq)
    ├─ Step 2: Generate audio for each sentence (Edge TTS)
    ├─ Step 3: Download images using keyword extraction (Pixabay)
    ├─ Step 4: Add IPA phonetic transcriptions (AI + epitran fallback)
    └─ Step 5: Create .apkg Anki deck with 3 card types
    ↓
DOWNLOAD & IMPORT
    ├─ Download .apkg file directly (no extraction needed!)
    ├─ Double-click to open in Anki
    ├─ Anki imports automatically ✅
    └─ 3 card types per word ready to study
```

---

## 🛠️ Setup (2 Steps)

### Step 1: Install Dependencies

```bash
cd LanguagLearning

# Create virtual environment
python -m venv .venv

# Activate it
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install packages
pip install -r streamlit_app/requirements.txt
```

### Step 2: Add API Keys

Create a `.env` file in `LanguagLearning/` folder:

```env
# Required: Groq (free tier, no credit card)
GROQ_API_KEY=gsk_your_key_here

# Required: Pixabay (free tier, 5000 images/day)
PIXABAY_API_KEY=your_pixabay_key_here

# Optional: Google Cloud TTS (fallback audio)
# Setup: GOOGLE_TTS_SETUP.md
GOOGLE_APPLICATION_CREDENTIALS=./languagelearning-480303-93748916f7bd.json

# Optional: Firebase (cloud progress sync)
# Setup: FIREBASE_SETUP.md
FIREBASE_CONFIG=./firebase_config.json
```

**Get free API keys:**
- **Groq**: https://console.groq.com/keys (free, instant)
- **Pixabay**: https://pixabay.com/api/docs/ (free tier, 5000/day)
- **Google TTS**: [GOOGLE_TTS_SETUP.md](./GOOGLE_TTS_SETUP.md) (optional fallback)
- **Firebase**: [FIREBASE_SETUP.md](./FIREBASE_SETUP.md) (optional cloud sync)

---

## 📱 Using the App

### Launch Streamlit GUI

```bash
streamlit run streamlit_app/app_v3.py
```

Visit: **http://localhost:8507**

### Step-by-Step

**Page 1: API Setup**
- Enter Groq API key
- Enter Pixabay API key
- Optional: Setup Google TTS or Firebase
- Click "Let's Go!"

**Page 2: Main App**
- **Step 1:** Select language (109 options)
- **Step 2:** Choose batch size (5-50 words)
- **Step 3:** Select words
  - Browse by page with **frequency ranks** (Top 1-25, Top 25-50, etc.)
  - **Custom word import**: Upload CSV/XLSX with your own words
  - Search for specific words (🔍)
  - Mark completed words (✓)
  - Each word shows its frequency rank
- **Step 4:** Configure audio
  - Speed slider (0.5x - 1.5x)
  - Voice selector (male/female)
- **Settings Icon (⚙️):** Adjust difficulty, sentence length, tracking
- **Step 5:** Generate Deck
  - **Watch detailed progress in real-time**:
    - Step 1/5: Generating sentences (AI batch processing)
    - Step 2/5: Generating audio (word-by-word progress)
    - Step 3/5: Downloading images (keyword-based search)
    - Step 4/5: Adding IPA phonetic transcriptions
    - Step 5/5: Creating .apkg package with 3 card types
  - **Page auto-scrolls to top** when generation starts
  - Download .apkg file when complete

**Page 3: Complete**
- Download button for .apkg file (ready to import directly!)
- Import instructions for Anki
- **3 Card Types Included:**
  1. 🎧 **Listening**: Audio plays → You guess meaning/translation
  2. 💬 **Production**: English phrase → You produce target language sentence
  3. 📖 **Reading**: Target language sentence → You understand meaning
  - All with IPA, keywords, and images automatically included

---

## 🔧 Command Line Guide

### For Advanced Users

**Why?** Power users who want direct control over the Python scripts for batch processing, custom parameters, or integration with other tools.

#### Individual Scripts

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

---

## 📖 Documentation

- **[GOOGLE_TTS_SETUP.md](./GOOGLE_TTS_SETUP.md)** - Setup Google Cloud TTS fallback
- **[FIREBASE_SETUP.md](./FIREBASE_SETUP.md)** - Setup Firebase for cloud sync
- **[SETTINGS_FEATURE.md](./SETTINGS_FEATURE.md)** - Detailed settings guide
- **[WORD_MEANINGS_AND_IMAGES.md](./WORD_MEANINGS_AND_IMAGES.md)** - Meanings & image selection

---

## 🤝 Contributing

Contributions welcome! Areas for improvement:
- [ ] Additional language support
- [ ] More TTS voices
- [ ] User authentication
- [ ] Deck sharing platform
- [ ] Mobile app
- [ ] Browser extension

---

## 📄 License

MIT License - See [LICENSE](./LICENSE)

---

## 🙏 Credits

- **Fluent Forever Method**: Gabriel Wyner
- **Frequency Lists**: [most-common-words-multilingual](https://github.com/frekwencja/most-common-words-multilingual)
- **Groq API**: Fast, accurate sentence generation
- **Edge TTS**: Native speaker audio
- **Pixabay**: Beautiful, professional images
- **Streamlit**: Beautiful, intuitive GUI
- **SQLite**: Fast, reliable local database
- **Firebase**: Optional cloud sync

---

## 📞 Questions?

- 🐛 **Bug reports**: GitHub Issues
- 💬 **Discussions**: GitHub Discussions
- 📧 **Email**: See GitHub profile

---

## 🎉 Enjoy!

Start learning today. The hardest part is choosing a language—we handle the rest! ✨

```
🚀 Open Streamlit → Select Language → Click Generate → 
   Download ZIP → Import to Anki → Review Cards → Learn Faster!
```

**Happy learning! 🌍📚🎵**
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
