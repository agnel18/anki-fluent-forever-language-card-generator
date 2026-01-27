# 🌍 Language Anki Deck Generator

**Generate professional language learning Anki decks in minutes.**

Create complete decks with AI-written sentences, native audio, beautiful images, and phonetic transcriptions—**for 77 languages**. Built with Google Cloud services (Gemini AI, Google Custom Search, Google Cloud Text-to-Speech) and genanki.

Based on the **[Fluent Forever method](https://fluent-forever.com/)** by Gabriel Wyner—a proven system using spaced repetition, personalized context, and multi-sensory learning.

---

## ⚡ Quick Start

### 1. Install
```bash
cd LanguagLearning
pip install -r requirements.txt
```

### 2. Get API Keys

#### Required APIs
- **Google Cloud** (AI sentences, images, audio): https://console.cloud.google.com/

**Note**: Single Google Cloud API key provides access to all services (Gemini AI, Custom Search, Text-to-Speech).

### 3. Run & Configure APIs
```bash
streamlit run streamlit_app/app_v3.py
```
**In the app:**
1. Enter your Google Cloud API key (required for all services)
2. Test the API key
3. Save and proceed

### 4. Generate Your First Deck
1. Pick a language (API keys already configured)
2. Select 1-10 words (max 10 per generation)
3. Hit "Generate"
4. Download & import to Anki ✅

---

## ✨ Features

### Core Functionality
- **AI Sentences** — Google Gemini generates 10 contextual sentences per word
- **Grammar Analysis** — AI-powered grammatical breakdown with color-coded elements
- **Native Audio** — Google Cloud Text-to-Speech with 200+ neural voices, adjustable speed & pitch
- **Beautiful Images** — Google Custom Search API with keyword extraction
- **IPA Transcriptions** — Official phonetic transcriptions or romanization for learner-friendly languages ([IPA Chart Reference](https://www.ipachart.com/))
- **3-Card Anki Template** — Listening, Production, Reading cards
- **Direct Anki Import** — `.apkg` files ready to use
- **Progress Tracking** — SQLite database saves your progress

### Advanced Features
- **77 Languages** — Pre-built frequency word lists
- **Custom Word Lists** — Upload your own CSV files
- **Audio Controls** — Speed (0.5x-1.5x) and pitch (-20% to +20%)
- **Rate Limit Monitoring** — Smart warnings for API limits
- **Error Recovery** — Graceful handling of API failures
- **Theme Toggle** — Light/dark mode support

---

## �️ Language Grammar Generator Framework

For developers and linguists interested in extending support to new languages:

- **[Modular Framework](language_grammar_generator/)** — Domain-driven design for creating grammar analyzers
- **77 Language Support** — Comprehensive templates and guides for all target languages
- **AI-Powered Analysis** — Advanced prompting techniques for grammatical breakdown
- **Quality Assurance** — Automated testing and validation frameworks
- **Production Ready** — Deployment guides and monitoring strategies

**See**: [language_grammar_generator/README.md](language_grammar_generator/README.md) for implementation details.

---

## �🎴 Card Types

Each word generates 3 cards for comprehensive learning:

1. **Listening Card** 🎧  
   *Front*: Audio only  
   *Back*: Sentence, image, translation, IPA, grammar analysis

2. **Production Card** 💬  
   *Front*: English translation  
   *Back*: Sentence, audio, image, IPA, grammar analysis

3. **Reading Card** 📖  
   *Front*: Sentence text (with color-coded grammar elements)  
   *Back*: Audio, image, translation, IPA, grammar analysis

**Tip**: Use Anki's built-in "Record Own Voice" (R key) on the Pronunciation card to practice speaking.

---

## 📋 How It Works
1. **Select a language and words** from the frequency list (max 10 per generation)
2. **Configure settings**: difficulty, sentence length, audio speed, voice
3. **Generate deck**: AI creates sentences, audio, images, and IPA
4. **Download the .apkg** and import into Anki

---

## � **Understanding IPA Transcriptions**

**IPA (International Phonetic Alphabet)** is the universal system for accurately representing pronunciation using special symbols.

### Why IPA Matters for Language Learning
- **Accurate Pronunciation**: Learn exactly how native speakers pronounce words
- **Consistent System**: Same symbols mean the same sounds across all languages
- **Scientific Standard**: Used by linguists, dictionaries, and language teachers worldwide

### How to Use IPA in Your Learning
1. **Compare Sounds**: Match IPA symbols to sounds in your native language
2. **Practice Pronunciation**: Use IPA as a guide for speaking practice
3. **Identify Differences**: Spot sounds that don't exist in your language

### Interactive IPA Learning
Visit **[ipachart.com](https://www.ipachart.com/)** for:
- **Interactive Chart**: Click any IPA symbol to hear it pronounced
- **Audio Examples**: Real human recordings of each sound
- **Mobile-Friendly**: Learn on any device
- **Free Access**: No login required, no ads blocking content

**Example**: The English word "think" is transcribed as `/θɪŋk/` in IPA.
- `/θ/` = "th" as in "think" (not "this")
- `/ɪ/` = "i" as in "sit"
- `/ŋ/` = "ng" as in "sing"
- `/k/` = "k" as in "cat"

**Note**: For learner-friendly languages with complex scripts (Hindi, Arabic, Persian, etc.), we provide romanization using familiar letters instead of strict IPA symbols for easier learning.

---

## �🛠️ Troubleshooting

### "Images show as filenames instead of pictures"
- ✅ **Fixed in v3.1** — Images now display properly in Anki
- ✅ Verify you're using the latest version (`app_v3.py`)

### "Invalid API key"
- ✅ Check for typos in your Google Cloud API key
- ✅ Generate new key if needed

### ".apkg file not created"
- ✅ Check Google Custom Search API key and Engine ID (images required)
- ✅ Try with fewer words (1-3 to test)

### Audio sounds strange
- ✅ Try different voice options
- ✅ Adjust speed (0.7x-0.9x recommended for learners)

---

## 📊 API Limits & Best Practices

### Google Cloud Services
- **Gemini AI**: 1,500 requests/day (free tier), higher limits with billing
- **Custom Search**: 100 queries/day (free), 10,000/day with billing
- **Text-to-Speech**: 1 million characters/month (free), 4 million with billing

**Tip**: Generate in batches throughout the day to stay within limits.

---

## 📥 Importing to Anki

**Easiest way**: Double-click the `.apkg` file - Anki opens automatically and imports everything.

---

## ☁️ Optional: Cloud Sync

Sync progress across devices with Firebase (optional).

---

## 📄 License

MIT License. Not affiliated with Fluent Forever or Anki.

---

## 🙏 Credits

- [Fluent Forever](https://fluent-forever.com/) - Proven language learning method
- [Google Cloud](https://cloud.google.com/) - AI, search, and text-to-speech services
- [genanki](https://github.com/kerrickstaley/genanki) - Anki deck creation

---

## 🚀 What's New (v3.3)

- ✅ **Modular Language Grammar Generator** — Comprehensive framework for creating analyzers for all 77 languages ([language_grammar_generator/](language_grammar_generator/))
- ✅ **Repository Cleanup** — Archived obsolete files and migration docs (~50+ files safely moved to `20260127_old_files/`)
- ✅ **Documentation Restructuring** — Split monolithic template into modular guides (research, architecture, implementation, testing, deployment)
- ✅ **Romanization Support** — Learner-friendly pronunciation for 13 Indic/Arabic languages (hi, ar, fa, ur, bn, pa, gu, or, ta, te, kn, ml, si)
- ✅ **Grammar Analysis** — AI-powered grammatical breakdown with color-coded elements
- ✅ **Fixed Image Display** — Images now show properly in Anki cards
- ✅ **Enhanced Error Recovery** — Better API failure handling
- ✅ **10-Word Limit** — Prevents API rate limit issues
- ✅ **Improved Media Embedding** — All audio/images in .apkg files
- ✅ **Batch QA Framework** — 20x API efficiency gains for testing
- ✅ **Spanish Analyzer Fix** — Words with punctuation now color correctly
- ✅ **Git Backup Strategy** — Safe cleanup with version control preservation

---

**Ready to start learning?**
```bash
streamlit run streamlit_app/app_v3.py
```

**Happy learning!** ✨
