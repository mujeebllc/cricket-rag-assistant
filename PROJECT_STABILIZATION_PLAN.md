# Project Stabilization Plan

## Objective

Make the existing Cricket Assistant reliable, understandable, and testable before starting new features. This plan is based on the current code and observed evaluation runs. It is a work plan only; it does not change application code.

## Current baseline

- The API, frontend, Ollama, Qdrant, and database were reachable during the last live check.
- A live chat request for the total number of matches returned the expected answer.
- `backend/run_accuracy_regression_suite.py` previously passed **28/30 (93.3%)**. Later fixes raised the current run to 30/30; re-run against the current database before treating this as a baseline.
- SQL safety checks passed 5/5, and the active Python modules compiled.
- The broader `backend/backend_test_suite.py` is not currently a reliable overall gate: it reported 5/11 on its legacy regression cases and then stopped when the Windows console could not print Urdu characters.
- The cricket-knowledge RAG under `backend/rag/knowledge/` is now connected to `/api/chat` for general rules and terminology, using its own Qdrant collection. Re-index that collection after corpus changes.
- SQL routing, knowledge retrieval, and API tests have been added since this plan was drafted; update the remaining stabilization status against a fresh run.

These are a starting point, not a release-quality acceptance standard. Re-run the checks against the current database before treating the figures as a new baseline.

## Prioritized work

### Phase 1: Establish trustworthy tests and expected results

The current evaluation scripts disagree about expected database values. For example, the legacy accuracy suite expects 18,485 players, while its run returned 10,979; other legacy cases also failed against their expected counts. The comprehensive suite's Urdu output caused a Windows console encoding error and terminated the run.

- Decide which database snapshot and semantics define correct answers (for example, all players versus registered players).
- Verify each expected result against the intended database using reviewed, read-only SQL; record the source and meaning of each expected value.
- Remove stale, ambiguous, or duplicate expectations from the acceptance set; do not make a test pass merely by changing its expected answer to match an unexplained result.
- Make evaluation output encoding-safe on supported platforms, including Windows and Urdu text.
- Ensure test failures are reported without aborting unrelated test categories, while preserving a nonzero process exit when the overall suite fails.
- Separate offline/unit checks from database-, Qdrant-, and Ollama-backed integration checks.

**Exit criteria:** A clean, repeatable test run reports all planned categories and has trusted expectations tied to a documented database snapshot.

### Phase 2: Fix verified query correctness failures

Two failures were observed in the 30-case run:

1. **Country with the most registered players:** The question generated a total registered-player count rather than a country ranking. In `backend/sql_generator.py`, the broad `registered.*player|player.*registered` rule appears before the country-ranking rule and captures the query first.
2. **Best bowling wickets in an innings:** The generated query returned one 10-wicket innings instead of the benchmark's expected player. Database inspection showed multiple bowlers tied at 10 wickets, including the expected player. The rule contains a player-name-specific filter and uses `LIMIT 1` without a tie policy, so the question is not being answered as a general ranking.

- Correct routing precedence so specialized ranking intents are not swallowed by broad count rules.
- Define the meaning of “best bowling” and the desired tie behavior; use that definition consistently in SQL and its expected result.
- Add regression tests for the exact failed prompts and nearby negative/paraphrased prompts.
- Check that the generated SQL, database rows, and final natural-language answer all match the same expected intent.

**Exit criteria:** Both failures pass, nearby cases do not regress, and the verified end-to-end evaluation improves without weakening its checks.

### Phase 3: Clarify and verify language support

The project describes itself as multilingual, but `detect_language` in `backend/answer_generator.py` documents English and Roman Urdu and says Urdu script defaults to English/Roman Urdu. The broader suite includes Urdu-script cases and expects an `urdu` language result. That contract is currently inconsistent, and the suite's encoding crash prevented a complete report.

