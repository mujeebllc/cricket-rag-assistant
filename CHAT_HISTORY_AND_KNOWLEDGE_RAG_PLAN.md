# Chat History, Context, and Cricket Knowledge RAG Plan

## Goal

Make turns within one chat share useful context, retain conversations across page reloads, and answer general cricket questions from the separate cricket-knowledge RAG. Keep database-backed statistics on the existing read-only SQL path.

## Current State and Root Cause

- `frontend/app.js` posts only `{ question }` to `/api/chat`. It renders messages into the DOM, and Clear only empties that DOM; there is no browser persistence or conversation identifier.
- `backend/main.py` accepts one question and calls `detect_language`, `generate_sql`, SQL execution, and `generate_answer` without loading or storing prior turns.
- `backend/sql_generator.py` checks deterministic regex rules before calling `retrieve_schema()`. A match returns hand-built SQL immediately, so that question does not use schema RAG or LLM SQL generation. The regex path is useful for narrow, well-defined cases, but current patterns can claim broader questions and return valid SQL for the wrong intent.
- Verified regex examples: `generate_direct_database_counts_sql()` runs first and matches `registered.*player|player.*registered`, so “Which country has the most registered players?” is returned as a registered-player count before the country-ranking rule later in `generate_direct_rankings_bowling_sql()` can run. Also, `generate_direct_player_profile_sql()` runs before rankings and includes `who is (.+?)`; “Who is the highest run scorer?” can therefore become a lookup for a player literally named “the highest run scorer” instead of reaching the most-runs rule. SQL safety, table validation, and dry-run execution do not detect this semantic mismatch.
- For complex database questions, the correct target is not “always use RAG”: narrow, exact rules should remain fast, while a question should use schema RAG + LLM SQL generation whenever no rule fully represents its filters, grouping, comparison, or requested result. Raw chat history must not be added to SQL generation; follow-ups need to be resolved into a standalone database question first.
- The general knowledge implementation is isolated in `backend/rag/knowledge/`. `retrieve_knowledge()` is not called by the API or frontend. The indexer currently stores the whole `cricket_knowledge.txt` as one Qdrant point, and the retriever returns retrieved text without checking relevance scores.
- `backend/settings.py` already separates `KNOWLEDGE_COLLECTION` from `SCHEMA_COLLECTION`. The current corpus is a short primer, so general-question coverage and provenance need work before claiming broad cricket expertise.

## Recommended Design

### Conversation identity and persistence

- Have the client create a random `conversation_id` for a new chat and send it with each turn. The server validates the ID and owns message ordering and persistence.
- Add a small conversation store isolated from cricket statistics. For this single-user/local application, a SQLite database at a configurable project data path is a low-friction first choice; use parameterized SQL and create the tables at startup. If deployment later requires multiple users or shared hosting, move this store to the deployment's managed database and add authentication/ownership checks.
- Store conversation metadata and ordered messages (role, content, timestamp, optional route and source metadata). Store user and assistant messages only after a turn is successfully processed, or mark failures explicitly so retries do not duplicate turns.
- Add API operations to list conversations, load a conversation's messages, start a new conversation, and delete a conversation. A deleted conversation must also lose its messages.
- Keep `conversation_id` opaque and non-sequential. Without authentication, treat this as local/single-user functionality, not access control for a public multi-user service.

### Bounded context window

- Load only the latest relevant turns for each request; enforce a configurable message/token budget rather than sending unlimited history. The context should remain below the selected Ollama model's effective context limit with room reserved for system instructions, retrieved text, results, and output.
- Initially use recent user/assistant text and a simple token/character budget. Add a rolling summary only if real conversations exceed that budget; refresh it from persisted messages and retain recent turns verbatim.
- Keep the stored transcript separate from the prompt context. Do not include generated SQL or large result tables in ordinary conversational context by default; retain those as optional message metadata and summarize only facts needed for follow-up questions.
- When a request is a follow-up, resolve it using recent history into a self-contained question before routing. Example: after “Who scored the most runs?”, “Which team did he play for?” must resolve the person before SQL generation. Preserve the resolved question in logs/metadata for debugging.

