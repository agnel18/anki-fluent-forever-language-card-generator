---
name: new-analyzer
description: |
  Generate a complete language analyzer for one of the 65 unimplemented languages
  by walking through the 7-phase pipeline in language_grammar_generator/.
  Auto-commits each phase. Blocks at the validation gate per CLAUDE.md
  (85% confidence threshold + 11-check implementation validator + 3-level E2E).

  Invoke as: /new-analyzer <iso-code> [language_name] [family] [script_type] [word_order]
  Examples:
    /new-analyzer pt
    /new-analyzer pt Portuguese Indo-European Latin SVO
    /new-analyzer th Thai Tai-Kadai Thai SVO

  Only the iso-code is required. Anything missing — prompt the user before proceeding.
---

# Generate a new language analyzer

Follow this workflow exactly. The seven phases come from `language_grammar_generator/`.
Auto-commit after every phase. Block at the validation gate. Match the gold standards.

## Step 0 — Inputs and pre-flight

1. **Parse the user's invocation** for: ISO code (required), language name, language family, script type, word order.
2. **Look up missing fields** in `streamlit_app/languages.yaml` (has code + name; family/script/word_order are NOT in there — you'll need to either know them or ask the user).
3. **If any of family/script/word_order are missing** and the language isn't obvious (e.g. you'd guess wrong on Burmese vs Tibetan), **ask the user** with one AskUserQuestion call before proceeding. Do not guess on edge cases.
4. **Compute the folder name**: lowercase, spaces → underscores. Examples: Portuguese → `portuguese`, Chinese (Traditional) → `chinese_traditional`, Tagalog → `tagalog`.
5. **Bail-out checks:**
   - If `languages/{folder_name}/` already exists, abort with a clear message — analyzer already implemented.
   - If `git status` is dirty, abort and tell the user to commit/stash first. We're going to make 7+ commits; a clean baseline matters.
6. **Pick the gold standard reference:**
   - **RTL** (Arabic, Hebrew, Persian, Urdu, Pashto): use `languages/arabic/` as the structural reference.
   - **Everything else**: use `languages/french/` (CLAUDE.md calls it "enterprise gold standard, v2.0, most complete").
   - Quote 2-3 of the reference's `_analyzer.py` methods into your context before generating Phase 3 — you need to copy the patterns, not invent new ones.

## Step 1 — Phase loop

For each phase 1 through 7:

### A. Load the prompt template

Each phase script in `language_grammar_generator/phase{N}_*_prompt.py` exports a constant
named `PHASE{N}_*_PROMPT`. Read the file, extract the constant text. Phase 3 is the most
critical (per CLAUDE.md) — produces all 4 domain components + fallbacks.

### B. Fill placeholders

The templates use `{LANGUAGE_NAME}`, `{LANGUAGE_CODE}`, `{LANGUAGE_FAMILY}`, `{SCRIPT_TYPE}`, `{WORD_ORDER}`. Substitute the values from Step 0.

### C. Generate the artifact

YOU are the AI fulfilling the prompt — produce the artifact directly. Don't shell out to
the project's Gemini API for this; the existing 12 analyzers were built this way.

**Cost note for the user:** generating one full analyzer through Claude costs more than
batching it through Gemini 2.5-flash. If they're budget-constrained and want to do many
languages, suggest they run the prompts manually through aistudio.google.com instead. But
for one-at-a-time interactive generation, doing it here is fine.

For each phase, the expected outputs (per CLAUDE.md):

| Phase | Output |
|---|---|
| 1 | `languages/{folder_name}/{lang_code}_grammar_concepts.md` (research doc) |
| 2 | Complete file tree (17+ files) — empty/skeleton OK at this phase |
| 3 | `domain/{lang_code}_config.py`, `_prompt_builder.py`, `_response_parser.py`, `_validator.py`, `_fallbacks.py` |
| 4 | `infrastructure/{lang_code}_fallbacks.py` + AI service plumbing |
| 5 | `infrastructure/data/grammatical_roles.yaml`, `language_config.yaml`, `patterns.yaml`, `word_meanings.json` |
| 6 | `tests/test_*.py` (full suite) + registry update in `streamlit_app/language_analyzers/analyzer_registry.py` |
| 7 | Documentation + deployment checklist |

### D. Write the files

Use the `Write` tool. For Python files, after writing, run a syntax check:
```
python -c "import ast; ast.parse(open('<path>', encoding='utf-8').read())"
```
If syntax fails, fix it before committing.

### E. Auto-commit

