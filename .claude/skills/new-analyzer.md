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

## Step -1 — Cost-aware session setup (do this FIRST, before anything else)

Real-measured cost data from the Portuguese smoke test (token-dashboard, 2026-05-02):

| Approach | $/analyzer |
|---|---:|
| Long Opus 4.7 session, no /clear between analyzers | **~$73** |
| Add `/clear` between analyzers (drops cumulative cache reads) | ~$45 |
| **+ Sonnet 4.6 orchestrator** | **~$25** |

Cache reads on a long Opus session were $37 of $73 on Portuguese — that's the single biggest line item, and `/clear` zeroes it. The skill, the agent file, the per-phase YAML, and CLAUDE.md all reload after `/clear`, so nothing important is lost.

**Run these two slash commands at the start of each new analyzer:**

```
/clear
/model sonnet
```

Then `/new-analyzer <code>`. The orchestrator only does file I/O, AST parsing, git, and agent dispatch — Sonnet handles all of that fine. Subagents still use the per-phase tier from `phase_model_tiers.yaml` (Opus on P1+P3, Sonnet on P4+P6+P8, Haiku on P2+P5+P7) regardless of orchestrator model. Switch back to Opus 4.7 ad-hoc only if you hit a novel error the Sonnet orchestrator can't reason through.

Across the remaining 63 analyzers, applying both commands cuts the queue cost from ~$4,600 → ~$1,580.

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
7. **Read the phase-tier table** at `language_grammar_generator/phase_model_tiers.yaml`. Build an in-memory map `{phase_number: tier}` from the `phases:` list. Every phase below dispatches to a subagent at its assigned tier — **never** hardcode the tier in this skill text and **never** override the YAML without the user's explicit instruction. If the YAML is missing or malformed, abort with a clear message.

## Step 1 — Phase loop (per-phase Agent dispatch)

For each phase 1 through 7, do **not** fulfill the prompt inline. Dispatch to an `Agent` subagent at the tier assigned in `phase_model_tiers.yaml` (loaded in Step 0). The main session orchestrates: it builds the phase prompt, launches the agent, validates outputs, commits, then advances.

### A. Load the prompt template

Each phase script in `language_grammar_generator/phase{N}_*_prompt.py` exports a constant
named `PHASE{N}_*_PROMPT`. Read the file with the Read tool, extract the constant text. Phase 3
is the most critical (per CLAUDE.md) — produces all 4 domain components + fallbacks.

### B. Fill placeholders + thread forward inputs

The templates use `{LANGUAGE_NAME}`, `{LANGUAGE_CODE}`, `{LANGUAGE_FAMILY}`, `{SCRIPT_TYPE}`, `{WORD_ORDER}`. Substitute the values from Step 0.

**Subagents do not see prior session context.** For phases that depend on earlier phases' outputs (e.g. P3 needs P1's research doc, P6 needs P3's component file paths, P8 needs P3's config role vocabulary), the main session must Read the prior artifacts from disk and inline them into the next phase's prompt. Standard chains:

| Dispatching | Inline into the agent's prompt |
|---|---|
| P3 | full text of `languages/{folder}/{code}_grammar_concepts.md` (P1 output) |
| P5 | role list from `domain/{code}_config.py` (P3 output) |
| P6 | the 5 P3 component files' public method signatures + `languages/japanese/ja_analyzer.py` for the batch pattern |
| P8 | `domain/{code}_config.py` advanced-tier role vocabulary + `tests/test_end_to_end_pipeline.py` Latvian reference dict |

### C. Dispatch the agent

```
Agent({
  description: "Phase {N}: {phase_name}",
  subagent_type: "general-purpose",
  model: "<tier from phase_model_tiers.yaml — opus | sonnet | haiku>",
  prompt: <filled phase prompt
           + the threaded-forward inputs from step B
           + explicit instruction: "Write artifacts to these absolute paths: <list>.
              Run python -c 'import ast; ast.parse(open(P, encoding=\"utf-8\").read())'
              on each .py file you write before returning. Report back with: files
              written, any syntax failures, and a 1-line summary of design choices.">
})
```

**Tier rules (from the YAML — do not override without user instruction):**
- **opus** — P1, P3 (peak reasoning + critical-path)
- **sonnet** — P4, P6, P8 (correctness-sensitive but not novel)
- **haiku** — P2, P5, P7 (mechanical scaffolding, data entry, templated docs)

**Print before each dispatch:** `Phase {N} ({phase_name}) → {tier} agent dispatched`. This makes the tier choice visible to the user during the run.

**Imperative phrasing in the agent prompt — non-negotiable.** Sub-agents will return a *plan* instead of executing if the prompt sounds advisory. From the Portuguese smoke test: 3 of 4 sonnet agents in a parallel batch returned plans the first time around. Every dispatch prompt must:

