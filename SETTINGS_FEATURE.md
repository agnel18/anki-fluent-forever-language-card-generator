# Settings Feature - Language Learning App

## ⚙️ New Settings Icon

Added a **Settings** button in the top-right corner with a popover containing all adjustable options:

### Available Settings

#### 1. **Difficulty Level** 🎯
- **Options:** Beginner, Intermediate, Advanced
- **Default:** Intermediate
- **Impact:** 
  - Beginner: Simple present tense, common scenarios
  - Intermediate: Mixed tenses, formal/informal, various contexts
  - Advanced: Complex structures, rare vocabulary, literary/academic

#### 2. **Sentence Length** 📏
- **Range:** 4-30 words
- **Default:** 6-16 words
- **Impact:** Controls minimum and maximum sentence length
- **Use Cases:**
  - Beginners: 4-8 words (shorter, easier sentences)
  - Intermediate: 6-16 words (balanced)
  - Advanced: 12-25 words (longer, complex sentences)

#### 3. **Sentences Per Word** 📝
- **Range:** 3-15 sentences
- **Default:** 10 sentences
- **Impact:** How many example sentences to generate per word
- **Use Cases:**
  - Quick deck: 3-5 sentences
  - Standard: 10 sentences
  - Deep learning: 12-15 sentences

#### 4. **Track Progress** ✅
- **Options:** On/Off (checkbox)
- **Default:** On
- **Impact:** 
  - When enabled: Words marked as "completed" after generation
  - Helps you pick up where you left off
  - Shows completed count in word selection
  - "Skip completed" option uses this data

#### 5. **Audio Speed** 🎵
- **Range:** 0.5x - 1.5x
- **Default:** 0.8x (learner-friendly)
- **Impact:** Playback speed of generated audio
- **Recommendations:**
  - Beginners: 0.5-0.7x (slower)
  - Intermediate: 0.8-1.0x
  - Advanced: 1.0-1.5x (normal to fast)

#### 6. **Voice Preview** 🎤
- **Display:** Shows currently selected voice
- **Location:** Set in "Step 4: Audio Settings" below
- **Note:** This is a read-only preview in the settings popup

---

## 📍 Where Settings Appear

### Main Header
```
🌍 Language Learning Anki Deck Generator    [🔐 Change Keys]  [⚙️ Settings]
```

### Settings Popover (Click ⚙️)
```
Global Settings
━━━━━━━━━━━━━━━━━
○ Difficulty
  ○ beginner
  ● intermediate  ← Selected
  ○ advanced

━━━━━━━━━━━━━━━━━
Sentence length (words)
[====|=====|=====]
6           16        30

━━━━━━━━━━━━━━━━━
Sentences per word
[========|====]
3        10       15

━━━━━━━━━━━━━━━━━
☑ Track progress (mark generated words as completed)

━━━━━━━━━━━━━━━━━
Audio speed
[====|====|====]
0.5     0.8     1.5

━━━━━━━━━━━━━━━━━
Voice preview: es-ES-ElviraNeural (Female)
```

---

## 🔄 Settings Persistence

### Session-Based
- Settings persist throughout your browser session
- Closing the tab resets to defaults
- Changing language auto-adjusts voice options

### State Management
All settings stored in `st.session_state`:
```python
st.session_state.difficulty             # "beginner" | "intermediate" | "advanced"
st.session_state.sentence_length_range  # (min, max) tuple
st.session_state.sentences_per_word     # 3-15
st.session_state.track_progress         # True | False
st.session_state.audio_speed            # 0.5-1.5
st.session_state.selected_voice         # "es-ES-ElviraNeural"
st.session_state.selected_voice_display # "es-ES-ElviraNeural (Female)"
```

---

## 🎯 Where Settings Take Effect

### Sentence Generation
- **Difficulty:** Passed to Groq API prompt
- **Sentence Length:** Min/max constraints in generation
- **Sentences Per Word:** Number of sentences to generate