### Hybrid cricket question routing

- Route each turn to one of: database statistics, general cricket knowledge, or mixed/unsupported. Use conversation context to classify short follow-ups, but do not use prior chat to override an explicit new topic.
- Within database questions, retain deterministic SQL only for narrow patterns whose full intent and constraints are represented by the rule. Add explicit rule-match diagnostics and a reliable way to assert which rule/path handled a question. Any extra grouping, comparison, time range, ranking scope, or other unsupported constraint must fall through to schema RAG + LLM SQL generation rather than being silently dropped by a regex.
- Database questions continue through `generate_sql()` and the existing SQL safety checks. The resolved standalone question, not the whole transcript, is the input to fast-path matching, schema retrieval, and SQL generation. SQL dry-run validation proves executability, not that the requested semantics were answered; semantic expectations need regression coverage.
- General questions call `retrieve_knowledge()`, then a dedicated answer-generation function with retrieved excerpts and recent conversational context. Require the answer to stay grounded in the excerpts; if retrieval is weak or empty, say the indexed material does not answer the question instead of inventing facts. Include source title(s) where available.
- For a mixed question, either combine the SQL result and retrieved knowledge in a controlled synthesis step or ask a concise clarification. Do not silently answer one half.
- Keep live/current cricket scores out of the knowledge route unless a live-data source is separately implemented; static RAG cannot answer current events reliably.

### Knowledge corpus and retrieval quality

- Expand `cricket_knowledge.txt` into reviewed topic-based documents covering laws, formats, scoring, dismissals, roles, tournaments, and terminology. Record authoritative source/provenance and review date for claims that can change.
- Chunk by coherent paragraph/topic with overlap where needed. Store stable point IDs and payload metadata such as source, title, section, and text; avoid one vector for the entire corpus.
- Return scores and metadata from retrieval. Establish a relevance threshold through representative tests; return no context below threshold rather than always passing the nearest result to the LLM.
- Keep the knowledge collection isolated from the schema collection. Before indexing, validate the configured collection name and dimensions; the current indexer recreates its collection, so indexing must never target `SCHEMA_COLLECTION`.

## Incremental Implementation Phases

### Phase 0: Baseline and contracts

- Complete or explicitly defer the stabilization plan's test/API baseline work before changing the chat pipeline.
- Define route labels, conversation lifecycle semantics, context budget, retention/deletion policy, and whether the initial deployment is strictly single-user.
- Add deterministic tests for SQL fast-path routing, context assembly, follow-up resolution, overall question routing, and store behavior before connecting Ollama or Qdrant.

### Phase 1: Correct SQL fast-path routing

- Inventory every direct-rule function and its position in `generate_sql()`; document the prompt shapes and constraints each rule actually supports.
- Narrow overbroad regexes and correct precedence so specialized rankings are not swallowed by generic counts or profile lookups. In particular, cover the registered-player country-ranking/count collision and `who is ...` versus player-profile/ranking ambiguity.
- Make fast-path matching explicit and observable (for example, return or log a route/rule identifier alongside SQL internally). Do not use a rule merely because a broad phrase matched; require the full supported intent. Unsupported complexity must reach schema RAG.
- Add regression tests that assert both route and answer semantics: “Which country has the most registered players?” must rank countries; “How many registered players are there?” must count; “Who is the highest run scorer?” must run the ranking; a real named-player profile question must remain a profile lookup; and a multi-dimensional query such as team win rates by tournament must reach schema RAG.
- Extend tests for tie handling, filters, and multi-part questions. Keep SQL safety and MariaDB dry-run checks, but do not treat successful execution as proof of correctness. Verify generated SQL and returned rows against reviewed expected results for database-backed cases.

