# Google Cloud TTS Setup Guide

## Quick Summary

**Google Cloud TTS is OPTIONAL** - it's a safety fallback for audio generation.

- **Primary audio:** Edge TTS (free, no setup needed) ✅
- **Backup audio:** Google Cloud TTS (optional, 5-minute setup) 🔄
- **Both fail?** Manual upload available 📤

## Why Google Cloud TTS?

Edge TTS occasionally has service issues. Google Cloud TTS provides a reliable backup that automatically kicks in if Edge TTS fails.

**Free tier:** 1 million characters/month (usually more than enough)

---

## Step-by-Step Setup (5 minutes)

### Step 1: Create Google Cloud Account

1. Go to https://console.cloud.google.com
2. If you don't have a Google Cloud account:
   - Click "Create project"
   - Name it: `Language Learning` (or anything you want)
   - Click "Create"
   - Wait for it to activate

### Step 2: Enable Text-to-Speech API

1. In the search bar at the top, search for: `Text-to-Speech API`
2. Click on it from the search results
3. Click the blue "ENABLE" button
4. Wait 30 seconds for it to activate
5. ✅ You should see "API enabled" message

### Step 3: Create Service Account

1. Go to: https://console.cloud.google.com/iam-admin/serviceaccounts
2. Click "CREATE SERVICE ACCOUNT"
3. Fill in:
   - **Service account name:** `language-learning-tts` (or any name)
   - **Service account ID:** (auto-fills)
4. Click "Create and Continue"
5. In the next screen, click "Continue" (skip the optional steps)
6. Click "Done"
7. ✅ Service account created

### Step 4: Create & Download JSON Key

1. You'll see a list of service accounts
2. Click on the one you just created (should have your project name)
3. Go to the "KEYS" tab at the top
4. Click "Add Key" → "Create new key"
5. Choose "JSON"
6. Click "Create"
7. A file automatically downloads: `service-account-key.json` (or similar)
8. ✅ Check your Downloads folder

### Step 5: Place the File in Project

1. **Rename the downloaded file:**
   - Old name: `service-account-key.json`
   - New name: `languagelearning-480303-93748916f7bd.json`

2. **Move it to the main project folder:**
   - Place it at: `d:\Language Learning\LanguagLearning\languagelearning-480303-93748916f7bd.json`
   - This is the same folder as `app_v3.py`, `core_functions.py`, etc.

3. ✅ Don't commit this file to GitHub (already in .gitignore)

### Step 6: Restart & Verify

1. Refresh the app page (or close and reopen)
2. On the "API Setup" page, you should see:
   ```
   ✅ Google Cloud TTS is configured! 
      (Will auto-use as fallback if Edge TTS fails)
   ```
3. ✅ Done! Google TTS is ready

---

## What Happens Now?

### Normal Flow (Edge TTS Works)
```
generate_audio()
    ↓
Try Edge TTS ✅ SUCCESS
    ↓
Audio file created (10-15KB)
```

### Fallback Flow (Edge TTS Fails)
```
generate_audio()
    ↓
Try Edge TTS ❌ FAILED
    ↓
Try Google Cloud TTS ✅ SUCCESS
    ↓
Audio file created using Google
```

### Both Fail (Rare)
```
Both TTS fail
    ↓
Error message shows
    ↓
User can manually upload CSV
```

---

## Cost Information

### Edge TTS
- **Cost:** Free (Microsoft service)
- **Limits:** Some regional/rate limits but generally unlimited
- **Quality:** Good natural voices

### Google Cloud TTS
- **Cost:** $0-0.016 per 1,000 characters
- **Free tier:** 1 million characters/month
- **Quality:** Excellent neural voices

### Typical Usage
- 10 sentences × 50 words = 500 sentences
- Average sentence: 50 characters
- Total: ~25,000 characters
- Cost: $0.40 or completely free (within free tier)

---

## Troubleshooting

### "Google Cloud TTS credentials not found"

**Problem:** File wasn't placed correctly

**Solution:**
1. Check the file location:
   ```
   d:\Language Learning\LanguagLearning\languagelearning-480303-93748916f7bd.json
   ```
2. File name must be EXACT (including the numbers)
3. Restart the app after moving the file

### "Google Cloud TTS library not installed"

**Problem:** Python package missing

**Solution:**
```powershell
cd "d:\Language Learning\LanguagLearning"
.\.venv\Scripts\python.exe -m pip install google-cloud-texttospeech
```

### "Both TTS methods failed"

**Problem:** Both Edge and Google TTS failed

**Causes:**
1. No internet connection
2. API key invalid
3. Quota exceeded
4. Language not supported

**Solutions:**
1. Check internet connection
2. Try again in a few minutes
3. Use manual CSV upload option
4. Check error logs for more details

---

## Security Notes

⚠️ **Your credentials file contains sensitive information**

- ✅ It's in .gitignore (won't be committed)
- ✅ Keep it private (never share with others)
- ✅ Delete it if you share your computer
- ✅ Can regenerate keys from Google Cloud Console anytime

---

## Disable Google TTS Fallback

If you want Edge TTS only (and no Google fallback):

**Edit:** `streamlit_app/core_functions.py`

Find this line (~line 240):
```python
language=language,
```

Change the next line from:
```python
use_google_fallback=True,
```

To:
```python
use_google_fallback=False,
```

Then restart the app.

---

## Questions?

- **Edge TTS issues:** Check https://github.com/rany2/edge-tts/issues
- **Google TTS issues:** Check https://cloud.google.com/text-to-speech/docs
- **This app:** Check the GitHub repository

---

## Quick Reference

| Component | Status | Setup Time | Cost |
|-----------|--------|-----------|------|
| Edge TTS | Primary | ✅ None | Free |
| Google TTS | Fallback | ⏱️ 5 min | Free tier |
| Groq API | Sentences | ✅ Already set | Free tier |
| Pixabay API | Images | ✅ Already set | Free tier |

**Total setup time:** ~5 minutes (optional)
**Total cost:** Usually free, max $0-2/month for Google TTS if heavily used