### Audio Generation
- **Audio Speed:** Applied to Edge TTS rate parameter
- **Voice:** Used for TTS synthesis (with Google fallback)

### Progress Tracking
- **Track Progress:** Marks words as completed after successful generation
- **Completed Words:** Used in "Skip completed" and "Continue" options

---

## 📊 Current Settings Display

Below audio controls, see a summary:
```
Difficulty: intermediate, Sentences/word: 10, Length: 6-16 words, Tracking: On
```

---

## 🚀 Usage Example

### Scenario 1: Beginner Spanish Learner
```
Settings:
- Difficulty: Beginner
- Sentence Length: 4-8 words
- Sentences Per Word: 5
- Audio Speed: 0.6x
- Voice: es-ES-ElviraNeural (Female)
- Track Progress: On

Result:
- Short, simple sentences
- Present tense focus
- Slower audio for easier comprehension
- 5 examples per word (quick decks)
```

### Scenario 2: Advanced French Practice
```
Settings:
- Difficulty: Advanced
- Sentence Length: 12-25 words
- Sentences Per Word: 15
- Audio Speed: 1.2x
- Voice: fr-FR-HenriNeural (Male)
- Track Progress: On

Result:
- Complex, literary sentences
- Rare vocabulary, subjunctive mood
- Faster native-like audio
- 15 examples per word (deep immersion)
```

### Scenario 3: Quick Review Deck
```
Settings:
- Difficulty: Intermediate
- Sentence Length: 6-12 words
- Sentences Per Word: 3
- Audio Speed: 1.0x
- Voice: Auto (based on language)
- Track Progress: Off

Result:
- Balanced sentences
- Only 3 examples per word
- Normal speed
- No progress tracking (one-off deck)
```

---

## 🔧 Technical Details

### Code Changes

#### App (app_v3.py)
1. Added session state defaults for all settings
2. Created settings popover in header
3. Bound audio controls to session state
4. Passed settings to generation workflow
5. Added progress tracking after successful generation
6. Display current settings summary

#### Core Functions (core_functions.py)
1. Extended `generate_sentences()` with min/max length and difficulty
2. Extended `generate_sentences_batch()` to accept and pass settings
3. Extended `generate_complete_deck()` to accept settings parameters
4. Properly forward all settings to Groq API

---

## ✅ Testing Checklist

- [x] Settings popover opens/closes correctly
- [x] All sliders and radio buttons work
- [x] Settings persist across page interactions
- [x] Voice changes when language changes
- [x] Audio speed applies to generated audio
- [x] Difficulty affects sentence complexity
- [x] Sentence length range enforced
- [x] Sentences per word generates correct count
- [x] Progress tracking marks completed words
- [x] Settings summary displays correctly
- [x] Syntax validation passes
- [x] App starts without errors

---

## 📝 Notes

### Voice Selection
- Voice is set in "Step 4: Audio Settings" (not in popover)
- Settings popover shows preview only
- This keeps voice selection language-specific

### Progress Tracking
- Only works for frequency list words (not custom CSV uploads)
- Completed words marked after successful ZIP export
- "Skip completed" and "Continue" buttons use this data

### Performance
- Settings have minimal performance impact
- Only sentence generation time affected by difficulty/length
- More sentences per word = proportionally longer generation time

---

## 🎉 Benefits

1. **Flexibility:** Adjust learning pace and complexity
2. **Personalization:** Tailor decks to your level
3. **Efficiency:** Quick decks (3 sentences) or deep learning (15 sentences)
4. **Progress:** Never lose track of what you've generated
5. **Audio Control:** Match your listening comprehension level
6. **Convenience:** All settings in one place

---

## 🔮 Future Enhancements

Potential additions:
- [ ] Save settings profiles (Beginner preset, Advanced preset, etc.)
- [ ] Export settings as JSON
- [ ] Language-specific default settings
- [ ] Context type preferences (academic, casual, business, etc.)
- [ ] Grammar focus (specific tenses, conjugations)
- [ ] Word frequency range presets
