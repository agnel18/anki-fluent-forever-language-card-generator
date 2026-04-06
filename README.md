# 🌍 Language Anki Deck Generator

**Generate professional language learning Anki decks in minutes — completely free.**

Create complete decks with AI-written sentences, native audio, images, and phonetic transcriptions for **77 languages**. Built with Google Gemini AI, Google Cloud TTS, Pixabay, and genanki.

Based on the **[Fluent Forever method](https://fluent-forever.com/)** by Gabriel Wyner — a proven system using spaced repetition, personalized context, and multi-sensory learning.

**[▶ Try the Live App](https://language-card-generator-anki-fluent-forever-method.streamlit.app/)** · **[📖 Grammar Framework](language_grammar_generator/README.md)**

---

## ⚡ Quick Start

### 1. Install & Run
```bash
cd LanguagLearning
pip install -r requirements.txt
streamlit run streamlit_app/app_v3.py
```

### 2. Set Up API Keys (Step 0 in-app)

The app guides you through setup on the **"Step 0: API Keys"** page. You need **3 free API keys**:

| # | Service | Key | Where to Get It | Cost |
|---|---------|-----|-----------------|------|
| 1 | **Gemini AI** (sentences) | `google_api_key` | [Google AI Studio](https://aistudio.google.com/apikey) | Free (1,500 requests/day) |
| 2 | **Text-to-Speech** (audio) | `google_tts_api_key` | [Google Cloud Console](https://console.cloud.google.com/) | Free (1M chars/month) |
| 3 | **Pixabay** (images) | `pixabay_api_key` | [pixabay.com/api](https://pixabay.com/api/docs/) | Free (5,000 images/month) |

> **⚠️ Important — Use two separate Google Cloud projects:**
> - **Project A** (Gemini): No billing enabled → preserves free tier (1,500 requests/day)
> - **Project B** (TTS): Billing enabled (required to activate TTS) → still **free** within 1M characters/month
>
> Why? Enabling billing on a GCP project upgrades *all* APIs in that project to paid tier. Keeping them separate protects Gemini's free quota.

### 3. Generate Your First Deck
1. Pick a language from 77 options
2. Select 1–5 words from frequency lists (or upload your own)
3. Choose difficulty, topics, and audio settings
4. Generate → Download `.apkg` → Import to Anki ✅

---

## ✨ Features

### Content Generation
- **AI Sentences** — Gemini AI generates 1–10 contextual sentences per word (default 4)
- **Grammar Analysis** — Color-coded grammatical breakdown with word-by-word explanations (11 languages)
- **Native Audio** — Google Cloud TTS with learner-friendly speed (0.8x default), adjustable 0.5x–1.5x
- **Images** — Pixabay integration with AI keyword extraction
- **IPA / Romanization** — Phonetic transcriptions for all languages; romanization for complex scripts (Hindi, Arabic, Persian, etc.)

### Deck Generation
- **77 Languages** — 44 with pre-built frequency word lists, all 77 with TTS support
- **3-Card Template** — Listening 🎧, Production 💬, Reading 📖 cards per word
- **5-Step Workflow** — Language → Words → Settings → Generate → Download
- **Direct Anki Import** — `.apkg` files ready to use

### Smart Features
- **30 Topic Filters** — Narrow sentences by theme (Food, Travel, Technology, Daily Life, etc.)
- **Real-Time Progress** — Live generation tracking with cancel option
- **Statistics Dashboard** — API quota monitoring with warnings at 80% and 100% usage
- **AI Repair Pipeline** — Auto-fixes malformed AI output (lower temperature for deterministic repair)
- **Graceful Degradation** — Audio/image failures never block card generation

### User Experience
- **Guest Mode** — Full app access without an account
- **Firebase Auth** — Optional sign-in (email/password or Google) for cloud sync
- **Per-Language Settings** — Save preferred difficulty, sentences/word, and audio speed per language
- **Dark / Light Theme** — Toggle in settings
- **Custom Word Lists** — Upload CSV/XLSX files with your own vocabulary

### 100% Free
- All core features are free — no premium tier, no paywalls
- Voluntary donations via Razorpay (optional, non-refundable)

---

## 🎴 Card Types

Each word generates **3 cards** for comprehensive learning:

| Card | Front | Back |
|------|-------|------|
| **Listening** 🎧 | Audio only | Sentence, image, translation, IPA, grammar |
| **Production** 💬 | English translation | Sentence, audio, image, IPA, grammar |
| **Reading** 📖 | Sentence text (color-coded grammar) | Audio, image, translation, IPA, grammar |

**Tip**: Use Anki's built-in "Record Own Voice" (R key) to practice speaking.

---

## 📋 How It Works

1. **Select a language and words** — Choose from frequency lists (max 5 per deck) or upload your own
2. **Configure settings** — Difficulty, sentence count, topics, audio speed, voice
3. **Generate** — AI creates sentences, audio, images, and IPA with real-time progress
4. **Download** — Get the `.apkg` file and import into Anki

---

## 🗣️ IPA & Romanization

**IPA (International Phonetic Alphabet)** provides accurate pronunciation for every language. Explore the interactive chart at **[ipachart.com](https://www.ipachart.com/)** — click any symbol to hear it.

For languages with complex scripts (Hindi, Arabic, Persian, Urdu, Bengali, and 8 more), we provide **romanization** using familiar Latin letters instead of strict IPA, making pronunciation more accessible for beginners.

---

## 🧠 Grammar Analyzers

**11 of 77 languages** have dedicated grammar analyzers that add color-coded sentence overlays with word-by-word explanations to your cards:

| Language | Code | Status |
|----------|------|--------|
| French | `fr` | ✅ Gold standard (v2.0) |
| Spanish | `es` | ✅ Implemented |
| German | `de` | ✅ Implemented |
| Chinese (Simplified) | `zh` | ✅ Implemented |
| Chinese (Traditional) | `zh-tw` | ✅ Implemented |
| Arabic | `ar` | ✅ Implemented |
| Hindi | `hi` | ✅ Implemented |
| Hungarian | `hu` | ✅ Implemented (v1.0) |
| Japanese | `ja` | ✅ Implemented (v1.0) |
| Korean | `ko` | ✅ Implemented (v1.0) |
| Turkish | `tr` | ✅ Implemented |

Grammar coloring preserves **language-specific concepts** — e.g., Chinese classifiers, Japanese particles, Arabic case markers each get their own unique colors, rather than being collapsed into generic English grammar categories.

All 77 languages work for deck generation (TTS, translations, frequency lists) even without an analyzer. The [Language Grammar Generator Framework](language_grammar_generator/README.md) provides a 7-phase process for creating new analyzers.

---

## 🛠️ Troubleshooting

### "API keys not persisting"
- Each section has its own **Save** button — click it after entering each key
- Keys are saved to `user_secrets.json` and persist across sessions

### "TTS not working"
- TTS requires a **separate GCP project** with billing enabled
- Billing is only needed to *activate* the API — usage is free within 1M chars/month
- Check that you entered the TTS key in the correct field (Section 2, not Section 1)

### "Invalid API key"
- Check for leading/trailing spaces when pasting
- Gemini key: get from [Google AI Studio](https://aistudio.google.com/apikey)
- TTS key: get from a billing-enabled GCP project's credentials page
- Pixabay key: get from [pixabay.com/api](https://pixabay.com/api/docs/)

### ".apkg file not created"
- Try with fewer words (1–3) to test
- Check the generation logs for specific error messages

### Audio sounds strange
- Try different voice options in sentence settings
- Adjust speed (0.7x–0.9x recommended for learners)

---

## 📊 API Limits (All Free Tier)

| Service | Free Limit | Billing Required? |
|---------|-----------|-------------------|
| **Gemini AI** | 1,500 requests/day | No |
| **Google Cloud TTS** | 1M characters/month (Standard voices) | Yes (to activate only) |
| **Pixabay** | 5,000 images/month | No |

The app's **Statistics** page tracks your usage in real time and warns you at 80% and 100% of daily/monthly limits.

**Tip**: Generate in batches throughout the day to stay within Gemini's daily limit.

---

## 📥 Importing to Anki

Double-click the `.apkg` file — Anki opens automatically and imports everything (sentences, audio, images, IPA).

---

## ☁️ Cloud Sync (Optional)

Sign in with Firebase (email/password or Google) to sync across devices:
- **Usage statistics** — track your learning progress
- **Custom word lists** — access from any device
- **Settings** — language preferences, favorites

No account needed for core functionality — **Guest mode** provides full access to deck generation.

---

## 📄 License

MIT License. Not affiliated with Fluent Forever or Anki.

---

## 🙏 Credits

- [Fluent Forever](https://fluent-forever.com/) — Proven language learning methodology
- [Google Cloud](https://cloud.google.com/) — Gemini AI and Text-to-Speech
- [Pixabay](https://pixabay.com/) — Free images
- [genanki](https://github.com/kerrickstaley/genanki) — Anki deck creation library

---

## 🚀 Changelog

### v3.4 (April 2026)
- ✅ **API Key Persistence** — All 3 Save buttons now persist keys to disk (previously session-only)
- ✅ **Two-Project GCP Setup** — Separate Gemini and TTS projects to protect free tier
- ✅ **Pixabay Images** — Replaced Google Custom Search with Pixabay for free image integration
- ✅ **8 Grammar Analyzers** — French (gold standard), Spanish, German, Chinese (Simplified & Traditional), Arabic, Hindi, Turkish
- ✅ **Topic Filtering** — 30 curated topics to narrow sentence generation
- ✅ **Statistics Dashboard** — Real-time API quota tracking with 80%/100% health warnings
- ✅ **Repository Cleanup** — Removed 21 unused test/debug files (3 had hardcoded API keys)

### v3.3 (January 2026)
- ✅ **Language Grammar Generator Framework** — 7-phase process for creating analyzers ([language_grammar_generator/](language_grammar_generator/))
- ✅ **Romanization Support** — Learner-friendly pronunciation for 13 Indic/Arabic languages
- ✅ **Grammar Analysis** — AI-powered color-coded grammatical breakdowns
- ✅ **Enhanced Error Recovery** — AI repair pipeline with exponential backoff retries
- ✅ **Documentation Restructuring** — Modular guides (research, architecture, implementation, testing, deployment)

---

**Ready to start learning?**
```bash
streamlit run streamlit_app/app_v3.py
```

**[▶ Try the Live App](https://language-card-generator-anki-fluent-forever-method.streamlit.app/)** · **Happy learning!** ✨