1. Open with: **"EXECUTE THIS TASK NOW. Do not return a plan — actually use the Edit/Write tool to modify the file(s)."**
2. Use action verbs in step headings ("**Step 2: Make the changes (USE THE EDIT TOOL)**" not "Step 2: Changes to make").
3. End the prompt with a verification block the agent must run, not a "you may verify" suggestion.

If an agent returns only a plan, re-dispatch with stronger imperative phrasing — don't accept the plan as the output.

### D. Validate the agent's output (main session)

After the agent returns:
1. Confirm every file the agent claims to have written actually exists on disk.
2. Re-run the AST syntax check on each .py file the agent wrote (don't trust the agent's self-report alone).
3. For phases with critical-path risk (P1, P3, P6): spot-read the most important file (e.g. P3 `_response_parser.py`'s `parse_grammar_response` method) and verify the structure matches the gold-standard pattern.
4. If any check fails, do **not** commit. Re-dispatch the same phase with a corrective prompt that names the specific defect. Up to 2 retries; on third failure, halt and surface to the user.

### E. Auto-commit

```
git add languages/{folder_name}/
# Phase 6 also touches the registry — add that too:
git add streamlit_app/language_analyzers/analyzer_registry.py
# Phase 8 touches the E2E test:
git add tests/test_end_to_end_pipeline.py
git commit -m "Add {language_name} analyzer — Phase {N}: {phase_name} ({tier})"
```

Including the tier in the commit message lets the user audit the per-phase routing later. Standard `Co-Authored-By` line per repo convention.

### F. Report and proceed

Print: `Phase {N} ({phase_name}, {tier}) — committed as {short_sha}, {n} files written`. Move to next phase.

### G. Phase 8 — E2E mock data (post-Latvian requirement)

After Phase 7 ships, run a Phase 8 dispatch (sonnet tier per the YAML) to add level-appropriate mocks to `tests/test_end_to_end_pipeline.py`. The agent must produce three dicts (`{LANGUAGE}_MOCK_DATA` for beginner, `_{LANGUAGE}_INTERMEDIATE_MOCK`, `_{LANGUAGE}_ADVANCED_MOCK`), group them in `{LANGUAGE}_LEVEL_MOCK_DATA`, and add a parametrized `test_{lang}_all_difficulty_levels` test that calls the existing `_run_full_pipeline(...)` helper. See the canonical Latvian implementation. The advanced mock's `grammatical_role` tags must come from the analyzer's own advanced-tier vocabulary (e.g. `participle`, `debitive`, `relative_pronoun`) — never just renamed beginner roles. The agent's prompt must inline the advanced role list from `domain/{code}_config.py`.

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

CLAUDE.md requires: **the full pipeline must run successfully at all three difficulty levels** — beginner, intermediate, and advanced — for every analyzer. One full run per level.

### 4a. Add a single-level mock (default = beginner)

Append `{LANGUAGE}_MOCK_DATA` to `tests/test_end_to_end_pipeline.py` with `difficulty="beginner"`, then add it to the `LANGUAGE_MOCK_DATA` registry. This satisfies the existing parametrized `test_end_to_end_pipeline[{lang}]` test.

### 4b. Add intermediate + advanced mocks and a per-level test

Follow the **Latvian reference pattern** in the same file:

1. Define `_{LANGUAGE}_INTERMEDIATE_MOCK` and `_{LANGUAGE}_ADVANCED_MOCK` dicts. Each `mock_grammar_batch_response` must use grammatical-role tags drawn from the analyzer's own `domain/{code}_config.py` for that level — e.g. advanced should exercise roles that only exist in the advanced vocabulary, not just renamed beginner roles.
2. Group them in `{LANGUAGE}_LEVEL_MOCK_DATA = {"beginner": {LANGUAGE}_MOCK_DATA, "intermediate": ..., "advanced": ...}`.
3. Add a parametrized test that calls the existing `_run_full_pipeline(data, f"{lang}_{difficulty}", tmp_path)` helper:
   ```python
   @pytest.mark.parametrize("difficulty", ["beginner", "intermediate", "advanced"])
   def test_{lang}_all_difficulty_levels(difficulty, tmp_path):
       _run_full_pipeline({LANGUAGE}_LEVEL_MOCK_DATA[difficulty], f"{lang}_{difficulty}", tmp_path)
   ```

See `test_latvian_all_difficulty_levels` and `LATVIAN_LEVEL_MOCK_DATA` in `tests/test_end_to_end_pipeline.py` for the canonical implementation.

### 4c. Run

```bash
pytest tests/test_end_to_end_pipeline.py -v -s -k {code}
```

Must produce four reports under `tests/reports/`:
- `pipeline_report_{lang}.txt` — original parametrized run (beginner)
- `pipeline_report_{lang}_beginner.txt`
- `pipeline_report_{lang}_intermediate.txt`
- `pipeline_report_{lang}_advanced.txt`

Each report must show all 7 stages PASS. If any level falls back to generic AI (analyzer roles collapsed to gray `other`) or any role tag is missing from the analyzer's color scheme, fail the gate.

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