- Decide whether Urdu script is supported in the product or whether support is English plus Roman Urdu only.
- Align language detection, answer generation, API response expectations, README, and tests with that decision.
- If Urdu script is supported, add end-to-end tests for detection, SQL generation, and Urdu-script answers.
- If it is not supported, state the limitation clearly and avoid counting unsupported cases as a passing language feature.

**Exit criteria:** The supported languages and test expectations agree, and all claimed language paths are verified end to end.

### Phase 4: Add reliable API-level regression coverage

The previous checks exercised a live chat request manually, while most existing evaluation scripts call Python functions directly.

- Add automated checks for API health, request validation, response shape, and a representative successful chat request.
- Cover empty/whitespace questions and dependency failures with clear, expected HTTP responses.
- Keep a small deterministic API test separate from slower live-model evaluations.

**Exit criteria:** The API contract is testable without relying exclusively on a manual Swagger/browser check, and failure cases are observable.

### Phase 5: Stabilize the separate cricket-knowledge RAG independently

This component is distinct from the active schema RAG used for SQL generation. The current knowledge RAG has an indexer in `backend/rag/knowledge/index_knowledge.py`, a retriever in `backend/rag/knowledge/knowledge_retriever.py`, a single checked-in source file (`cricket_knowledge.txt`), and a separate `KNOWLEDGE_COLLECTION` setting. It embeds and retrieves text, but no answer-generation flow or main-API integration was found. Do not wire it into the main API as part of stabilization.

- Decide whether this standalone RAG is an intended supported component, a future experiment, or something to retire later; until that decision, keep its status explicit and do not imply that the chat API uses it.
- Review `cricket_knowledge.txt` for correctness, coverage, provenance, and freshness. Confirm it contains enough authoritative knowledge for the intended questions before treating retrieval results as useful.
- Verify that `KNOWLEDGE_COLLECTION` names a collection isolated from the active schema collection before any indexing run. The indexer recreates its configured collection, so running it against the wrong collection could delete the existing indexed data.
- In an isolated test environment, index the knowledge document and verify collection creation, document count, payload fields, and successful retrieval for representative cricket-rule questions. Also test empty/no-match behavior and service/model failures.
- Check that changing `EMBEDDING_MODEL` requires re-indexing and that indexed vector dimensions match the configured model.
- Record clearly that retrieval alone does not provide a complete question-answering feature; any future answer-generation or API integration is separate work requiring an explicit product decision and its own end-to-end evaluation.

**Exit criteria:** The knowledge corpus and retrieval path have independent, repeatable checks; its support status is documented; and it remains separate from the main API unless integration is explicitly prioritized later.

### Phase 6: Reconcile documentation and supported workflows

- Update README and architecture/pipeline documentation to reflect verified behavior, supported languages, current test commands, and known external-service requirements.
- Remove outdated accuracy claims or mark them with their database snapshot and evaluation method.
- Document which scripts and RAG paths are active, standalone, diagnostic, or legacy. State explicitly that the cricket-knowledge RAG is not wired into the main API.
- Keep this phase focused on accuracy and operational clarity; do not add new user-facing capabilities.

**Exit criteria:** Setup, run, and evaluation instructions match the verified implementation.

## Definition of “project is OK”

Before feature work begins:

- The agreed regression suite completes on the supported developer platforms.
- Expected answers have a traceable database basis.
- Previously observed query failures are fixed and covered.
- The language support contract is explicit and tested.
- API success and failure behavior has automated coverage.
- The separate cricket-knowledge RAG is either independently verified and accurately described as standalone, or explicitly marked unsupported/deferred.
- Documentation makes no unsupported accuracy or feature claims.
- The agreed end-to-end benchmark meets a project-owner-set acceptance threshold, with failures explained rather than hidden.

## Deferred until stabilization is complete

Do not begin unrelated feature work or dependency-removal work until the definition of “project is OK” is met. Reassess enhancements only after the stable baseline is repeatable and the project owner prioritizes the next change.
