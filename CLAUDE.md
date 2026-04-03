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

### API Setup UI (api_setup.py + settings.py)
Both pages use the same 3-section layout with self-contained instructions:

| Section | Title | Billing | Key Session State |
|---------|-------|---------|-------------------|
| 1 | 🤖 Gemini AI — FREE (no billing needed) | OFF | `google_api_key` |
| 2 | 🔊 Text-to-Speech — FREE (billing for activation only) | ON | `google_tts_api_key` |
| 3 | 🖼️ Pixabay — FREE Images | N/A | `pixabay_api_key` |

- Each section has its own **expander** (setup instructions), **input field**, **Save** and **Test** buttons
- TTS section has nested expanders: "Why a separate project?" and "Set a daily spend limit"
- Status overview is **vertical** (mobile-friendly), not 3-column
- The "Next" / proceed button **requires all 3 keys** — no partial setup
- Settings page additionally persists keys to `.env` file
- Streamlit widget keys: `google_api_key_input` / `google_tts_api_key_input` / `pixabay_api_key_input` (api_setup), `google_key_input` / `google_tts_key_input` / `pixabay_key_input` (settings)
- Input fields have **visible borders** via CSS: `border: 1px solid var(--card-border)` in `theming.py`

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

> **⚠️ KNOWN ISSUE — Model config was DUPLICATED** in `config/models.py` AND `shared_utils.py`. **RESOLVED:** `config/models.py` deleted (was dead code — nothing imported from it). `shared_utils.py` is the sole canonical source. `content_generator.py` imports from `shared_utils`.

---

## ⛔ CRITICAL — GCP Single Project Billing Trap

### The Problem
**Enabling a Billing Account for ANY API in a GCP project automatically upgrades ALL APIs in that project to the Paid Tier.** This means:

1. You enable billing to use Cloud Text-to-Speech (TTS requires billing)
2. This silently upgrades Generative Language API (Gemini) to paid tier
3. Gemini **loses its free tier RPD limit** and starts charging per request
4. A single batch generation can burn through ₹600+ unexpectedly

### Current State (as of commit 03f08db)
- The app **requires** two separate GCP projects — both keys are mandatory
- **Project A ("Language Cards - Gemini"):** Gemini only, NO billing → free tier preserved (1,500 RPD)
- **Project B ("Language Cards - TTS"):** TTS only, billing enabled → **FREE within 1M characters/month** (Standard voices)
- Both keys entered on the **API Setup** page in dedicated sections (Gemini section + TTS section)
- **No fallback:** TTS will NOT fall back to the Gemini key. `api_keys.py` has `required: True` for TTS. `audio_generator.py` only checks `google_tts_api_key` session state and `GOOGLE_TTS_API_KEY` env var.
- TTS is **FREE** — billing is required only to *activate* the API, not because it costs money

### Alternative (single project, NOT recommended)
- Enable billing (required for TTS) → Gemini loses free tier
- Set per-minute rate limit on `GenerateContent requests per minute` in Cloud Console (e.g., 15 RPM)
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
**9 implemented** out of 77 target languages:

| Language | Code | Folder | Status |
|----------|------|--------|--------|
| Arabic | `ar` | `languages/arabic/` | ✅ Implemented |
| Chinese (Simplified) | `zh` | `languages/chinese_simplified/` | ✅ Implemented |
| Chinese (Traditional) | `zh-tw` | `languages/chinese_traditional/` | ✅ Implemented |
| French | `fr` | `languages/french/` | ✅ Gold standard (v2.0) |
| German | `de` | `languages/german/` | ✅ Implemented |
| Hindi | `hi` | `languages/hindi/` | ✅ Implemented |
| Japanese | `ja` | `languages/japanese/` | ✅ Implemented (v1.0) |
| Spanish | `es` | `languages/spanish/` | ✅ Implemented |
| Turkish | `tr` | `languages/turkish/` | ✅ Fully implemented |

