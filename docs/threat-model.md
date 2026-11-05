# Threat model

FlowGuard reads untrusted text (logs, documents, incident reports), asks a model to reason about it, and proposes changes to running systems. The design assumes the model can be wrong or manipulated, and puts every control that matters in code.

## What needs protecting

- **The systems a plan would change.** A wrong or malicious step, approved, could make an incident worse.
- **The approval decision.** A state-changing step must never proceed without a named person's explicit decision.
- **The audit trail.** It must show what FlowGuard saw, concluded, and proposed, and who decided what.
- **Credentials** that appear in logs, documents, or reports.

## Trust boundaries

| Boundary | What crosses it | How it's treated |
|---|---|---|
| API requests | Incident reports, decisions | Validated by schema; redacted before the graph sees them; invalid requests audited without their contents |
| MCP tool results | Logs, deployments, alerts, metrics, maps | Validated as `EvidenceItem`, redacted on arrival |
| Retrieved documents | Runbooks, specs, past incidents | Only current documents for the system; redacted |
| Model output | Hypotheses, plans | Constrained by a schema with enum-limited IDs, then validated again in code |
| Checkpoint files | Paused graph state | Only FlowGuard's own classes are rebuilt on load |

## Threats, controls, and tests

These follow the brief's safety list. The tests are in [`tests/unit/test_safety.py`](../tests/unit/test_safety.py) unless noted. Most use a *compromised model*: a fake that does whatever injected text asks.

| Threat | Controls | Tests |
|---|---|---|
| Prompt injection in a log | Evidence is fenced off as data, and the system prompt says never to follow it. Fence tags inside evidence are removed. A model that obeys anyway can only propose; code decides. | `test_injected_log_text_stays_inside_the_evidence_fence`, `test_an_obeyed_log_injection_still_cannot_act`, `test_evidence_cannot_close_the_fence_early` |
| Prompt injection in a runbook | Risk, rollback, and approval come from the catalogue, not the model or the document. | `test_an_obeyed_runbook_injection_cannot_lower_risk_or_skip_approval` |
| Arbitrary shell commands | Only the 11 catalogue actions can pass validation. The model never calls tools, and the tool guard refuses unknown tools. | `test_the_tool_layer_refuses_a_tool_that_isnt_allowed`, `test_actions_outside_the_catalogue_are_rejected` |
| Database changes | No such action exists. A write tool can't be declared without requiring approval. | `test_a_database_change_is_not_an_action`, `test_a_write_tool_cannot_be_declared_without_approval` |
| Secrets in retrieved content | Credentials are redacted in tool results, documents, the request, the description, and approval comments, before the model, checkpoints, or audit see them. | `test_no_credential_reaches_the_model_the_checkpoint_or_the_audit` |
| Tool loops | The graph fixes which tools run. Each tool has a per-investigation call limit, and each graph run a step limit. | `test_the_model_cannot_make_tools_run_again`, `test_a_tool_stops_at_its_call_limit`, `test_a_run_that_exceeds_the_step_limit_stops` |
| Invented evidence | The schema limits citations to gathered IDs, and code checks them again. | `test_a_diagnosis_citing_invented_evidence_is_refused`, `test_an_action_citing_invented_evidence_is_rejected` |
| Approval bypass | The graph only leaves the pause with a validated decision. A request can't arrive approved, a decision body can't choose its own outcome, and a second decision gets 409. | `test_a_request_cannot_arrive_already_approved`, `test_a_model_claiming_approval_still_waits_for_a_person`, `test_a_forged_decision_without_an_approver_is_refused`, `test_resuming_without_a_decision_keeps_it_paused`, and in `tests/integration`: `test_an_investigation_cannot_be_decided_twice`, `test_a_decision_that_loses_a_race_is_a_conflict` |
| Stale runbooks | Retrieval filters to current documents inside the search. | `test_a_superseded_runbook_is_never_retrieved` |
| Unsupported, confident diagnoses | The model can't set confidence. Below 0.65, FlowGuard abstains and proposes nothing. | `test_a_confident_claim_without_support_abstains`, `test_a_model_cannot_set_its_own_confidence` |
| A tampered checkpoint file | Loading rebuilds only allowlisted classes; anything else stays a plain dictionary. | `test_a_paused_investigation_survives_a_restart` |
| Leaking internals in errors | A crash returns only an error ID; validation errors never repeat the rejected value. | `test_an_audit_failure_is_an_error_that_reveals_nothing`, `test_a_body_that_is_not_an_object_is_not_repeated` |

The evaluation checks the same properties on real model output: across five incidents with `gemma4:12b`, the unsafe-action and approval-bypass rates were zero, and validation refused one or two unsafe proposals per run.

## Risks that remain

These are accepted for the MVP, and are the first things to address before real use.

- **No authentication or authorisation.** Anyone who can reach the API can start investigations, read records, and approve plans; the approver's name is whatever the caller sends. Run it only on a trusted network.
- **The audit trail is append-only by code, not by cryptography.** Someone with access to the SQLite file could edit it. A hash chain or a write-once store would make tampering detectable.
- **Redaction is pattern-based.** It catches common credential formats, not every secret. A secret in an unusual format would pass through.
- **No rate limiting.** Each investigation takes about a minute of model time, so a flood of requests would queue indefinitely.
- **The model can still be wrong.** Controls stop unsafe and unsupported actions, not wrong but valid ones: a plan can be safe and still miss the fix, as INC-004's redelivery showed. That's why a person approves every change.
- **Nothing is executed.** This removes the biggest risk, but adding execution would need its own review, starting with credentials scoped to each action.
