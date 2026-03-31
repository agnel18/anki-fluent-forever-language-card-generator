# CLAUDE.md — Project Context for AI Assistants

> **This file is .gitignored.** It contains internal project context, not public documentation.

---

## Project Overview

**Language Card Generator v3** — A Streamlit web app that generates Anki flashcard decks for **77 languages** using Google Gemini AI for content generation, Google Cloud TTS for audio, and Pixabay for images.

- **Entry point:** `streamlit run streamlit_app/app_v3.py`
- **Stack:** Streamlit, Google Gemini API (`google-genai`), Google Cloud TTS (REST), genanki (Anki decks), Firebase (optional cloud sync), SQLite (local storage)
- **22 page modules**, session-state routing, 2 service layers (generation + sentence_generation)
- **Payment:** Simple Razorpay.me redirect (`razorpay.me/@agneljosephn`) — no server-side API integration
- **Hosting:** Streamlit Community Cloud (free tier)

---

## Architecture

### Routing
`app_v3.py` → `router.route_to_page()` via `st.session_state.page`. No Streamlit multi-page app — all routing is session-state-based.

### Content Generation Pipeline
```
generate() → parse() → validate() → if failures → _repair_with_ai() → re-parse → return if improved
```
- **ContentGenerator** class in `services/generation/content_generator.py`
- `_repair_with_ai()` uses **temperature=0.4** (lower than 0.7 generation) for deterministic repair
- Repair only accepted if it **reduces** the failure count
- Structured output format: `MEANING:`, `RESTRICTIONS:`, `SENTENCES:`, `TRANSLATIONS:`, `IPA:/PINYIN:/ROMANIZATION:`, `KEYWORDS:`

### Error Handling Pattern
```
Primary model → Fallback model → AI repair → Fallback response (graceful degradation)
```
- `retry_with_exponential_backoff` decorator (3 retries, base_delay=1s, max_delay=60s, jitter)
- Custom exception hierarchy: `APIError` → `NetworkError`, `APIQuotaError`, `APIAuthError`, `APIServerError`

### Import Pattern
Try/except import fallbacks throughout the codebase for graceful degradation when optional dependencies are missing.

---

## Model Configuration

| Role | Model | Free Tier | Paid Price |
|------|-------|-----------|------------|
| **Primary** | `gemini-2.5-flash` | ~1,500 RPD | $0.30/1M input, $2.50/1M output |
| **Fallback** | `gemini-3-flash-preview` | More restrictive | $0.50/1M input, $3.00/1M output |

**Deprecated models** (do NOT use):
- `gemini-2.0-flash`, `gemini-2.0-flash-lite` — shut down June 1, 2026
- `gemini-3-pro-preview` — **SHUT DOWN March 9, 2026**
- `gemini-1.5-flash` — legacy

**Environment overrides:** `GEMINI_MODEL`, `GEMINI_FALLBACK_MODEL`

**Generation params:** max_tokens=20000, temperature=0.7, top_p=0.8, top_k=40

**Rate limits (constants.py):**
- `GEMINI_CALL_LIMIT = 1500` (~1,500 RPD, resets at midnight Pacific Time)
- `GEMINI_TOKEN_LIMIT = 3,000,000`
- `GOOGLE_SEARCH_CALL_LIMIT = 100`

**Official docs:**
- Pricing: https://ai.google.dev/gemini-api/docs/pricing
- Rate limits: https://aistudio.google.com/rate-limit
- Models: https://ai.google.dev/gemini-api/docs/models

> **⚠️ KNOWN ISSUE — Model config is DUPLICATED** in `config/models.py` AND `shared_utils.py`. The `content_generator.py` imports from `shared_utils`, not `config/models.py`. Both must be kept in sync. This is tech debt.

---

## ⛔ CRITICAL — GCP Single Project Billing Trap

### The Problem
**Enabling a Billing Account for ANY API in a GCP project automatically upgrades ALL APIs in that project to the Paid Tier.** This means:

1. You enable billing to use Cloud Text-to-Speech (TTS requires billing)
2. This silently upgrades Generative Language API (Gemini) to paid tier
3. Gemini **loses its free tier RPD limit** and starts charging per request
4. A single batch generation can burn through ₹600+ unexpectedly

