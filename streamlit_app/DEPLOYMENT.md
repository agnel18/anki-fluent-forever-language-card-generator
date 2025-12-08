# Streamlit App Deployment Guide

## Local Development

### 1. Setup

```bash
cd streamlit_app
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

### 2. Create Secrets File

Create `.streamlit/secrets.toml`:
```toml
GROQ_API_KEY = "your_groq_key"
PIXABAY_API_KEY = "your_pixabay_key"
```

### 3. Run Locally

```bash
streamlit run app.py
```

Navigate to `http://localhost:8501`

---

## Streamlit Cloud Deployment (FREE)

### 1. Push to GitHub

```bash
cd ..
git add streamlit_app/
git commit -m "add: streamlit GUI"
git push origin main
```

### 2. Create Streamlit Account

- Go to [streamlit.io/cloud](https://streamlit.io/cloud)
- Sign up with GitHub
- Click "New app"

### 3. Deploy App

- **Repository**: `agnel18/anki-fluent-forever-language-card-generator`
- **Branch**: `main`
- **Main file path**: `streamlit_app/app.py`
- Click **"Deploy"**

### 4. Add Secrets

- Go to **Settings** → **Secrets**
- Paste contents of `.streamlit/secrets.toml.example`:
  ```toml
  GROQ_API_KEY = "your_groq_key"
  PIXABAY_API_KEY = "your_pixabay_key"
  ```
- Click **"Save"**

### 5. Done! 🎉

Your app is now live at: `https://share.streamlit.io/agnel18/anki-fluent-forever-language-card-generator/main/streamlit_app/app.py`

---

## Docker Deployment (Advanced)

Create `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY streamlit_app /app

RUN pip install -r requirements.txt

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build & run:
```bash
docker build -t anki-generator .
docker run -p 8501:8501 \
  -e GROQ_API_KEY="your_key" \
  -e PIXABAY_API_KEY="your_key" \
  anki-generator
```

---

## Performance Tips

1. **Session state caching**: Avoid regenerating API calls
2. **Async audio**: Edge TTS batches asynchronously for speed
3. **Temporary directories**: Cleanup after ZIP creation
4. **Rate limits**: Pixabay ~5,000 req/day; Groq unlimited (free)

---

## Troubleshooting

**"Import Error: No module named 'edge_tts'"**
- Run: `pip install edge-tts`

**"Groq API Error: Insufficient quota"**
- Check API key at console.groq.com
- Ensure billing is active

**"Pixabay Error: 400 Bad Request"**
- Verify API key format
- Check query string encoding

**"Audio files not downloading"**
- Check internet connection
- Ensure Edge TTS voice code is valid
- Try simpler text first

---

## Cost Breakdown

- **Groq**: Free (1M+ tokens/day)
- **Edge TTS**: Free (unlimited)
- **Pixabay**: Free (5,000 images/day)
- **Streamlit Cloud**: Free (small deployments)

**Total cost: $0** ✅

---

For updates: [GitHub](https://github.com/agnel18/anki-fluent-forever-language-card-generator)