```
git add languages/{folder_name}/
# Phase 6 also touches the registry — add that too:
git add streamlit_app/language_analyzers/analyzer_registry.py
git commit -m "Add {language_name} analyzer — Phase {N}: {phase_name}"
```

Use a HEREDOC for the commit body if you want to add detail. Standard `Co-Authored-By` line per repo convention.

### F. Report and proceed

Print: `Phase {N} ({phase_name}) — committed as {short_sha}, {n} files written`. Move to next phase.

## Step 2 — Critical invariants (apply throughout)

Per CLAUDE.md:
- **Lazy imports**: never `from streamlit_app.shared_utils import ...` at module level in the analyzer. Always import inside `_call_ai()`. Module-level imports break test mocking and cause cross-test contamination.
- **No hardcoded complexity**: read `st.session_state.get("difficulty", "intermediate")` — don't pin a value.
- **Pass through POS labels**: in the analyzer's `_convert_analyzer_output_to_explanations` (or equivalent), preserve the original POS label and color from the analyzer's config — don't re-map through `_map_pos_to_category`.
- **Match Japanese `batch_analyze_grammar` exactly**: returns `List[GrammarAnalysis]` dataclasses, not dicts. The Chinese-Simplified bug in late April 2026 came from violating this. Re-read [languages/japanese/ja_analyzer.py:128-173](languages/japanese/ja_analyzer.py#L128-L173) before writing the new analyzer's batch method.
- **5-level fallback parsing** in `parse_grammar_response`: direct JSON → markdown code block → JSON repair → text pattern → rule-based.
- **External config**: all settings in YAML/JSON in `infrastructure/data/`, not hardcoded.

## Step 3 — Validation gate (per CLAUDE.md, hard block)

After Phase 7, run all three. Stop and report on first failure.

```bash
python language_grammar_generator/validate_implementation.py --language {code} --verbose
python language_grammar_generator/run_all_tests.py --language {code} --coverage
python language_grammar_generator/compare_with_gold_standard.py --language {code} --detailed
```

**Pass criteria:**
- `validate_implementation.py`: all 11 checks pass (file structure, methods, interface vs French, integration, error handling, performance <30s, registry).
- `run_all_tests.py`: tests pass, coverage acceptable (no hard threshold in CLAUDE.md but >70% is reasonable).
- `compare_with_gold_standard.py`: ≥0.85 similarity to French (LTR) or Arabic (RTL).
- The analyzer's own `validate_analysis()` method must return ≥0.85 confidence on the gold-standard test sentences.

**On any failure**: stop. Do NOT push. Print the failure summary and tell the user:
> Validation failed at {check_name}. Run `python language_grammar_generator/validate_implementation.py --language {code} --verbose` to see details. Fix forward, then re-run `/new-analyzer {code} --resume validate`.

(The `--resume` flag is aspirational; for now they just re-run the validation manually until it passes, then run the next step manually.)

## Step 4 — E2E pipeline test (per CLAUDE.md)

CLAUDE.md states: "for each analyzer, all three difficulty levels are covered and validated:
1 beginner sentence, 1 intermediate sentence, 2 advanced sentences."

Run:
```bash
pytest tests/test_end_to_end_pipeline.py -v -s -k {code}
```

Must produce a report at `tests/reports/pipeline_report_{language}.txt` showing all 3 difficulty levels exercised.

If any level is missing or the analyzer falls back to generic AI for any of them, fail the gate.

## Step 5 — Final commit + push

When all validation passes:

1. Update `CLAUDE.md` "Language Analyzers → Status" table: add the new language row with ✅ Implemented (v1.0) — E2E verified.
2. Update the "X implemented out of 77 target languages" count (e.g. 12 → 13).
3. Update the "65 languages remaining" line.
4. Commit:
   ```
   git commit -m "Add {language_name} analyzer — validated, all checks pass"
   ```
5. Push:
   ```
   git push origin main
   ```
6. Report: list of all commits in this run, total LOC added, validation summary, suggested next analyzer (alphabetical from the Open Tasks queue).

## Step 6 — One-line offer for follow-up

End your final reply with: "Want me to /schedule a background agent to run the same flow for the next language in the queue?" — only if validation succeeded and there are languages remaining.

## What you must NOT do

- Do not skip the validation gate "because it's a small change."
- Do not generate Phase 3 from scratch without first reading the gold-standard reference.
- Do not amend earlier commits — keep one commit per phase.
- Do not push if validation failed — leave commits local for fix-forward.
- Do not run multiple analyzers in parallel inside this skill — one at a time. (Use parallel agents at the call site if you want batching.)
