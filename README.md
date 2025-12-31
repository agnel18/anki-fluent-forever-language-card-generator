# 🌍 Language Anki Deck Generator

**Generate professional language learning Anki decks in minutes.**

Create complete decks with AI-written sentences, native audio, beautiful images, and phonetic transcriptions—**for 74 languages**. Built with Groq, Edge TTS, Pixabay, and genanki.

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
3. Select 1-10 words (max 10 per generation)
4. Hit "Generate"
5. Download & import to Anki ✅

---

## ✨ Features

### Core Functionality
- **AI Sentences** — Groq generates 10 contextual sentences per word
- **Native Audio** — Edge TTS with 200+ voices, adjustable speed & pitch
- **Beautiful Images** — Pixabay API with keyword extraction
- **IPA Transcriptions** — Official phonetic transcriptions ([IPA Chart Reference](https://www.ipachart.com/))
- **3-Card Anki Template** — Listening, Production, Reading cards
- **Direct Anki Import** — `.apkg` files ready to use
- **Progress Tracking** — SQLite database saves your progress

### Advanced Features
- **74 Languages** — Pre-built frequency word lists
- **Custom Word Lists** — Upload your own CSV files
- **Audio Controls** — Speed (0.5x-1.5x) and pitch (-20% to +20%)
- **Rate Limit Monitoring** — Smart warnings for API limits
- **Error Recovery** — Graceful handling of API failures
- **Theme Toggle** — Light/dark mode support

---

## 🎴 Card Types

Each word generates 3 cards for comprehensive learning:

1. **Listening Card** 🎧  
   *Front*: Audio only  
   *Back*: Sentence, image, translation, IPA, word info

2. **Production Card** 💬  
   *Front*: English translation  
   *Back*: Sentence, audio, image, IPA, word info

3. **Reading Card** 📖  
   *Front*: Sentence text  
   *Back*: Audio, image, translation, IPA, word info

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

📖 **For a comprehensive IPA learning guide**, see [docs/guides/IPA_GUIDE.md](docs/guides/IPA_GUIDE.md)

---

## �🛠️ Troubleshooting

### "Images show as filenames instead of pictures"
- ✅ **Fixed in v3.1** — Images now display properly in Anki
- ✅ Verify you're using the latest version (`app_v3.py`)

### "Invalid API key"
- ✅ Check for typos in your Groq/Pixabay keys
- ✅ Generate new keys if needed

### ".apkg file not created"
- ✅ Check Pixabay API key (images required)
- ✅ Try with fewer words (1-3 to test)

### Audio sounds strange
- ✅ Try different voice options
- ✅ Adjust speed (0.7x-0.9x recommended for learners)

---

## 📊 API Limits & Best Practices

### Groq (Sentences)
- **Limit**: 30 requests/minute, ~4M tokens/day (free)
- **Safe**: 5-10 words per batch

### Pixabay (Images)
- **Limit**: 5,000 images/day (free)
- **Safe**: Under 50 words/day

### Edge TTS (Audio)
- **Limit**: Unlimited (free, no keys needed)

**Tip**: Generate in batches throughout the day to stay within limits.

---

## 📥 Importing to Anki

**Easiest way**: Double-click the `.apkg` file - Anki opens automatically and imports everything.

**See**: [ANKI_SETUP.md](./ANKI_SETUP.md) for detailed import help

---

## ☁️ Optional: Cloud Sync

Sync progress across devices with Firebase (optional).

**See**: [FIREBASE_SETUP.md](./FIREBASE_SETUP.md) for setup instructions.

---

## 📄 License

MIT License. Not affiliated with Fluent Forever or Anki.

---

## 🙏 Credits

- [Fluent Forever](https://fluent-forever.com/) - Proven language learning method
- [Groq](https://groq.com/) - Fast AI inference
- [Pixabay](https://pixabay.com/) - Free images
- [Edge TTS](https://github.com/rany2/edge-tts) - Neural voices
- [genanki](https://github.com/kerrickstaley/genanki) - Anki deck creation

---

## 🚀 What's New (v3.1)

- ✅ **Fixed Image Display** — Images now show properly in Anki cards
- ✅ **Repository Cleanup** — Removed obsolete files (~10MB saved)
- ✅ **Enhanced Error Recovery** — Better API failure handling
- ✅ **10-Word Limit** — Prevents API rate limit issues
- ✅ **Improved Media Embedding** — All audio/images in .apkg files

---

**Ready to start learning?**
```bash
streamlit run streamlit_app/app_v3.py
```

**Happy learning!** ✨
