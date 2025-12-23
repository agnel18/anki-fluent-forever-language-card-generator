# 🚀 Language Anki Deck Generator - Deployment Guide

## Overview
This guide will help you deploy your Language Anki Deck Generator to **Streamlit Cloud** and optionally configure **Firebase** for data persistence.

## Prerequisites
- ✅ GitHub account
- ✅ Streamlit Cloud account (free)
- ✅ API Keys: Groq, Pixabay, Gemini (optional)
- ✅ Firebase project (optional, for data persistence)

---

## Step 1: Prepare Your Repository

### 1.1 Ensure Repository Structure
Your repository should have this structure:
```
├── app.py                    # Main entry point (created)
├── requirements.txt          # Dependencies (updated)
├── .streamlit/
│   ├── config.toml          # Streamlit configuration
│   └── secrets.toml         # API keys and secrets (template)
├── streamlit_app/           # Your app code
│   ├── app_v3.py
│   ├── core_functions.py
│   └── ...
└── README.md
```

### 1.2 Update .gitignore
Make sure your `.gitignore` includes:
```
# Virtual environment
.venv/
venv/

# Secrets (IMPORTANT!)
.streamlit/secrets.toml
firebase_config.json
.env

# Generated files
output/
*.db
*.log
```

---

## Step 2: Deploy to Streamlit Cloud

### 2.1 Push Code to GitHub
```bash
git add .
git commit -m "Prepare for deployment"
git push origin main
```

### 2.2 Deploy on Streamlit Cloud

1. Go to **[share.streamlit.io](https://share.streamlit.io)**
2. Sign in with your GitHub account
3. Click **"New app"**
4. Select your repository: `agnel18/language-anki-deck-generator`
5. Set the main file path: `app.py`
6. Click **"Deploy"**

### 2.3 Configure Secrets

After deployment, you need to add your API keys:

1. Go to your app on Streamlit Cloud
2. Click **"Manage app"** → **"Secrets"**
3. Copy the content from `.streamlit/secrets.toml` and replace with your actual keys:

```toml
# Required API Keys
GROQ_API_KEY = "sk-your-groq-key-here"
PIXABAY_API_KEY = "your-pixabay-key-here"
GEMINI_API_KEY = "your-gemini-key-here"  # Optional

# Firebase (if using)
FIREBASE_PROJECT_ID = "your-project-id"
FIREBASE_PRIVATE_KEY_ID = "your-key-id"
FIREBASE_PRIVATE_KEY = "-----BEGIN PRIVATE KEY-----\nyour-key\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL = "firebase-adminsdk@your-project.iam.gserviceaccount.com"
FIREBASE_CLIENT_ID = "your-client-id"
```

### 2.4 Redeploy
After adding secrets, click **"Save"** and then **"Redeploy"**

---

## Step 3: Optional - Firebase Setup

If you want persistent data storage:

### 3.1 Follow Firebase Setup Guide
See `FIREBASE_SETUP.md` for complete Firebase configuration.

### 3.2 Update Secrets
Add Firebase configuration to your Streamlit Cloud secrets.

---

## Step 4: Test Your Live App

1. Visit your Streamlit Cloud URL
2. Test the main features:
   - Language selection
   - Word selection
   - Deck generation
   - Download functionality

---

## Troubleshooting

### Common Issues:

**App won't start:**
- Check that `app.py` exists in root directory
- Verify `requirements.txt` includes all dependencies
- Check Streamlit Cloud logs for errors

**API errors:**
- Verify all API keys are correctly set in secrets
- Check API key formats and permissions

**Firebase issues:**
- Ensure Firebase service account key is properly formatted
- Check Firebase project permissions

### Useful Commands:

```bash
# Test locally before deployment
streamlit run app.py

# Check for import errors
python -c "import streamlit_app.app_v3"

# Validate requirements
pip install -r requirements.txt
```

---

## Performance Optimization

For better performance on Streamlit Cloud:

1. **Use caching** for expensive operations
2. **Optimize images** and media files
3. **Consider upgrading** to paid plan for more resources
4. **Monitor usage** in Streamlit Cloud dashboard

---

## Maintenance

- **Monitor logs** in Streamlit Cloud dashboard
- **Update dependencies** regularly
- **Backup Firebase data** if using Firebase
- **Test new features** locally before deploying

---

🎉 **Congratulations! Your Language Anki Deck Generator is now live!**

Share your app URL with others and start helping people learn languages! 🌍📚