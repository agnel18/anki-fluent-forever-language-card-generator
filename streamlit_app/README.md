# Streamlit GUI - Anki Card Generator

🌍 **Production-ready, accessible Streamlit app** for generating Anki language learning cards.

**Suitable for ages 10-90** with:
- Large fonts (16px+ base)
- High contrast dark theme
- Colorblind-friendly palette
- Minimal jargon
- Multi-language UI (English, Spanish, French, Hindi, Mandarin)

---

## ✨ Features

### Core Functionality
- **Groq API**: Generate 10 natural sentences per word (llama-3.3-70b-versatile model)
- **Edge TTS Audio**: Free, unlimited native speaker audio (200+ languages supported)
- **Pixabay Images**: Randomized, relevant images for each sentence
- **ZIP Export**: Complete Anki deck with TSV + audio + images

### Input Options
1. **Single Word**: Type word + meaning manually
2. **CSV Upload**: Import custom word lists (word, meaning columns)
3. **Frequency List** *(coming soon)*: Use pre-built 109-language lists

### Accessibility
- **Top 5 Languages Fast Track**: English, Mandarin, Hindi, Spanish, Arabic
- **All 109 Languages**: Full list for any learner
- **Font Size Selector**: S/M/L adjustable in settings
- **Colorblind Palette**: High contrast, accessible colors
- **Session Tracking**: Progress preserved within session
- **Helpful Tooltips**: Every setting explained clearly

### Cost Calculator
- **Real-time estimates**: See Groq tokens, Pixabay requests, API usage
- **Free tier warnings**: Stay safe from quota limits
- **Detailed breakdown**: Sentences, images, requests

---

## 🚀 Quick Start (Local)

### 1. Install

```bash
cd streamlit_app
pip install -r requirements.txt
```

### 2. Create Secrets

Create `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "gsk_..."
PIXABAY_API_KEY = "..."
```

Get keys:
- [Groq](https://console.groq.com): Free API key (no billing)
- [Pixabay](https://pixabay.com/api): Free API key (5,000 req/day)

### 3. Run

```bash
streamlit run app.py
```

Visit `http://localhost:8501` 🎉

---

## ☁️ Deploy to Streamlit Cloud (FREE)

### 1. Push Code

```bash
cd ..
git add streamlit_app/
git commit -m "add: streamlit GUI"
git push origin main
```

### 2. Create App on Streamlit Cloud

- [streamlit.io/cloud](https://streamlit.io/cloud)
- Sign in with GitHub
- Click "New app"
- Select repo, branch `main`, file `streamlit_app/app.py`

### 3. Add Secrets

In Streamlit Cloud dashboard → Settings → Secrets:
```toml
GROQ_API_KEY = "gsk_..."
PIXABAY_API_KEY = "..."
```

### 4. Deploy

Click "Deploy" and share your URL! 🌐

For detailed guide, see [DEPLOYMENT.md](DEPLOYMENT.md)

---

## 📁 Project Structure

```
streamlit_app/
├── app.py                         # Main Streamlit GUI
├── core_functions.py              # Groq, Edge TTS, Pixabay, TSV, ZIP
├── languages.yaml                 # 109 languages + voices + UI strings
├── requirements.txt               # Python dependencies
├── DEPLOYMENT.md                  # Cloud deployment guide
├── .streamlit/
│   ├── config.toml               # Dark theme, large fonts
│   └── secrets.toml.example      # API key template
└── README.md                      # This file
```

---

## 🎯 How It Works

1. **Select Language**: Top 5 quick-pick or all 109 options
2. **Input Words**: Single, CSV, or frequency list
3. **Review Settings**: Sentences, length, difficulty, voice
4. **Generate**: Groq → Edge TTS → Pixabay (parallel processing)
5. **Download**: ZIP with ANKI_IMPORT.tsv + audio + images
6. **Import to Anki**: File → Import → Select TSV → Done!

---

## 💰 Cost Breakdown

| Component | Free Tier | Cost |
|-----------|-----------|------|
| **Groq** | 1M+ tokens/day | $0 |
| **Edge TTS** | Unlimited | $0 |
| **Pixabay** | 5,000 images/day | $0 |
| **Streamlit Cloud** | Light deployments | $0 |
| **Total** | - | **$0** ✅ |

---

## 🎨 Customization

### Change Theme Colors

Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#58a6ff"          # Blue highlights
backgroundColor = "#0e1117"       # Dark background
textColor = "#e6edf3"             # Light text
```

### Add More Languages to UI

Edit `languages.yaml`:
```yaml
ui_strings:
  ja:
    title: "🌍 Fluent Forever Anki カード生成器"
    # ... (copy and translate other keys)
```

### Adjust Font Size

Modify CSS in `app.py`:
```python
st.markdown("""
<style>
    :root {
        --base-font-size: 18px;  # Increase from 16px
    }
</style>
""")
```

---

## ⚠️ Troubleshooting

**"Import Error: No module named 'edge_tts'"**
```bash
pip install edge-tts
```

**"Groq API Key Error"**
- Get free key: [console.groq.com](https://console.groq.com)
- Paste into `.streamlit/secrets.toml`

**"Pixabay 400 Error"**
- Verify API key format
- Check rate limits at pixabay.com/api/docs

**"Audio generation slow"**
- Edge TTS is async but sequential; 10 sentences ~30 seconds normal
- Check internet connection

**"Images not downloading"**
- Verify Pixabay key
- Try simpler search queries (e.g., "house" not "my beautiful house")

---

## 📊 Performance

- **Single word → Anki deck**: ~2-3 minutes
- **10 words → Anki deck**: ~20-30 minutes
- **100 words → Anki deck**: ~3-4 hours (can run unattended)

---

## 🔐 Security

- **API keys stored in `st.secrets.toml`** (never committed to Git)
- **Streamlit Cloud secrets**: Encrypted, isolated per deployment
- **No user data stored**: All processing is local/temporary
- **Open source**: Audit code anytime on [GitHub](https://github.com/agnel18/anki-fluent-forever-language-card-generator)

---

## 📚 Learn More

- [Streamlit Docs](https://docs.streamlit.io)
- [Groq API Docs](https://console.groq.com/docs)
- [Edge TTS GitHub](https://github.com/rany2/edge-tts)
- [Pixabay API Docs](https://pixabay.com/api/docs)

---

## 💬 Support

Issues? Questions?
- [GitHub Issues](https://github.com/agnel18/anki-fluent-forever-language-card-generator/issues)
- [Discussions](https://github.com/agnel18/anki-fluent-forever-language-card-generator/discussions)

---

## 📝 License

MIT License - Free for personal and commercial use.

---

**Made with ❤️ for language learners worldwide** 🌍