### Current State
- The app guides users to create **two separate GCP projects** (API Setup page)
- **Project A ("Language Cards - Gemini"):** Gemini only, NO billing → free tier preserved (1,500 RPD)
- **Project B ("Language Cards - TTS"):** TTS only, billing enabled → pay only for audio
- The `GOOGLE_TTS_API_KEY` env var (in `audio_generator.py`) should be set to Project B's key
- Users who skip the two-project setup and use a single key will still work, but risk losing Gemini's free tier

### Proposed Solutions
1. **Two separate GCP projects** (recommended):
   - Project A: Gemini only, NO billing → free tier preserved
   - Project B: TTS only, billing enabled → pay only for audio
   - Set `GOOGLE_TTS_API_KEY` env var to Project B's key
2. **Single project with per-minute rate limits:**
   - Enable billing (required for TTS)
   - Set per-minute rate limit on `GenerateContent requests per minute` in Cloud Console → APIs & Services → Generative Language API → Quotas & System Limits (e.g., 15 RPM)
   - Set `Characters synthesized per day` for TTS cost control

### GCP Quota Confusion
GCP has **1,700+ quotas** in the dashboard. Key facts:
- **There is NO daily request quota for regular Gemini calls.** Daily quotas only exist for Search and Map Grounding features.
- **Gemini:** `GenerateContent requests per minute` (per-model RPM limit — the only rate control available for regular calls)
- **TTS:** `Characters synthesized per day` (under Cloud Text-to-Speech API)
- The quota names containing "with Search functionality enabled" or "with Map Grounding enabled" are NOT for regular generation calls

---

## Language Analyzers

### Status
**8 implemented** out of 77 target languages:

| Language | Code | Folder | Status |
|----------|------|--------|--------|
| Arabic | `ar` | `languages/arabic/` | ✅ Implemented |
| Chinese (Simplified) | `zh` | `languages/chinese_simplified/` | ✅ Implemented |
| Chinese (Traditional) | `zh-tw` | `languages/chinese_traditional/` | ✅ Implemented |
| French | `fr` | `languages/french/` | ✅ Gold standard |
| German | `de` | `languages/german/` | ✅ Implemented |
| Hindi | `hi` | `languages/hindi/` | ✅ Implemented |
| Spanish | `es` | `languages/spanish/` | ✅ Implemented |
| Turkish | `tr` | `languages/turkish/` | ✅ Fully implemented |

**69 languages remaining** — basic deck generation (TTS, frequency lists, translations) works for all 77 without an analyzer. Analyzers add grammar analysis overlays.

### Gold Standard: French
```
languages/french/
├── fr_analyzer.py                  # Main facade
├── fr_grammar_concepts.md          # Grammar reference
├── domain/
│   ├── fr_config.py                # Language configuration
│   ├── fr_prompt_builder.py        # AI prompt construction
│   ├── fr_response_parser.py       # Parse AI responses
│   ├── fr_validator.py             # Validation (85% threshold)
│   └── fr_fallbacks.py             # Fallback logic
├── infrastructure/data/            # Static data files
└── tests/                          # Full test suite (13 test files)
```

### Creating New Analyzers
1. Templates in `language_grammar_generator/templates/` — parameterized scaffolding
2. 7-phase creation process documented in `language_grammar_generator/`
3. Base class: `BaseGrammarAnalyzer` (ABC) — requires:
   - `get_grammar_prompt(complexity, sentence, target_word) -> str`
   - `parse_grammar_response()` — parse AI response into structured data
   - `get_color_scheme()` — color scheme for grammatical elements
   - `validate_analysis()` — must meet **85% quality threshold**
4. Registration: add `folder_name → language_code` mapping in `analyzer_registry.py` `folder_to_code` dict

### Data Classes
- `GrammarAnalysis` — result with sentence, target_word, language_code, complexity_level, grammatical_elements, explanations, color_scheme, html_output, confidence_score, word_explanations, is_rtl, text_direction
- `LanguageConfig` — code, name, native_name, family, script_type, complexity_rating, key_features, supported_complexity_levels

---

## TTS Configuration

- **API:** Google Cloud Text-to-Speech REST API at `texttospeech.googleapis.com`
- **SDK:** Import available but disabled (`GOOGLE_TTS_SDK_AVAILABLE = False`), REST preferred
- **API key resolution order:**
  1. `config.api_keys.get_api_key('text_to_speech', st.session_state)`
  2. `st.session_state.get("google_api_key")`
  3. `os.getenv("GOOGLE_TTS_API_KEY")` ← **use this for separate TTS project**
  4. `os.getenv("GOOGLE_API_KEY")`