**68 languages remaining** — basic deck generation (TTS, frequency lists, translations) works for all 77 without an analyzer. Analyzers add grammar-colored sentence overlays with word-by-word explanations.

### Gold Standards

| Reference | Language | Folder | Use As |
|-----------|----------|--------|--------|
| **Primary** | French v2.0 | `languages/french/` | Enterprise gold standard — most complete, all patterns |
| **Secondary** | Chinese Simplified | `languages/chinese_simplified/` | Clean architecture reference |

#### Direction-Based Gold Standard Selection

| Direction | Gold Standard | Use For |
|-----------|--------------|---------|
| **LTR** | French v2.0 | All LTR languages (Spanish, German, Japanese, Korean, Hungarian, etc.) |
| **RTL** | Arabic | All RTL languages (Hebrew, Persian, Urdu, Pashto) |

> **Note:** Japanese is **LTR** (horizontal) or top-to-bottom vertical — it is NOT RTL. Use French as gold standard for Japanese, Korean, and Hungarian.

```
languages/french/
├── fr_analyzer.py                  # Main facade (orchestrates all components)
├── fr_grammar_concepts.md          # Grammar reference (Phase 1 output)
├── domain/
│   ├── fr_config.py                # Language config, roles, colors, templates
│   ├── fr_prompt_builder.py        # AI prompt construction (Jinja2-based)
│   ├── fr_response_parser.py       # Parse AI responses (5-level JSON fallback)
│   ├── fr_validator.py             # Validation (85% threshold, natural scoring)
│   └── fr_fallbacks.py             # Rule-based fallback analysis
├── infrastructure/data/            # External YAML/JSON config files
└── tests/                          # Full test suite (13 test files)
```

### Creating New Analyzers — 7-Phase Process

All tooling lives in `language_grammar_generator/`. Each phase script exports a **prompt template constant** (e.g., `PHASE1_RESEARCH_PROMPT`) — these are NOT CLI tools. The orchestrator `language_analyzer_creation_guide.py` imports them and fills placeholders (`{LANGUAGE_NAME}`, `{LANGUAGE_CODE}`, `{LANGUAGE_FAMILY}`, `{SCRIPT_TYPE}`, `{WORD_ORDER}`). You feed the generated prompts to Gemini to produce implementation artifacts.

| Phase | Script | Constant | Output Artifact |
|-------|--------|----------|-----------------|
| 1. Research | `phase1_research_prompt.py` | `PHASE1_RESEARCH_PROMPT` | `{lang}_grammar_concepts.md` — linguistic research doc |
| 2. Directory | `phase2_directory_structure_prompt.py` | `PHASE2_DIRECTORY_PROMPT` | Complete file tree (17+ files) |
| 3. Domain ⭐ | `phase3_domain_components_prompt.py` | `PHASE3_DOMAIN_COMPONENTS_PROMPT` | Config, PromptBuilder, ResponseParser, Validator, Fallbacks |
| 4. Infrastructure | `phase4_infrastructure_prompt.py` | `PHASE4_INFRASTRUCTURE_PROMPT` | AI service, circuit breaker, caching |
| 5. Configuration | `phase5_configuration_files_prompt.py` | `PHASE5_CONFIGURATION_PROMPT` | External YAML/JSON config files |
| 6. Testing | `phase6_testing_integration_prompt.py` | `PHASE6_TESTING_INTEGRATION_PROMPT` | Full test suite + registry integration |
| 7. Deployment | `phase7_documentation_deployment_prompt.py` | `PHASE7_DOCUMENTATION_DEPLOYMENT_PROMPT` | Documentation + deployment checklists |

**Phase 3 is the most critical** — produces all 4 core domain components + fallbacks.

### Key Requirements for New Analyzers

