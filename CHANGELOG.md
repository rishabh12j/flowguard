# Changelog

## 2026-11-04

- Chose a local `gemma4:12b` model through Ollama as the LLM, after measuring it against `gemma4:e4b` on INC-001.
- Added a provider-neutral `LLM` adapter with an Ollama implementation. All model failures become `LLMError`.
- Added `propose_hypotheses`, which asks the model for up to three root-cause hypotheses. A schema limits citations to the evidence provided, and code checks them again.
- The model can't set a hypothesis's confidence. Code will score it with the brief's rubric.
- Tests that call the real model are marked `llm` and only run with `pytest -m llm`.
- Added the `log_analysis` node, which searches the incident window through MCP and marks the earliest error as the first failure.
- Added the `dependency_trace` node, which finds deployments in the 24 hours before the first failure and drops those downstream of it on the dependency map.
- Log analysis and document retrieval now run in parallel. The graph runs asynchronously.
- Evidence from MCP is validated on arrival. A failing, denied, or truncated tool call is recorded in `errors` without stopping the investigation.
- Added the `root_cause` node. The model proposes hypotheses, and code scores them with the brief's confidence rubric, ranks them, and selects one only at 0.65 or above.
- The investigation abstains, with a reason, when there's no evidence, when the model fails or breaks the rules, or when no hypothesis scores high enough.
- Each source that failed or was cut short lowers confidence by 0.15.
- Moved the 24-hour lookback and the dependency-map walk into `domain/causality.py`, so evidence gathering and scoring use the same rule.
- With `gemma4:12b`, the graph now diagnoses INC-001 end to end. The rubric score isn't yet a measured accuracy.
- Each hypothesis now carries one of the brief's 11 incident categories, limited by the schema, and the incident takes the selected root cause's category, or `unknown` when FlowGuard abstains. This replaces a separate triage node. The reasons are recorded in the brief.
- The prompt defines every category. Without definitions, Gemma labelled INC-001 `data_quality` in 3 of 3 runs; with them, `schema_contract_mismatch` in 3 of 3, matching the ground truth.
- Known gap: the confidence rubric only rewards citations, so citing everything can only raise a score. Evidence precision in the evaluation runner should drive the fix.
- Added the `audit` node. Every investigation, whether diagnosed, abstained, or rejected, ends by saving an `InvestigationRecord` to SQLite.
- Each investigation gets an ID (`INVEST-…`) and a start time before the graph runs.
- `McpEvidenceTools` records every tool call, with its arguments, outcome (`ok`, `denied`, or `failed`), item count, truncation, and duration.
- The record stores the validated incident, never the raw request, so a rejected request leaves no trace of its contents.
- Records can only be added. Saving the same investigation twice fails instead of overwriting it.
- If the record can't be saved, the investigation fails instead of returning an unaudited result.
- Not yet audited: runbook retrieval (it doesn't go through MCP yet), full tool results, raw model output, and approvals.
- Added a FastAPI app with `GET /health`, `POST /investigations`, and `GET /investigations/{investigation_id}`. Run it with `uvicorn flowguard.api.app:app`.
- `POST /investigations` waits for the investigation, then answers 201 with the saved audit record and a `Location` header, or 422 with the record of a rejected request. This replaces the brief's two-step incident routes; the reasons are recorded in section 19.
- The request body is checked by the graph, not by FastAPI, so every rejected request is audited. No error response repeats the rejected input.
- The embedder, document index, model client, and audit store are loaded once at startup. Each investigation opens its own MCP tools, so call limits and tool history are never shared.
- `FLOWGUARD_AUDIT_DB` sets the audit database file, which defaults to `flowguard-audit.db`.
- The audit store now takes a lock, because requests share its SQLite connection across threads.
- Added `fastapi` and `uvicorn` as dependencies.
- Diagnosed INC-001 through the API with `gemma4:12b`: 201 in 23–50 seconds, `schema_contract_mismatch`, confidence 0.90.
- Known gap: when the model is unavailable, the investigation abstains with a 201 like any other abstention. A client can only tell the difference from the `abstention` text.
- Added remediation. After a root cause is selected, the model proposes up to five steps, chosen from a catalogue of five allowed actions, each with a target and cited evidence.
- Added the deterministic `validation` node. Risk, rollback, verification, and approval come from the catalogue, never from the model. A step is rejected, with its reason, when it isn't in the catalogue, cites unknown or unrelated evidence, targets something not in the evidence, or replays messages before an accepted fix.
- Every state-changing step requires approval. The plan, the rejected steps, and whether approval is needed are saved in the audit record. Records saved before this change still load.
- An abstention proposes no actions. If the model can't propose a plan, the investigation keeps its diagnosis with an empty plan.
- Real Gemma output changed one rule. Requiring every step to cite the root cause's evidence rejected a replay justified by the runbook and a contract test justified by HIST-INC-044. Runbooks and past incidents now count as grounds for a step.
- With `gemma4:12b`, INC-001's plan is: update the field mapping, replay failed messages, add a contract test, notify the service owner. Nothing was rejected, and approval is required. Gemma targets the mapping fix at `supplier-api`, while the ground truth names the transformation mapping. The evaluation runner will measure that.
- Added the human approval pause. A plan with a state-changing step is saved as `awaiting_approval`, and the graph stops in the new `approval` node until a person decides.
- Paused investigations are kept in a SQLite checkpoint file (`FLOWGUARD_CHECKPOINT_DB`, default `flowguard-checkpoints.db`), so they survive an API restart. Loading a checkpoint rebuilds only FlowGuard's own state classes.
- Added `POST /investigations/{id}/approve`, `/reject`, and `/request-more-evidence`, each with a named approver. Reject and request-more-evidence need a comment. Deciding an investigation that isn't paused answers 409.
- The audit store now keeps every version of a record. `GET /investigations/{id}` returns the latest, and the new `GET /investigations/{id}/events` returns them all. Records saved before versions existed are moved in as version 1.
- Two decisions can't both be saved: each version can be written only once, and the losing request gets 409.
- The graph has no module-level instance any more. The app builds it at startup with its checkpointer.
- Added `langgraph-checkpoint-sqlite` and `aiosqlite` as dependencies. Installing them upgraded `langgraph-checkpoint` to 4.3.1.
- With `gemma4:12b`, INC-001 paused for approval, survived a server restart, and was approved, keeping all three tool calls. A second decision got 409.
- Known gaps: approval records the decision but runs nothing, as the MVP allows. The approver's name isn't authenticated. Request-more-evidence ends the investigation instead of gathering more.
- Added credential redaction (`domain/redaction.py`) for passwords, API keys, tokens, bearer headers, JWTs, AWS keys, private keys, and credentials in URLs. Ordinary text such as "token expired" is left alone.
- Redaction is applied wherever outside text enters an investigation: MCP tool results, retrieved documents, the incident description, approval comments, and the whole request before it enters the graph.
- Fixed a leak found by the new safety tests: the raw request was kept in the graph state, so a credential in it was saved in every checkpoint, including the one written before the first node runs.
- Fixed a prompt weakness: evidence containing `</evidence>` could close the evidence fence early, so injected text after it would read as instructions. Fence tags inside data are now replaced.
- Added `tests/unit/test_safety.py`, covering every threat in the brief's safety list. Most tests use a compromised model that obeys injected text, and show that the catalogue, validation, scoring, and approval still hold.
- A test checks that the seeded data contains nothing that looks like a credential, so redaction never changes what Gemma sees for INC-001.

## 2026-11-03

- Added the `Incident` model, which validates an investigation request.
- Added the first LangGraph investigation graph: `intake` validates the request, and `runbook_retrieval` adds matching documents to the evidence.
- An invalid request now stops the investigation before any search, with errors that name the field but never repeat the rejected value.
- Added `langgraph` as a dependency.

- Added `SentenceTransformerEmbedder`, using `BAAI/bge-small-en-v1.5`.
- Added ingestion of API specs, runbooks, and historical incidents into Qdrant.
- Ingestion now refuses a chunk longer than the model's token limit, instead of letting it be cut off silently.
- Added `retrieve`, which searches current documents for one system and returns `EvidenceItem` results with their source metadata.
- Retrieval drops results below a placeholder threshold of 0.6, until evaluation cases exist to tune it.
- Added 20 retrieval evaluation cases and `python -m flowguard.evaluation.retrieval`, which reports recall, precision, and abstention across thresholds.
- Kept the retrieval threshold at 0.6, now based on the evaluation: recall 1.00, precision 0.42, abstention 0.71 on the cases it was tuned on.
- `SentenceTransformerEmbedder` now raises an error if the model doesn't report its input limit, instead of storing `None`.

## 2026-10-30

- Added the Python package and test setup.
- Added the `EvidenceItem` model and its tests.
- Added the INC-001 synthetic dataset, including separate ground truth.
- Added `flowguard.dataset` to load the dataset as `EvidenceItem` records.
- Added seed validation tests for INC-001.
- Added a temporary integration test that solves INC-001 without an LLM.
- Added `observability-server` with the read-only `search_logs` tool.
- Added `operations-server` with the read-only `get_deployments` tool.
- Made `service` optional on both tools, so a search can cross services.
- Added `knowledge-server` with the read-only `get_dependency_map` and `get_api_spec` tools.
- Added tool policies and `ToolGuard` for allowlists, call limits, and unknown arguments.
- Added `GuardedClient`, which applies those checks and a timeout to every tool call.
- Added metadata-aware chunking for API specs, runbooks, and historical incidents.
