# Changelog

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