| Requirement | Details |
|------------|--------|
| **Base Class** | Inherit from `BaseGrammarAnalyzer` (ABC) in `base_analyzer.py` |
| **4 Abstract Methods** | `get_grammar_prompt(complexity, sentence, target_word) -> str` | 
| | `parse_grammar_response(ai_response, complexity, sentence) -> Dict` |
| | `get_color_scheme(complexity) -> Dict[str, str]` |
| | `validate_analysis(parsed_data, original_sentence) -> float` (0.0–1.0) |
| **85% Quality Threshold** | `validate_analysis()` must return ≥ 0.85 for production deployment |
| **Natural Scoring** | Confidence 0.0–1.0, NO artificial boosting |
| **External Config** | All settings in YAML/JSON files in `infrastructure/data/` — never hardcoded |
| **Registration** | Add `folder_name → language_code` in `analyzer_registry.py` `folder_to_code` dict |
| **Clean Architecture** | `domain/` (business logic) → `infrastructure/` (external concerns) → `tests/` |
| **5-Level Fallback Parsing** | Direct JSON → Markdown code block → JSON repair → Text pattern → Rule-based |

**17 required files per analyzer** (checked by `validate_implementation.py`):
```
{lang}_analyzer.py, {lang}_grammar_concepts.md,
domain/__init__.py, domain/{lang}_config.py, domain/{lang}_prompt_builder.py,
domain/{lang}_response_parser.py, domain/{lang}_validator.py,
infrastructure/__init__.py, infrastructure/{lang}_fallbacks.py,
tests/__init__.py, tests/conftest.py, tests/test_{lang}_analyzer.py,
tests/test_{lang}_config.py, tests/test_{lang}_prompt_builder.py,
tests/test_{lang}_response_parser.py, tests/test_{lang}_validator.py,
tests/test_integration.py
```

### Validation & Testing Tools

| Tool | Purpose | CLI |
|------|---------|-----|
| `validate_implementation.py` | 11 checks: file structure, method completeness, interface compliance vs French, component integration, error handling, performance (<30s), registry | `--language {code}`, `--verbose`, `--all-languages` |
| `run_all_tests.py` | Unit + integration + gold standard tests | `--language {code}`, `--coverage`, `--parallel`, `--all-languages` |
| `compare_with_gold_standard.py` | Compare against French/Chinese reference implementations | `--language {code}`, `--detailed`, `--export-results`, `--reference fr` |

```bash
# Example: validate and test a new Portuguese analyzer
python language_grammar_generator/validate_implementation.py --language pt --verbose
python language_grammar_generator/run_all_tests.py --language pt --coverage
python language_grammar_generator/compare_with_gold_standard.py --language pt --detailed
```

### Language Family Guides

Located in `language_grammar_generator/language_family_guides/`:

| Guide | Languages | Key Patterns |
|-------|-----------|-------------|
| `indo_european.md` | Spanish, French, German, Hindi, Russian, etc. | Fusional morphology, SVO word order, gender/case systems |
| `sino_tibetan.md` | Chinese (Simplified/Traditional), Tibetan, Burmese | Analytic (no inflection), character-based analysis, external `word_meanings.json` |

> **⚠️ Missing guides:** `afro_asiatic.md` (Arabic, Hebrew) and `agglutinative.md` (Turkish, Japanese, Korean) are referenced in the README but **don't exist yet**.

### Templates

22 parameterized template files in `language_grammar_generator/templates/` — includes analyzer skeleton, config, prompt builder, response parser, validator, fallbacks, circuit breaker, AI service, test templates, `grammatical_roles.yaml`, `language_config.yaml`, `patterns.yaml`, `word_meanings.json`. See `templates/README.md` for usage.

### Data Classes
- `GrammarAnalysis` — result with sentence, target_word, language_code, complexity_level, grammatical_elements, explanations, color_scheme, html_output, confidence_score, word_explanations, is_rtl, text_direction
- `LanguageConfig` — code, name, native_name, family, script_type, complexity_rating, key_features, supported_complexity_levels

---

## TTS Configuration