- **Voice mappings:** 77 languages with TTS voices defined in `streamlit_app/languages.yaml`
- **Default params:** MP3 encoding, speaking_rate=1.0, pitch=0.0

---

## Open Tasks

1. **Daily generation quota** — Per-minute rate limit UX guidance implemented across api_setup, settings, statistics, help pages. Two-project approach recommended (Gemini free + TTS billed). Note: Google does NOT offer a daily request quota for regular Gemini calls — only RPM limits exist.
2. **Grammar analyzers for 69 remaining languages** — Use `language_grammar_generator/` templates. French and Turkish are reference implementations.
3. **AI repair pipeline verification** — `_repair_with_ai()` implemented in content_generator.py. Needs systematic verification across all 8 language outputs to confirm repair quality.
4. **Social media posts** — Not yet implemented.
5. **Razorpay payment** — Currently a simple redirect link in `payment.py`. No server-side API integration, no webhook handling.
6. **Model config duplication** — `shared_utils.py` and `config/models.py` both define `GEMINI_MODELS` independently. Risk of drift. content_generator uses shared_utils.
7. **.gitignore encoding** — Last 2 entries (`ARCHIVED_PHASES.md`, `repo_backup_pre_cleanup/`) were appended in UTF-16LE encoding. Rest of file is ASCII/UTF-8. May cause Git to not ignore those entries on some systems.

---

## Key File Reference

| File | Purpose |
|------|---------|
| `streamlit_app/app_v3.py` | Main entry point, routing, global CSS |
| `streamlit_app/constants.py` | All app constants, rate limits, page names, session keys |
| `streamlit_app/shared_utils.py` | Model config (duplicate), cache, retry utilities, exceptions |
| `streamlit_app/config/models.py` | Canonical model config (but content_generator uses shared_utils) |
| `streamlit_app/router.py` | Page routing via session state |
| `streamlit_app/services/generation/content_generator.py` | Gemini content generation, AI repair mechanism |
| `streamlit_app/services/generation/generation_orchestrator.py` | Orchestrates batch generation workflow |
| `streamlit_app/audio_generator.py` | Google Cloud TTS integration (REST API) |
| `streamlit_app/language_analyzers/analyzer_registry.py` | Auto-discovery of language analyzers from `languages/` directory |
| `streamlit_app/language_analyzers/base_analyzer.py` | BaseGrammarAnalyzer ABC, GrammarAnalysis/LanguageConfig dataclasses |
| `streamlit_app/error_recovery.py` | Retry decorators, custom exception hierarchy |
| `streamlit_app/payment.py` | Razorpay.me redirect (18 lines) |
| `streamlit_app/languages.yaml` | 77 languages: codes, TTS voices, frequency list mappings, UI translations |
| `streamlit_app/page_modules/api_setup.py` | API key setup with hard quota instructions |
| `streamlit_app/page_modules/statistics.py` | Usage dashboard with quota health warnings (80%/100%) |
| `languages/french/` | Gold standard analyzer implementation |
| `languages/turkish/` | Fully implemented analyzer (clean architecture) |
| `language_grammar_generator/` | Templates and 7-phase guides for creating new analyzers |
| `requirements.txt` | Python dependencies (streamlit, google-genai, genanki, etc.) |

---

## Coding Conventions

- **Routing:** Session-state based (`st.session_state.page`), not Streamlit multi-page app
- **Imports:** Try/except fallbacks throughout for graceful degradation
- **Error pattern:** Primary → fallback → repair → fallback response (never crash)
- **Language analyzers:** Clean architecture — `domain/` (config, prompt_builder, response_parser, validator) + `infrastructure/data/` + `tests/`
- **AI output format:** Structured sections (`MEANING:`, `RESTRICTIONS:`, `SENTENCES:`, `TRANSLATIONS:`, `IPA:`, `KEYWORDS:`)
- **Constants:** Centralized in `constants.py` but some duplicated in `shared_utils.py` — always update both
- **Environment:** `.env` files loaded from both project root AND `streamlit_app/` directory
- **API keys:** Stored in `st.session_state.google_api_key`; shared between Gemini and TTS unless `GOOGLE_TTS_API_KEY` is set
- **Testing:** pytest; language-specific tests live in `languages/{lang}/tests/`; root-level test files for cross-cutting concerns
- **Frequency lists:** Excel files in `77 Languages Frequency Word Lists/`, mapped via `languages.yaml`
