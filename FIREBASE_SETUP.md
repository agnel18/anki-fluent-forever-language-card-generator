# Firebase Setup Guide (5 Minutes)

This guide walks you through setting up Firebase for the Language Learning app to sync progress across sessions.

## What You Get

- ✅ Persistent progress tracking (survives app restarts)
- ✅ Statistics and generation history
- ✅ Ready for multi-user deployment
- ✅ Completely FREE (Spark plan)

## Prerequisites

- Google account (free)
- 5 minutes of your time

---

## Step-by-Step Setup

### Step 1: Create Firebase Project

1. Go to **https://console.firebase.google.com**
2. Click **"Add project"** (or **"Create a project"**)
3. Enter project name:
   ```
   Language-Learning-App
   ```
4. Click **"Continue"**
5. Disable "Enable Google Analytics" (optional, but simplifies setup)
6. Click **"Create project"**
7. Wait for project to initialize (~30 seconds)
8. Click **"Continue"** when ready

### Step 2: Create Service Account Key

1. Go to **Project Settings** (click the ⚙️ gear icon at top)
2. Click **"Service Accounts"** tab
3. Click **"Python"** (generates Python-specific instructions)
4. Click **"Generate a new private key"**
5. **A JSON file will download automatically**
   - Usually named: `language-learning-app-xxxxx.json`
   - This is your **service account key** - keep it safe!

### Step 3: Add Key to Your Project

1. **Rename** the downloaded JSON file to:
   ```
   firebase_config.json
   ```

2. **Place it in** the main project folder:
   ```
   d:\Language Learning\LanguagLearning\firebase_config.json
   ```

3. **Do NOT commit this file to GitHub!**
   - It's already in `.gitignore`
   - Keep it private (never share online)

### Step 4: Enable Firestore Database

1. In Firebase Console, go to **"Firestore Database"** (left menu)
2. Click **"Create Database"**
3. Select **"Start in test mode"**
4. Click **"Enable"**
5. Wait for database to initialize

**Note:** Test mode allows reads/writes without authentication. Safe for development.

### Step 5: Verify Installation

1. Install Firebase SDK (if not already installed):
   ```bash
   pip install firebase-admin
   ```

2. Restart the Streamlit app:
   ```bash
   cd "d:\Language Learning\LanguagLearning"
   streamlit run streamlit_app/app_v3.py
   ```

3. You should see in the console:
   ```
   ✅ Firebase initialized successfully
   ```

---

## How It Works

### Progress Syncing

When you generate a deck with "Track progress" enabled:

1. **Locally (SQLite):**
   - Words marked as completed
   - Stats updated (times_generated, last_session)

2. **Cloud (Firebase):**
   - Progress synced to Firestore
   - Session ID tracked
   - History logged
   - Survives app restarts ✅

### Data Structure

Your progress in Firebase:

```
users/
  {session_id}/
    ├─ progress/
    │   ├─ Spanish
    │   │   ├─ words: ["el", "gato", "casa", ...]
    │   │   ├─ total_generated: 150
    │   │   ├─ last_updated: "2025-12-08T..."
    │   │
    │   ├─ French
    │       ├─ words: [...]
    │
    ├─ history/
    │   ├─ {generation_001}
    │   │   ├─ language: "Spanish"
    │   │   ├─ words_count: 10
    │   │   ├─ timestamp: "2025-12-08T..."
    │
    ├─ metadata/
        └─ settings
            ├─ difficulty: "intermediate"
            ├─ audio_speed: 0.8
            ...
```

---

## Firebase Free Tier Limits

✅ **More than enough for personal/small group use:**

- 1 GB storage
- 50,000 reads/day
- 20,000 writes/day
- 10 GB/month bandwidth

For reference:
- 1 deck generation = ~20 read/writes
- Even 100 users/day won't hit limits

---

## Troubleshooting

### "Firebase initialized successfully" not showing?

**Check:**
1. Is `firebase_config.json` in the right location?
   ```
   d:\Language Learning\LanguagLearning\firebase_config.json
   ```

2. Is file readable? (Windows: right-click → Properties → Security)

3. Is Firebase SDK installed?
   ```bash
   pip install firebase-admin
   ```

### Firestore Database shows "Error"?

**Solution:**
1. Go back to Firestore Database page
2. Click **"Create Database"** again
3. Make sure **"Production mode"** is selected
4. Click **"Enable"**

### Still having issues?

The app will work fine **without Firebase** - it just won't sync progress to the cloud.

All data stays local in SQLite, which is still fast and persistent!

---

## What's Next?

### Local Development (Right Now)
- App uses SQLite (fast, local)
- Firebase is optional backup
- Progress persists across sessions ✅

### Deploy to Streamlit Cloud (Later)
- When ready, push to GitHub
- Streamlit Cloud builds automatically
- Firebase keeps user data in sync across devices

---

## Disabling Firebase (Optional)

If you want to disable Firebase at any time:

1. Delete `firebase_config.json`
2. Restart the app
3. App continues working (SQLite only, no cloud sync)

---

## Security Notes

- 🔒 Never share your `firebase_config.json`
- 🔒 It's already in `.gitignore` (won't be pushed to GitHub)
- 🔒 Test mode is safe - only accessible from your apps
- 🔒 No user authentication needed - sessions are anonymous

---

## Questions?

If anything seems unclear, the app works perfectly fine with **just SQLite** - Firebase is optional!

The app will automatically:
- ✅ Work without Firebase
- ✅ Use fast SQLite queries
- ✅ Save progress locally
- ✅ Run on Streamlit Cloud

Firebase just adds cloud sync and multi-session support.