- **API:** Google Cloud Text-to-Speech REST API at `texttospeech.googleapis.com`
- **SDK:** Import available but disabled (`GOOGLE_TTS_SDK_AVAILABLE = False`), REST preferred
- **Free tier:** 1 million characters/month (Standard voices), 1M WaveNet, 1M Neural2. App uses Standard.
- **API key resolution order (no Gemini fallback):**
  1. `config.api_keys.get_api_key('text_to_speech', st.session_state)` — checks `google_tts_api_key` only
  2. `st.session_state.get("google_tts_api_key")`
  3. `os.getenv("GOOGLE_TTS_API_KEY")`
- **Voice mappings:** 77 languages with TTS voices defined in `streamlit_app/languages.yaml`
- **Default params:** MP3 encoding, speaking_rate=1.0, pitch=0.0

---

## Error Handling

### Exception Hierarchy (`error_recovery.py`)
```
APIError (base)
├── NetworkError          — connectivity/timeout
├── APIQuotaError         — rate limit / quota exceeded
├── APIAuthError          — authentication (401/403)
└── APIServerError        — server-side (5xx)
```

### Retry Mechanism
- **Decorator:** `retry_with_exponential_backoff` — 3 retries, base_delay=1s, max_delay=60s, backoff_factor=2.0, jitter ±50%
- **Retryable errors:** `rate limit`, `timeout`, `connection`, `network`, `temporary`, `429`, `503`, `502`
- Applied to all Gemini API calls and TTS requests

### User-Facing Error Messages

| Location | Trigger | Message |
|----------|---------|--------|
| **Global handler** (`app_v3.py` ~L278) | Any uncaught exception | "Application Error" + expandable traceback + Refresh/Home buttons |
| **Generation page** (`generating.py` ~L830) | API errors during generation | "API Issues Detected" + "Go to API Settings" button |
| **Generation page** | Audio generation fails | "Audio will be skipped (cards still work)" |
| **Generation page** | Image generation fails | "Images will be skipped (cards still work)" |
| **Generation page** | Any partial failure | "Retry with Safer Settings" button (reduces sentences per word) |
| **Statistics page** (`statistics.py` ~L84) | Gemini quota ≥ 100% | 🚫 "Daily Quota Reached — paused" + Cloud Console link |
| **Statistics page** | Gemini quota ≥ 80% | ⚠️ "You've used X of Y daily requests" + rate limit advice |
| **Statistics page** | Free tier exceeded | ⚠️ "You're now paying for Gemini API usage" |

### Graceful Degradation
- **Audio/image failures never block card generation** — cards are always produced
- Primary model → fallback model → AI repair → fallback response (never crash)
- Content generation: `generate() → parse() → validate() → _repair_with_ai() → re-parse`

> **Known gap:** TTS quota exhaustion silently returns `False` in `audio_generator.py` — no explicit user message. Cards still generate without audio.

---

## Open Tasks

1. **Grammar analyzers for 68 remaining languages** — Use the 7-phase process in `language_grammar_generator/`. Run `validate_implementation.py`, `run_all_tests.py`, and `compare_with_gold_standard.py` to verify. French v2.0 and Chinese Simplified are gold standard references.
2. **Missing language family guides** — `afro_asiatic.md` (Arabic, Hebrew) and `agglutinative.md` (Turkish, Japanese, Korean) referenced in `language_grammar_generator/README.md` but not created.
3. **AI repair pipeline verification** — `_repair_with_ai()` implemented in content_generator.py. Needs systematic verification across all 9 language outputs to confirm repair quality.
4. ~~**TTS silent failure**~~ — **RESOLVED.** `audio_generator.py` now shows `st.warning()` for missing API key, timeout, quota exhaustion, auth failure. Uses `tts_warning_shown` session flag to avoid spam.
5. **Social media posts** — Not yet implemented.
6. **Razorpay payment** — Currently a simple redirect link in `payment.py`. No server-side API integration, no webhook handling.
7. ~~**Model config duplication**~~ — **RESOLVED.** `config/models.py` deleted (was dead code — nothing imported from it). `shared_utils.py` is the sole canonical source. `content_generator.py` imports from `shared_utils`.
8. **.gitignore encoding** — Last 2 entries (`ARCHIVED_PHASES.md`, `repo_backup_pre_cleanup/`) were appended in UTF-16LE encoding. Rest of file is ASCII/UTF-8. May cause Git to not ignore those entries on some systems.
9. **API key retrieval duplication** — Key retrieval logic duplicated across `audio_generator.py`, `state_manager.py`, `api_setup.py`, `sync_manager.py`. Each has slightly different needs (startup vs runtime vs UI vs sync). Documented tech debt — centralizing risks breaking the delicate fallback chains. Address when building the next major feature.

