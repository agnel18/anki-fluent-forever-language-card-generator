# 🌍 Fluent Forever Anki Language Card Generator

**Professional language learning cards in minutes, not months.**

Generate complete Anki decks with AI-powered sentences, native audio, beautiful images, and word meanings—**for 109 languages**. Built with Groq AI, Edge TTS, Pixabay, and SQLite.

Based on the **[Fluent Forever method](https://fluent-forever.com/)** by Gabriel Wyner—a proven system using spaced repetition, personalized sentences, and multi-sensory learning.

---

## 🚀 Quick Start (2 Minutes)

### 1. Install Dependencies

```bash
cd LanguagLearning
pip install -r requirements.txt
```

### 2. Get API Keys (Free)

1. **Groq API** (AI sentences): https://console.groq.com/keys
2. **Pixabay API** (images): https://pixabay.com/api/docs/
3. **Edge TTS** (audio): Free built-in, no key needed

### 3. Start the App

```bash
streamlit run streamlit_app/app_v3.py
```

Opens at `http://localhost:8501`

### 4. Generate Decks

1. Enter your API keys in the app
2. Pick a language
3. Select 1–10 words (start with 1 to test)
4. Choose audio speed & pitch
5. Hit "Generate" and download your `.apkg`
6. Import into Anki ✅

---

## ✨ Key Features

- **109 Languages** with frequency word lists
- **AI Sentences** via Groq — contextual, natural examples
- **Native Audio** via Edge TTS — 200+ voices, adjustable speed & pitch
- **Beautiful Images** via Pixabay — auto-matched to words
- **3 Card Types** per word — Listening, Production, Reading
- **Rate Limit Monitor** — warnings for safe batch sizes
- **Progress Tracking** — SQLite-based word completion
- **Clean GUI** — no coding required, intuitive flow
- **.apkg Export** — direct Anki format, ready to import

---

## 📋 Project Structure

```
LanguagLearning/
├── streamlit_app/
│   ├── app_v3.py              # Main Streamlit GUI ← USE THIS
│   ├── core_functions.py      # Generation: sentences, audio, images, .apkg
│   ├── frequency_utils.py     # Frequency lists & word selection
│   ├── db_manager.py          # SQLite progress tracking
│   ├── firebase_manager.py    # Firebase sync (optional)
│   ├── languages.yaml         # 109 language configuration
│   ├── requirements.txt       # App dependencies
│   └── README.md              # App-specific documentation
│
├── 109 Languages Frequency Word Lists/  # Frequency word data
├── Anki Language Template/    # Template Anki deck
├── ANKI_SETUP.md             # How to import .apkg into Anki
├── FIREBASE_SETUP.md         # Optional cloud progress sync
├── requirements.txt          # Main project dependencies
├── .env                      # Your API keys (DO NOT commit)
└── README.md                 # This file
```

---

## 🚀 Quick Setup (3 Steps)

### 1. Install Python Dependencies

```bash
pip install -r streamlit_app/requirements.txt
```

### 2. Get Free API Keys

- **Groq** (AI sentences): https://console.groq.com/keys
- **Pixabay** (images): https://pixabay.com/api/docs/
- **Edge TTS** (audio): Built-in, no key needed

### 3. Start the App

```bash
streamlit run streamlit_app/app_v3.py
```

Then follow the in-app steps to generate your first deck.

---

## 🎯 How to Generate a Deck

### First Time: Test with 1 Word

1. **API Setup**: Enter Groq + Pixabay keys
2. **Language**: Pick Spanish (or any language)
3. **Words**: Select 1 word (e.g., "hola")
4. **Audio**: Keep defaults (0.8x speed, 0% pitch)
5. **Generate**: Hit the button and watch progress
6. **Download**: Get your `.apkg` file
7. **Import**: Double-click the file in Anki ✅

### Next Time: Batch Generation

1. **Words**: Pick 5–10 words per batch
2. **Run multiple batches** if you need more words
3. This respects API rate limits and completes faster

---

## ⚙️ Settings Explained

### Global Settings (⚙️ gear icon)

- **Difficulty**: Beginner (short, simple) → Advanced (complex sentences)
- **Sentence Length**: How many words per sentence (default: 6–16)
- **Sentences Per Word**: How many example sentences (default: 10)
- **Audio Speed**: 0.5x (very slow) → 1.5x (fast) [0.8x recommended for learners]
- **Track Progress**: Save completed words to database

### Audio Settings (Step 3)

- **Speed**: Adjust playback speed (learners prefer 0.7x–0.9x)
- **Pitch**: Adjust voice tone (-20% to +20%)
- **Voice**: Auto-selected by language (200+ voices available)

---

## 📊 Rate Limits & Best Practices

### Groq API Limits
- **Free tier**: 30 requests/minute, ~4 million tokens/day
- **Safe batch size**: 5–10 words per generation
- **Why**: 1 word × 10 sentences = 10 API calls

### Pixabay API Limits
- **Free tier**: 5,000 images/day
- **Safe batch size**: Keep under 50 words/day
- **Tip**: Generate in morning, use multiple batches throughout day

### Audio (Edge TTS)
- No rate limits — unlimited free usage
- Only limited by generation time (takes 5–10 seconds per word)

### Best Workflow
1. Generate 5–10 words in morning
2. Import to Anki, review for 30 mins
3. Generate next batch in afternoon
4. Scale up if studying actively

---

## 📥 Importing into Anki

See **[ANKI_SETUP.md](./ANKI_SETUP.md)** for:
- Step-by-step import instructions
- Recommended deck settings
- Spaced repetition best practices
- Tips for studying effectively

---

## ☁️ Optional: Cloud Sync (Firebase)

To sync your progress across devices:

See **[FIREBASE_SETUP.md](./FIREBASE_SETUP.md)** for:
- Firebase project setup
- Enabling cloud progress sync
- Multi-device study coordination

---

## 🛠️ Troubleshooting

### "Invalid API key"
- ✅ Check for typos or extra spaces
- ✅ Verify key works on provider website (Groq, Pixabay)
- ✅ Regenerate key if needed

### "Port already in use (8501)"
```bash
# Kill existing process
taskkill /IM python.exe /F  # Windows
pkill -f streamlit          # macOS/Linux

# Restart app
streamlit run streamlit_app/app_v3.py
```

### ".apkg file not created"
- ✅ Verify Pixabay API key (images required)
- ✅ Check temp folder write permissions
- ✅ Try a smaller batch (1–3 words)

### Audio sounds strange
- ✅ Adjust pitch/speed in Step 3
- ✅ Try a different voice (app shows available voices)
- ✅ Check Edge TTS availability in your region

### Generation times out
- ✅ Reduce batch size (try 3 words instead of 10)
- ✅ Check internet connection
- ✅ Verify API keys are valid

---

## 🔒 Privacy & Security

- **No data stored on servers** — all processing local
- **API keys stay in your browser** — never sent to our servers
- **Anki files on your computer** — full control
- **Optional Firebase** — only if you enable it explicitly
- **.env file** — Add to `.gitignore` before committing

---

## 📦 What's Included

### Word Lists (109 Languages)
- Pre-compiled frequency word lists
- Ranked by usage in real speech
- Covers ~80% of everyday vocabulary in top 1,000 words

### Anki Template
- Professional card template with 3 types
- Dark/light mode support
- Responsive layout for desktop & mobile

### Documentation
- `ANKI_SETUP.md` — Anki import & study guide
- `FIREBASE_SETUP.md` — Cloud sync setup
- `streamlit_app/README.md` — App-specific features

---

## 🚀 What's New (v3 - Dec 2024)

✨ **Major Improvements**:
- Unified GUI (all steps in one flow)
- Pitch control for audio tone adjustment
- Rate limit monitor with warnings
- Clean, specific progress messages
- Reliable auto-scroll to top
- Simplified deck names (just language)

🐛 **Fixes**:
- Fixed Edge TTS pitch invalid format
- Fixed .apkg FileNotFoundError
- Fixed duplicate progress log messages
- Fixed float/NaN field errors in Anki

---

## 📞 Questions or Issues?

1. **Check the docs**:
   - `streamlit_app/README.md` — App features
   - `ANKI_SETUP.md` — Anki import help
   - `FIREBASE_SETUP.md` — Cloud sync

2. **Review the code**:
   - `streamlit_app/app_v3.py` — Main GUI logic
   - `streamlit_app/core_functions.py` — Generation pipeline
   - `streamlit_app/frequency_utils.py` — Word selection & search

3. **Test with 1 word** — Verify all keys work before bulk generation

---

## 🙏 Credits

Built with love using:
- **[Fluent Forever](https://fluent-forever.com/)** methodology by Gabriel Wyner
- **[Groq](https://groq.com/)** — Fast AI inference (llama-3.3-70b)
- **[Edge TTS](https://github.com/rany2/edge-tts)** — Microsoft neural voices
- **[Pixabay](https://pixabay.com/)** — Free high-quality images
- **[Genanki](https://github.com/kerrickstaley/genanki)** — Anki deck creation
- **[Streamlit](https://streamlit.io/)** — Beautiful web GUI framework

---

## 📄 License

MIT License — Free to use, modify, and distribute.

---

**Happy learning! 🌍✨**

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
