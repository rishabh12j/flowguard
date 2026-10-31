# Changelog

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