---

## Key File Reference

| File | Purpose |
|------|---------|
| `streamlit_app/app_v3.py` | Main entry point, routing, global CSS |
| `streamlit_app/constants.py` | All app constants, rate limits, page names, session keys |
| `streamlit_app/shared_utils.py` | Canonical model config, cache, retry utilities, exceptions |
| `streamlit_app/router.py` | Page routing via session state (dict dispatch + importlib) |
| `streamlit_app/services/generation/content_generator.py` | Gemini content generation, AI repair mechanism |
| `streamlit_app/services/generation/generation_orchestrator.py` | Orchestrates batch generation workflow |
| `streamlit_app/audio_generator.py` | Google Cloud TTS integration (REST API, no Gemini key fallback) |
| `streamlit_app/language_analyzers/analyzer_registry.py` | Auto-discovery of language analyzers from `languages/` directory |
| `streamlit_app/language_analyzers/base_analyzer.py` | BaseGrammarAnalyzer ABC, GrammarAnalysis/LanguageConfig dataclasses |
| `streamlit_app/error_recovery.py` | Retry decorators, custom exception hierarchy |
| `streamlit_app/payment.py` | Razorpay.me redirect (18 lines) |
| `streamlit_app/config/api_keys.py` | Centralized API key config — TTS required=True, no fallback |
| `streamlit_app/ui/theming.py` | Theme-aware CSS — dark/light mode, visible input borders |
| `streamlit_app/languages.yaml` | 77 languages: codes, TTS voices, frequency list mappings, UI translations |
| `streamlit_app/page_modules/api_setup.py` | API key setup — 3 dedicated sections (Gemini, TTS, Pixabay) |
| `streamlit_app/page_modules/statistics.py` | Usage dashboard with quota health warnings (80%/100%) |
| `languages/french/` | Gold standard analyzer implementation (v2.0, primary reference) |
| `languages/turkish/` | Fully implemented analyzer (clean architecture) |
| `language_grammar_generator/` | 7-phase prompt templates + orchestrator for creating new analyzers |
| `language_grammar_generator/language_analyzer_creation_guide.py` | Orchestrator — imports all phase prompts, fills placeholders per-language |
| `language_grammar_generator/validate_implementation.py` | 11-check implementation validator (files, methods, interface, performance) |
| `language_grammar_generator/run_all_tests.py` | Test runner with coverage reporting |
| `language_grammar_generator/compare_with_gold_standard.py` | Gold standard comparison (vs French/Chinese reference) |
| `language_grammar_generator/language_family_guides/` | Language family implementation guides (Indo-European, Sino-Tibetan) |
| `language_grammar_generator/templates/` | 22 parameterized template files for analyzer scaffolding |
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
- **API keys:** Gemini in `st.session_state.google_api_key`, TTS in `st.session_state.google_tts_api_key` — both required, no fallback between them
- **Testing:** pytest; language-specific tests live in `languages/{lang}/tests/`; root-level test files for cross-cutting concerns
- **Frequency lists:** Excel files in `77 Languages Frequency Word Lists/`, mapped via `languages.yaml`
