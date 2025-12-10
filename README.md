# 🌍 Fluent Forever Anki Language Card Generator

**Generate professional language learning Anki decks in minutes.**

Create complete decks with AI-written sentences, native audio, beautiful images, and phonetic transcriptions—**for 109 languages**. Built with Groq, Edge TTS, Pixabay, and genanki.

Based on the **[Fluent Forever method](https://fluent-forever.com/)** by Gabriel Wyner—a proven system using spaced repetition, personalized context, and multi-sensory learning.

---

## ⚡ Quick Start

### 1. Install
```bash
cd LanguagLearning
pip install -r requirements.txt
```

### 2. Get Free API Keys
- **Groq** (AI sentences): https://console.groq.com/keys
- **Pixabay** (images): https://pixabay.com/api/docs/

### 3. Run
```bash
streamlit run streamlit_app/app_v3.py
```

### 4. Generate Your First Deck
1. Paste your API keys
2. Pick a language
3. Select 1+ words
4. Hit "Generate"
5. Download & import to Anki ✅

---

## ✨ Features
- **109 Languages** — frequency-sorted word lists
- **AI Sentences** — Groq generates 10 contextual examples per word
- **Native Audio** — Edge TTS (200+ voices, adjustable speed)
- **Smart Images** — Pixabay auto-matched via keyword extraction
- **3 Card Types** — Listening, Production, Reading (Fluent Forever format)
- **Progress Tracking** — SQLite database saves your progress
- **Zero Coding** — GUI handles everything
- **Direct Anki Import** — `.apkg` files ready to use

---

## 📋 Project Structure

```
LanguagLearning/
├── streamlit_app/              # Main application
│   ├── app_v3.py              # ← START HERE (GUI entry point)
│   ├── core_functions.py      # Generation pipeline
│   ├── frequency_utils.py     # Word lists & search
│   ├── db_manager.py          # Progress tracking (SQLite)
│   ├── languages.yaml         # 109 languages config
│   ├── edge_tts_voices.py     # Voice options for Edge TTS
│   ├── firebase_manager.py    # (Optional) Firebase integration
│   └── ...
├── 109 Languages Frequency Word Lists/  # Word lists (Excel)
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

---

## 📝 How It Works
1. **Select a language and words** from the frequency list.
2. **Configure settings**: difficulty, sentence length, audio speed, voice, etc.
3. **Generate deck**: AI creates sentences, audio, images, and IPA.
4. **Download the .apkg** and import into Anki.

---

## 🛠️ Development & Contribution
- Main app: `streamlit_app/app_v3.py`
- Add voices: `streamlit_app/edge_tts_voices.py`
- Add languages: `streamlit_app/languages.yaml`
- Word lists: `109 Languages Frequency Word Lists/`

---

## 📄 License
MIT License. Not affiliated with Fluent Forever or Anki.

---

## 🙏 Credits
- [Fluent Forever](https://fluent-forever.com/)
- [Groq](https://groq.com/)
- [Pixabay](https://pixabay.com/)
- [Edge TTS](https://github.com/rany2/edge-tts)
- [genanki](https://github.com/kerrickstaley/genanki)
│   ├── requirements.txt       # Dependencies
│   └── README.md              # App-specific docs
│
├── 109 Languages Frequency Word Lists/  # Pre-built word data
├── Anki Language Template/    # Template for reference
├── ANKI_SETUP.md             # How to import .apkg files
├── FIREBASE_SETUP.md         # Optional cloud sync
├── requirements.txt          # Python packages
├── .env                      # API keys (local only, not committed)
└── README.md                 # This file
```

---

## 🎯 How to Use

### First Time: Test with 1 Word
1. **API Keys**: Paste Groq + Pixabay keys (appears on start)
2. **Language**: Pick one (e.g., Spanish)
3. **Words**: Select 1 word from the list
4. **Settings**: Keep defaults (0.8x speed)
5. **Generate**: Watch progress, download `.apkg`
6. **Import**: Double-click in Anki (will auto-import)

⏱️ **Takes ~2 minutes for 1 word**

### Scale Up: Batch Generation
- Start small (1–5 words) to test your setup
- Increase to 5–10 words per batch (respects rate limits)
- Generate multiple batches throughout the day
- Import all batches to the same Anki deck

⏱️ **Takes ~3–5 minutes for 10 words**

---

## ⚙️ Settings Reference

### Main Settings (All Steps)
- **Difficulty**: Beginner (simple) → Advanced (complex sentences)
- **Sentence Length**: 4–30 words per sentence (default: 6–16)
- **Sentences Per Word**: How many examples (default: 10)
- **Track Progress**: Save completed words to SQLite

### Audio Settings (Step 3)
- **Speed**: 0.5x (very slow) → 1.5x (fast) — *0.8x recommended for learners*
- **Voice**: Auto-detected by language (200+ available)

---

## 📊 API Limits & Best Practices

### Groq (Sentence Generation)
- **Limit**: 30 requests/minute, ~4M tokens/day (free tier)
- **Safe Batch**: 5–10 words (10 sentences per word = 10 API calls)
- **Pro Tip**: Generate in morning, study for 30 min, generate next batch afternoon

### Pixabay (Images)
- **Limit**: 5,000 images/day (free tier)
- **Safe Batch**: Keep under 50 words/day
- **Note**: 3 images per word = uses API quickly on large batches

### Edge TTS (Audio)
- **Limit**: Unlimited (free, no rate limits)
- **Speed**: ~5–10 seconds per word (parallel processing)
- **Note**: Fully local, no keys needed

### Recommended Workflow
```
Morning (9 AM):   Generate 10 Spanish words (2 min)
                  ↓ Study for 30 min with Anki
Afternoon (3 PM): Generate 10 French words (2 min)
                  ↓ Study for 30 min with Anki
Evening (8 PM):   Generate 10 Mandarin words (2 min)
                  ↓ Study before bed
```

**Result**: 30 new cards/day × 365 days = **11,000 cards/year** 🚀

---

## 📥 Importing into Anki

**Easiest way**: Double-click the `.apkg` file
- Anki opens automatically
- All cards, audio, and images import
- Settings pre-configured (3 card types per word)

**See also**: [ANKI_SETUP.md](./ANKI_SETUP.md) for detailed import help

---

## ☁️ Optional: Cloud Sync (Firebase)

Sync your progress across devices (laptop, phone, tablet):

**See**: [FIREBASE_SETUP.md](./FIREBASE_SETUP.md) for step-by-step setup

*This is optional. Local SQLite progress works great on one device.*

---

## 🛠️ Troubleshooting

### "Invalid API key"
- ✅ Check for typos (extra spaces, wrong key)
- ✅ Verify on provider website (https://console.groq.com/keys)
- ✅ Generate a new key if needed

### "Port already in use (8501)"
```powershell
# Kill existing Python process
taskkill /IM python.exe /F

# Restart the app
streamlit run streamlit_app/app_v3.py
```

### ".apkg file not created"
- ✅ Check Pixabay API key (images required)
- ✅ Verify folder write permissions
- ✅ Try with fewer words (1–3 to test)

### Audio sounds strange
- ✅ Try different voice (many available)
- ✅ Adjust speed (0.7x–0.9x for learners)

### Generation takes forever
- ✅ Reduce batch size (try 3 words instead of 10)
- ✅ Check internet connection
- ✅ Verify API keys are working

---

## 🔒 Privacy & Security

- ✅ **All local**: No data sent to our servers
- ✅ **Your keys only**: Stored in `.env` (never committed)
- ✅ **Anki files yours**: Full control of `.apkg` files
- ✅ **Optional Firebase**: Only if you explicitly enable it
- ✅ **.env in .gitignore**: Never shared

---

## 📦 What's Included

### Word Lists (109 Languages)
Pre-compiled frequency word lists ranked by usage:
- Top 1,000 words cover ~80% of everyday speech
- Supported languages: Spanish, French, German, Mandarin, Arabic, Hindi, Japanese, Korean, and 101 more

### Anki Template
Professional card design with:
- Dark/light mode support
- 3 card types (Listening, Production, Reading)
- Audio playback with controls
- Image display with captions
- Phonetic transcriptions

### Documentation
- [ANKI_SETUP.md](./ANKI_SETUP.md) — Import & study tips
- [FIREBASE_SETUP.md](./FIREBASE_SETUP.md) — Cloud sync (optional)
- [streamlit_app/README.md](./streamlit_app/README.md) — App internals

---

## 🚀 What's New (v3 - Dec 2024)

✨ **Major Changes**:
- Unified GUI (all steps in one app)
- Rate limit warnings
- Combined word selection (Steps 2&3)
- Real-time progress logging
- Auto-scroll between pages

🐛 **Fixes**:
- Fixed .apkg FileNotFoundError
- Fixed duplicate progress messages
- Fixed scroll positioning

---

## 💻 System Requirements

- **Python**: 3.8 or later
- **OS**: Windows, macOS, Linux
- **Disk**: ~500 MB for dependencies
- **RAM**: 2 GB minimum
- **Internet**: Required for API calls (Groq, Pixabay)

---

## 📊 Performance

| Task | Time | Speed |
|------|------|-------|
| 1 word | 2 min | Sentences (15s) + Audio (15s) + Images (15s) + .apkg (5s) |
| 10 words | 3–5 min | Parallel audio processing saves time |
| 50 words | 15–20 min | Multiple batches recommended |

---

## 📞 Need Help?

1. **Quick answers**: Check [Troubleshooting](#-troubleshooting) above
2. **Anki import issues**: See [ANKI_SETUP.md](./ANKI_SETUP.md)
3. **Cloud sync**: See [FIREBASE_SETUP.md](./FIREBASE_SETUP.md)
4. **App features**: See [streamlit_app/README.md](./streamlit_app/README.md)

---

## 📄 License

MIT License — Free to use, modify, and distribute

---

## 🙏 Built With

- **[Groq](https://groq.com/)** — llama-3.3-70b (fast inference)
- **[Edge TTS](https://github.com/rany2/edge-tts)** — Microsoft neural voices
- **[Pixabay](https://pixabay.com/)** — 50M+ free images
- **[genanki](https://github.com/kerrickstaley/genanki)** — Anki deck creation
- **[Streamlit](https://streamlit.io/)** — Web UI framework
- **[epitran](https://github.com/dmort27/epitran)** — IPA transcription

---

## 🎓 The Fluent Forever Method

This app implements Gabriel Wyner's proven language learning system:

1. **Spaced Repetition** — Anki shows cards when you're about to forget
2. **Personalized Context** — Sentences use words YOU want to learn
3. **Multi-Sensory** — Audio (listening), images (visual), text (reading)
4. **Frequency-Based** — Learn common words first (80/20 rule)
5. **Phonetic Awareness** — IPA helps pronunciation

**Result**: Faster, more natural language acquisition 🌍

---

**Ready to start?** 
```bash
streamlit run streamlit_app/app_v3.py
```

**Happy learning!** ✨
