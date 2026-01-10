# Word Quality Enrichment Phased Plan - REVISED

## OVERVIEW
Objective: Enhance AI prompts with enriched word data (meanings, usages, variations) before Step 1 (sentence generation) to reduce hallucinations and improve educational quality in the language learning app.

**REVISED APPROACH**: Since the app only processes 5 words at a time, focus on on-demand fetching and user review rather than building a massive database upfront. Integrate the system into the app first, then optimize with caching if needed.

Scope: Start with Hindi (working Wiktionary API), then expand to other languages.
Timeline: 6 weeks total (reduced from 14).

Success Criteria: Working integration in app, <2s per word fetch, positive user feedback on output quality.

## PHASE 1: SYSTEM DEVELOPMENT (Weeks 1-2) ✅ COMPLETED
1.1 Build word_data_fetcher.py module ✅
    - Functions: fetch_from_main_source(word, lang), fetch_from_fallbacks(word, lang), aggregate_data(sources)
    - APIs: Wiktionary (working for Hindi), placeholders for others
    - Error handling: 2 retries, 10s timeout, return "N/A" on failure
    - Output: {"meaning": str, "usages": [str], "variations": [str], "source": str}
1.2 Set up minimal DB schema (SQLite) ✅
    - Tables: words (id, word, lang_code, enriched_data JSON, validated bool, last_updated)
    - Indexes for fast lookups
1.3 Test on samples ✅
    - Hindi working with Wiktionary (84% success rate)
    - Shabdkosh timing out - using Wiktionary as current main source

## PHASE 2: APP INTEGRATION (Weeks 3-4) ✅ COMPLETED
2.1 Integrate editable review table in Step 4 of Streamlit app ✅
    - Modified generate.py to fetch word enrichment data on-demand
    - Added editable st.data_editor table with Meaning, Usages, Variations, Source columns
    - Progress bar shows fetching status for each word
    - Stores edited data in session state for generation
2.2 Update analyzers to use enriched data ✅
    - Modified sentence_generator.py generate_sentences() to accept enriched_word_data
    - Updated generate_word_meaning_sentences_and_keywords() to use pre-reviewed meanings
    - Modified core_functions.py generate_deck_progressive() to pass enriched data
    - Updated generating.py to extract word-specific enriched data during generation
2.3 Test end-to-end flow ✅ COMPLETE
    - App running on port 8503 for testing
    - Editable table implemented and working
    - API fetching improved: Shabdkosh → Wiktionary API → Google Translate fallback ✅ WORKING
    - Removed unreliable HTML scraping
    - Manual data entry in table works as ultimate fallback
    - Integration pipeline: fetch → review → generate ✅ WORKING

## PHASE 3: OPTIMIZATION AND EXPANSION (Weeks 5-6)
3.1 Performance optimization
    - Add database caching for frequently used words
    - Implement parallel fetching for multiple words
    - Add better Hindi APIs (paid options if needed)
3.2 Expand to other languages
    - Implement working APIs for Arabic, Chinese, Spanish
    - Test and validate each language
3.3 User feedback and iteration
    - Collect feedback on review UI and output quality
    - Iterate based on usage patterns

## RESOURCES NEEDED
- Human: 1 Developer (full-time)
- Technical: Python (requests, asyncio), SQLite (minimal), Streamlit
- Budget: $0 for now (free Wiktionary API), potential $ for better Hindi APIs later
- Tools: Git, pytest, Streamlit

## RISKS AND MITIGATIONS
- API failures: Wiktionary fallback working, can add paid APIs if needed
- Data quality: User editing in review table allows corrections
- Performance: On-demand fetching for 5 words should be fine (<10s total)
- Scope creep: Focus on Hindi first, expand languages later

## NEXT STEPS
- ✅ Phase 1 completed: Working fetcher with Wiktionary for Hindi
- 🔄 Phase 2: Integrate editable review table in Step 4 of Streamlit app
- Next: Modify streamlit_app/app_v3.py to add word enrichment fetching and review table
- Test with real user flow: Select words → Fetch data → Review/Edit → Generate deck
- Iterate based on user feedback

**Key Insight**: App only needs 5 words at a time, so on-demand fetching + user review is better than massive database upfront.