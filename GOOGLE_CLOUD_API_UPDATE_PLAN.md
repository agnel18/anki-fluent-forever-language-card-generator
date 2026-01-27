# Google Cloud API Setup Update Plan

## Overview
Update the app to use a single Google Cloud API key with access to exactly two services:
- **Gemini API** (AI text generation)
- **Cloud Text-to-Speech API** (audio generation)

This replaces the current confusing multi-API approach with a clear, single-key solution.

## Current Issues
1. Multiple API sections confuse users
2. Inconsistent API naming (Generative Language vs Gemini)
3. No API key restriction instructions
4. Separate status tracking for different services

## Target State
- Single "Google Cloud APIs" section
- One API key input field
- Clear instructions for enabling exactly 2 APIs
- API key restriction guidance for security
- Unified status tracking

## Implementation Plan

### Phase 1: Update api_setup.py (Primary Setup Page)

#### 1.1 Update Section Title
```python
# Current: "### 🤖 Gemini AI API (AI Generation & Audio)"
# New: "### ☁️ Google Cloud APIs (AI Generation & Audio)"
```

#### 1.2 Update Header Description
```python
# Current: "*Configure Gemini AI API for AI generation and Google Cloud Text-to-Speech for audio*"
# New: "*Configure a single Google Cloud API key with access to Gemini API and Cloud Text-to-Speech API*"
```

#### 1.3 Simplify API Enablement Instructions
Replace the current confusing list with:
```
**Enable exactly these two APIs in Google Cloud Console:**

1. **Gemini API** - For AI text generation and translations
2. **Cloud Text-to-Speech API** - For audio generation

[!IMPORTANT]
Do NOT enable other Google Cloud APIs unless you specifically need them for other projects.
```

#### 1.4 Add API Key Restriction Section
Add new expandable section:
```
### 🔒 API Key Security (CRITICAL)

**Restrict your API key to prevent unauthorized usage and reduce security risks:**

1. **Go to** [Google Cloud Console](https://console.cloud.google.com/)
2. **Navigate to** "APIs & Services" → "Credentials"
3. **Click on your API key** to edit it
4. **Under "API restrictions":**
   - Select **"Restrict key"**
   - Check ONLY these two APIs:
     - ✅ **Gemini API**
     - ✅ **Cloud Text-to-Speech API**
5. **Click "Save"**

[!WARNING]
An unrestricted API key can be used for expensive Google Cloud services like GPUs, Maps, or other APIs. Always restrict your keys!
```

#### 1.5 Update Status Display
Change from separate Gemini/TTS status to unified:
```python
# Current: Separate checks for Gemini and TTS
# New: Single "Google Cloud APIs" status
if google_key:
    st.success("✅ **Google Cloud APIs** - Configured")
else:
    st.error("❌ **Google Cloud APIs** - Required")
```

### Phase 2: Update settings.py (Settings Page)

#### 2.1 Combine API Sections
Replace separate Gemini and TTS sections with single:
```python
# Replace:
# "### 🔗 Google Gemini API (AI Generation)"
# "### 🔊 Google Cloud Text-to-Speech API (Audio Generation)"

# With:
### ☁️ Google Cloud APIs (Gemini + Text-to-Speech)
```

#### 2.2 Update Setup Instructions
Consolidate instructions to match api_setup.py approach.

#### 2.3 Update Status Overview
Change the top status display to show unified Google Cloud status.

### Phase 3: Update main.py (Main Page)

#### 3.1 Update API Check Logic
Modify the API validation to check for single Google Cloud key instead of separate Gemini/TTS checks.

#### 3.2 Update Error Messages
Change error messages to reference "Google Cloud APIs" instead of separate services.

### Phase 4: Testing & Validation

#### 4.1 Test Scenarios
- Fresh API setup with restrictions
- Existing unrestricted keys
- Invalid API configurations
- Error handling for missing APIs

#### 4.2 User Experience Validation
- Clarity of instructions
- Single API key concept
- Security warnings visibility

## Files to Modify
1. `streamlit_app/page_modules/api_setup.py` - Primary changes
2. `streamlit_app/page_modules/settings.py` - Secondary changes
3. `streamlit_app/page_modules/main.py` - Minor updates

## Success Criteria
- Users see one clear API setup section
- Instructions mention exactly 2 APIs to enable
- API key restriction instructions are prominent
- Status shows unified "Google Cloud APIs" state
- No user confusion about multiple keys/services</content>
<parameter name="filePath">GOOGLE_CLOUD_API_UPDATE_PLAN.md