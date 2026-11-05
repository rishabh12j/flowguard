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
- The Ollama client now retries server errors and lost connections up to twice, waiting 2 then 4 seconds. Timeouts and client errors, such as a missing model, aren't retried. This covers the intermittent crash of Ollama's runner seen in earlier runs.
- If validation rejects every step of a plan, the model gets one more attempt, with each rejection's reason in its prompt. Rejected steps record which attempt proposed them.
- "Request more evidence" now sends the investigation round once more: the reviewer's comment becomes a new knowledge-base search, the model sees the comment, and the new plan pauses for approval again. A second request ends the investigation.
- Every run of the graph has a step limit of 40, as a backstop against a routing mistake.
- Fixed: every error counted as a missing evidence source, so a failed plan in one round would have lowered the next round's confidence. Only errors from evidence-gathering nodes count now.
- Fixed: a checkpoint stores tuples as lists, so adding evidence after a resume failed with `TypeError`. The state's reducers now accept both.
- The audit record gains `evidence_round` and `reviewer_request`.
- Document retrieval now goes through MCP: the knowledge server has a `search_runbooks` tool (the brief's name), which searches current runbooks, API specifications, and past incidents for one system. `top_k` is limited to 1–10.
- Every piece of evidence now comes through MCP, so retrieval has a call limit (3 per investigation), is redacted on arrival, and appears in the audit's tool calls. The graph's separate retriever is gone.
- The knowledge server is built with the search function passed in, so the slow embedder is loaded once by the API. `open_evidence_tools` requires it, so the investigation can't be wired up without document search.
- A failed document search is recorded in `errors` and counts as a missing source, in the first round and in a reviewer's follow-up. The investigation goes ahead with the evidence it has.
- Added alerts and metrics as evidence. Alerts are loaded from `data/alerts/`, metrics from `data/metrics/`. A metric becomes one piece of evidence per period, timed at the moment it first crossed its threshold.
- The observability server gained `search_alerts`, `get_alert`, and `get_metrics`. `get_metrics` takes `metric_names` as optional, unlike the brief, so the graph can ask for everything a service records.
- `dependency_trace` now gathers alerts and metrics alongside deployments, from the same 24 hours and the same services at or upstream of the failure. One tool failing loses only its own evidence.
- The confidence rubric's timeline and path signals now count any cited change: a deployment, an alert, or a metric that crossed its threshold. Before, a cause that wasn't a deployment could never reach 0.65. The reasons are recorded under the rubric in the brief.
- Added INC-002 (an expired bank API credential causes 401s) and INC-003 (a backfill pushes requests past the carrier's 100 a minute, causing 429s), each with logs, decoy deployments, a dependency map, an API spec, a runbook, a past incident, and ground truth.
- Ground truth now includes a `reference_plan`, including for INC-001.
- Added five catalogue actions: `rotate_credential`, `rerun_job`, `pause_job`, `enable_rate_limiting`, and `add_monitoring`.
- Logs and deployments now record which system they belong to.
- Replaced `test_inc_001_solvable.py`, a hand-written solver, with `test_incidents_solvable.py`. It runs every incident through the real graph, MCP servers, and retrieval, with an oracle model that cites the ground truth. It must gather the required evidence, select the right category, and get the reference plan through validation.
- Fixed in review: a metric that never crossed its threshold still earned the path signal. It isn't a change, so it now earns nothing.
- Added INC-004 (a configuration change makes the uploader put the payment file in `/outbound/payments`, which the bank never reads) and INC-005 (a configuration change shrinks the database connection pool from 50 to 5, so requests time out at the morning peak). All five incidents from the brief's catalogue now exist, each a different category.
- Added data schemas (`seed_schemas.py`): every log, deployment, alert, metric series, dependency map, document header, and ground truth is validated as it loads. A map's edges must join known nodes, metric points must be in time order, and a document must be in the folder for its type. `load_ground_truth` now returns a `GroundTruth` model.
- The operations server gained the brief's `get_incident` and `search_incidents`. Retrieval can now filter by document type inside the search, so other documents can't fill the result limit.
- Added the `redeliver_file` catalogue action.
- Fixed INC-003's dependency map: an edge from A to B means B depends on A, so the carrier API now points to `order-sync-worker`.

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

## 2026-11-05

- Added the evaluation runner, `python -m flowguard.evaluation.investigations`. It runs every seeded incident through the real stack and writes `reports/evaluation.json` and `reports/evaluation.md`.
- Each incident also runs with log searches denied, to measure whether FlowGuard abstains when evidence is missing.
- Metrics follow the brief: diagnosis accuracy (a root cause selected, in the right category), top-3 recall, evidence precision, required-evidence recall, tool-call success, latency, unsupported claims, unsafe actions (rechecked against the catalogue independently of validation), and approval bypasses. Plan recall and refused steps are reported too.
- Ground truth gained `relevant_evidence_ids`, the other evidence that supports a diagnosis, so precision doesn't penalise good citations.
- A test runs the whole evaluation with the oracle model, where every metric must be perfect, to check the runner before trusting its numbers.
- First results with `gemma4:12b`: 3 of 5 incidents diagnosed correctly, 4 of 5 with the right category in the top 3, 97% evidence precision, 100% required-evidence recall, zero unsupported claims, zero unsafe actions, zero approval bypasses, and abstention in all 5 runs without logs. A second run gave the same results.
- Known gaps, from the results: Gemma labels a configuration change's effect by its trigger (`deployment_or_configuration`) instead of its mechanism, in INC-004 and INC-005. In INC-004, a partly valid plan lost both its fix steps to validation and wasn't retried, so it ended with no fix.
- The first results are kept as `reports/evaluation-baseline.md` and `.json`.
- A plan is now retried when validation refused steps and nothing left would fix the cause, not only when nothing is left. In INC-004, a plan that lost its rollback had kept only a contract test, a notification, and monitoring.
- The remediation prompt names each target kind exactly: "a service name", or "a deployment ID, such as DEPLOY-SOURCE-221".
- The category definitions and the root-cause prompt now say a configuration change's effect takes the category of what went wrong, and `deployment_or_configuration` is for a change that is broken in itself.
- After these changes, with `gemma4:12b`: 5 of 5 incidents diagnosed correctly, 5 of 5 with the right category in the top 3, zero unsafe actions, zero approval bypasses, abstention in all 5 runs without logs, and median latency 46 s. The prompt changes were written after seeing these incidents fail, so this result partly measures that tuning, and new, unseen incidents are needed for an unbiased number.
- Known gap: INC-004's plan still puts the file redelivery before the rollback, so validation refuses it, and the file isn't redelivered.
- The evaluation report now lists each refused step with its reason, and every hypothesis's category.
- Added Docker Compose: `docker compose up --build` starts the API and a Qdrant server, with the audit records, paused investigations, and document index on named volumes. By default the API uses the Ollama on the host; `docker compose --profile ollama up` runs Ollama in a container too.
- Added a `Dockerfile`: Python 3.13, CPU-only PyTorch, the embedding model built into the image so it starts offline, and a non-root user.
- Added `GET /health/ready`, which checks the document index, the model in Ollama, and the audit store, and answers 503 without error details if any fails. `/health` stays a liveness check.
- The Ollama address, the model, and a Qdrant server are now settings: `FLOWGUARD_OLLAMA_URL`, `FLOWGUARD_MODEL`, and `FLOWGUARD_QDRANT_URL`. Without a Qdrant URL, the index stays in memory.
- Added `.env.example`, with every setting commented out, so copying it can't override the container's own values; and `.dockerignore`, which keeps `.env`, databases, and tests out of the image.
- Verified in Docker: INC-001 diagnosed through the containers, the API container restarted while the investigation waited for approval, and the approval recorded afterwards.
- Added `GET /investigations/{id}/report`: a readable Markdown report of the latest record, with the root cause and its confidence reasons, the evidence, each step's risk, approval, verification, and rollback, any refused steps, the decision, and problems met.
- Every error is now JSON. An unexpected crash answers 500 with `{"detail": "internal error", "error_id": ...}`; the full traceback is logged on the server under the same ID, and nothing else reaches the caller.
- Added a demo, `python -m flowguard.demo [--incident ID] [--approve | --reject REASON]`, which walks an incident through a running API: readiness, the investigation, the plan, the decision, the report, and the audit trail. Run against Docker Compose and Gemma, it took INC-002 to an approved plan.
- Added `examples/requests.http`, sample requests for every route, including an invalid request and a second decision.
- Added CI on GitHub Actions: ruff, formatting, mypy, and the full test suite on every push and pull request, plus a job that builds the Docker image. The workflow passes `actionlint`.
- Added a README: what FlowGuard does, its results with their caveats, setup with and without Docker, the demo, the API, its safety controls, and the project layout.
- Added `docs/architecture.md` (components, the investigation graph, evidence, the confidence rubric, state and audit, and the main design decisions), `docs/threat-model.md` (trust boundaries, each threat with its controls and the tests that prove them, and the risks that remain), and `docs/evaluation.md` (method, metric definitions, baseline and tuned results, and their limits).
- Added three held-out incidents: INC-006 (a broker failover replays events and refunds are paid twice), INC-007 (a release drops a required setting and the email sender won't start), and INC-008 (a DNS migration drops a record and the nightly sync can't reach its database). Their ground truth is marked `"split": "held_out"`, and `python -m flowguard.evaluation.investigations --held-out` evaluates only them, into `reports/evaluation-held-out.*`.
- The held-out incidents were checked only with the oracle model, then evaluated once with Gemma, and nothing was changed afterwards. INC-007's configuration spec couldn't be retrieved from the reporter's description, so it's listed as relevant rather than required evidence instead of rewording the incident.
- Held-out results with `gemma4:12b`: 3 of 3 diagnosed correctly, 100% evidence precision and recall, zero unsafe actions, zero approval bypasses, abstention in 3 of 3 runs without logs, and 67% plan recall. Two of the three plans (INC-006, INC-008) had no step that fixes the cause: diagnosis generalised, planning did not.
- Updated the README and `docs/evaluation.md` with both sets of results.

## 2026-11-06

- The MCP servers, the tools, and the evaluation runner now take their data, so the benchmark lives in its own directory and never slows the normal tests or CI. `python -m flowguard.evaluation.investigations` gained `--data-dir`, `--output-dir`, and `--split`.
- A long evaluation is now resumable: each finished incident is appended to a journal, and running the same command again skips what's done.
- Added the benchmark generator, `python -m flowguard.benchmark.generate --seed 2027`, which writes `data/benchmark/`: 22 scenario families, two per category including two where abstaining is right, varied across 20 systems that share one topology. Variants differ in their system, wording, timings, field names, error counts, and decoys, including, in about 30% of cases, a harmless upstream deployment inside the lookback.
- The families are split by family into dev (11 families, 55 incidents) and test (11 families, 250 incidents), one family per category in each. Test families are run with a model only once.
- Added `python -m flowguard.benchmark.check`, which must pass before any model sees the benchmark: every record loads against the schemas, redaction changes nothing, incidents stay isolated in time, and the oracle solves every incident through the real graph. All 305 pass. It can't catch a wrong category label, because the oracle answers from the ground truth; the labels come from the family definitions.
- Ground truth gained `family` and `expected_outcome` (`diagnose` or `abstain`). The evaluation now scores abstain-correct cases on abstaining, reports diagnosis accuracy with a 95% Wilson interval over the incidents to diagnose, adds abstention accuracy and false-abstention rate, and breaks results down by family and category.
- The oracle model moved from the tests to `flowguard.evaluation.oracle`, since the checker uses it.
- FlowGuard is now open source under the Apache License 2.0, chosen for its explicit patent grant. The package metadata declares it, and the Docker build copies the licence it needs.
- Added `CONTRIBUTING.md`, with the checks CI runs and the ground rules: tools stay read-only, code decides rather than the model, every rule has a test that fails without it, no secrets or real data, and no tuning on held-out or test sets.
- Added `docs/connectors.md`, the contract a connector to a real system must meet: each server's tools and arguments, the evidence format, the metadata the investigation relies on, the rules, how to test, and the connectors wanted. First wanted: a setting that points FlowGuard at an external MCP server.
- Dev benchmark with `gemma4:12b` (55 incidents): 51 of 55 correct (92%, 95% interval 81% to 97%), 5 of 5 abstentions where abstaining was right, abstention in 55 of 55 runs without logs, zero unsafe actions, zero approval bypasses, and 77% plan recall. Six diagnosed plans had no step that fixes the cause.
- The evaluation now also reports plan precision (the share of planned steps in the reference plan), missing fixes (a diagnosed plan that fixes nothing, though the reference plan does), and unneeded fixes (a plan that changes something, though the reference plan fixes nothing), with missing fixes per family and category. They were added before the test run.
- Tried, on dev only, and removed: retrying any plan with no step that fixes the cause. The retry fired on all five targeted plans, and Gemma kept a plan without a fix each time (plan recall 75%, against 77% without it). A trace of BENCH-0048 showed why: no action in the catalogue describes stopping a worker that is doing harm, and the reference plan used `pause_job` beyond its stated purpose. The gap is in the catalogue, not the model, and it is left as a known limitation. The run is kept in `reports/benchmark/evaluation-dev-plan-retry.*`.