**Exit criteria:** Supported simple prompts select the intended fast path; unsupported/complex database prompts demonstrably use schema RAG; regression prompts produce the intended result, not just executable SQL.

### Phase 2: Persist conversations

- Implement the conversation store and API models/endpoints in `backend/main.py` (or a small focused backend module).
- Extend `/api/chat` to accept a conversation ID, append turns in order, and return the ID plus the existing answer/SQL/result fields.
- Update `frontend/app.js` to keep the active conversation ID, load its messages on startup, and create/delete conversations. Use browser storage only for the active ID and UI preferences; the server transcript is canonical.
- Preserve existing clients temporarily by creating a new conversation when the ID is omitted.

### Phase 3: Use context without changing SQL semantics

- Add a bounded context builder and a follow-up-to-standalone-question step.
- Pass the standalone question to the language detector, corrected fast-path rules, schema retriever, and SQL generator. Preserve route diagnostics so regressions reveal whether a bad answer came from follow-up resolution, a direct rule, or schema RAG.
- Record the original user wording separately from the resolved question. Verify that a new conversation never sees another conversation's turns.

### Phase 4: Activate general cricket RAG

- Improve corpus, chunking, payload metadata, and retrieval score handling; add an index verification command/test before enabling the route.
- Add the general knowledge answer path and route selection. Keep the SQL response contract compatible, adding optional route/source fields rather than removing current SQL fields.
- Ground answers in retrieved passages and make empty/low-confidence retrieval an explicit fallback.

### Phase 5: Frontend history and integrated quality

- Add conversation selection/listing, new chat, reload restoration, and delete confirmation while preserving the existing chat UI and technical SQL details.
- Add end-to-end coverage for multi-turn context, page reload, clear/new chat isolation, deletion, database questions, knowledge questions, and ambiguous/mixed questions.
- Evaluate retrieval precision and answer faithfulness on a reviewed cricket-question set; document unsupported topics and live-data limitations.

## Acceptance Criteria

- A follow-up in the same conversation correctly uses relevant earlier turns; the same follow-up in a new conversation does not.
- A page reload restores the selected conversation and its ordered messages; deleting it removes it from subsequent list/load responses.
- Context sent to the model is bounded and does not accidentally include unrelated conversations or oversized SQL result payloads.
- Database questions use a direct SQL rule only when its full intent is supported; complex/unsupported queries reach schema RAG, and tested prompts produce semantically correct answers as well as read-only, executable SQL.
- Existing database questions still pass SQL safety validation, while wrong-intent fast-path selections are covered by route-level regression tests.
- General cricket questions use knowledge retrieval, include grounding/source metadata when available, and abstain when no relevant source is retrieved.
- Knowledge indexing cannot recreate the schema collection, and tests run without requiring a live Ollama/Qdrant/database service wherever practical.

## Main Risks and Decisions

- **Context ambiguity:** Pronouns and topic changes can resolve incorrectly. Keep the original question, resolved question, and selected route observable; clarify instead of guessing when confidence is low.
- **Context growth:** A fixed recent-turn window can lose older facts. Start with a measured budget; add summaries only after tests show the need.
- **Public deployment:** Conversation IDs alone do not provide authorization. Require authentication and ownership checks before exposing stored history to multiple users.
- **Knowledge reliability:** The current primer is too small to support “any cricket question.” Expand and review the corpus, set retrieval thresholds, and be transparent about scope.
- **Regex routing:** Rule ordering and permissive patterns can bypass schema RAG and produce plausible, executable but semantically wrong SQL. Keep rules narrow, assert route selection in tests, and send unsupported complexity to the RAG-to-SQL path.
- **Existing stabilization work:** The repository's `PROJECT_STABILIZATION_PLAN.md` defers feature work until core tests and API behavior are trustworthy. Treat these phases as the next feature plan after agreeing which stabilization gates are mandatory.