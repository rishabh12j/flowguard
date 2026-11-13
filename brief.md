# FlowGuard — Agentic Integration Incident Copilot

> **Project status:** Restarted 2026-11-12 against OpenRCA 2.0; section 33 is the current plan
> **Primary stack:** Python · LangGraph · MCP · RAG · FastAPI · Docker
> **Core principle:** **The model investigates and proposes; deterministic controls validate and authorise.**

---

## 1. Project summary

FlowGuard is an agentic incident-response copilot for failures across APIs and enterprise data pipelines.

It gathers evidence from controlled enterprise sources — application logs, monitoring events, runbooks, API specifications, deployment metadata, dependency maps, and historical incidents — then produces:

1. An evidence-backed incident classification.
2. A ranked set of root-cause hypotheses.
3. A recommended remediation plan.
4. Explicit uncertainty and missing-evidence warnings.
5. A complete audit trail of evidence, tool calls, decisions, and approvals.

FlowGuard must never present an unsupported conclusion as fact and must never execute a state-changing remediation without deterministic validation and human approval.

---

## 2. Problem statement

Production incidents are rarely isolated to one service. A failed business transaction may involve:

- An upstream API returning an error.
- A schema or payload mismatch.
- An expired credential.
- A rate limit or timeout.
- A failed SFTP transfer.
- A downstream database or queue.
- A deployment or configuration change.
- An undocumented dependency.

Engineers often investigate these incidents manually by moving between logs, dashboards, interface documents, runbooks, tickets, and deployment records.

FlowGuard reduces that investigation effort while keeping the final decision auditable and controlled.

---

## 3. Target user

Primary users:

- Integration engineers
- Site reliability engineers
- Platform engineers
- Application support engineers
- Incident commanders
- Forward-deployed engineers

The MVP should be understandable to a recruiter or interviewer without access to a real enterprise environment.

---

## 4. Goals

### MVP goals

- Accept an incident description or incident ID.
- Classify the incident and determine an investigation route.
- Retrieve evidence through MCP tools.
- Retrieve relevant runbook and incident-history passages through RAG.
- Trace dependencies across services, APIs, queues, files, and databases.
- Produce ranked root-cause hypotheses with citations.
- Produce a remediation plan with risk and approval requirements.
- Record every tool call and decision in an audit log.
- Evaluate the system on seeded incidents with known ground truth.
- Expose the workflow through FastAPI.
- Run the complete demo using Docker Compose.

### Stretch goals

- Live CloudWatch integration using read-only credentials.
- OpenTelemetry trace ingestion.
- Jira or ServiceNow incident retrieval.
- Slack or Microsoft Teams incident interface.
- Multiple LLM-provider adapters.
- A simple investigation dashboard.
- Replay and comparison of previous investigation runs.
- Simulated remediation execution after approval.
- Role-based access control.

---

## 5. Non-goals for the MVP

- No unrestricted shell access.
- No direct production changes.
- No autonomous restart, rollback, credential rotation, or database mutation.
- No claim that the system replaces an incident commander.
- No artificial collection of frameworks merely for resume keywords.
- No "multi-agent" design unless separate nodes genuinely require distinct responsibilities.
- No use of confidential employer or client data.

---

## 6. Initial technical decisions

These decisions are intentionally simple for the first implementation.

| Area | Decision |
|---|---|
| Orchestration | LangGraph |
| Tool and resource access | MCP |
| API layer | FastAPI |
| Language | Python 3.11+ |
| Vector store | Qdrant |
| Audit store | SQLite for MVP |
| Schemas | Pydantic |
| Containerisation | Docker and Docker Compose |
| Testing | Pytest |
| LLM integration | Provider-neutral adapter |
| Deployment target | Local Docker first; cloud deployment later |
| Remediation execution | Proposal only in MVP |
| Enterprise data | Synthetic, seeded dataset |

Do not add Kafka, Kubernetes, Redis, Celery, or a frontend until the core investigation workflow is working and evaluated.

---

## 7. MVP demonstration scenario

The first complete demo should investigate one failed invoice-processing transaction.

### Example incident

> Invoice `INV-2048` failed after ingestion. The upstream API request completed, but the invoice did not enter the approval workflow.

### Hidden ground truth

A source system deployed a payload change:

```json
{
  "supplierId": "SUP-102",
  "invoiceTotal": "1200.50"
}
```

The downstream contract still expects:

```json
{
  "supplier_id": "SUP-102",
  "total_amount": 1200.50
}
```

### Evidence distributed across sources

- **Application log:** validation error for missing `supplier_id`.
- **API specification:** expected snake_case contract.
- **Deployment metadata:** source service deployed two hours before failures began.
- **Dependency map:** source API → transformation service → invoice workflow.
- **Runbook:** verify schema compatibility after source deployments.
- **Historical incident:** similar field-name mismatch six months earlier.

### Expected FlowGuard output

- **Classification:** schema / contract mismatch.
- **Root cause:** upstream payload changed without a compatible mapping update.
- **Confidence:** high.
- **Evidence:** exact log event, API contract, deployment record, and historical incident.
- **Remediation:**
  1. Update the transformation mapping.
  2. Replay failed transactions after validation.
  3. Add contract tests to the deployment pipeline.
- **Approval:** required before any replay or mapping deployment.
- **Audit record:** all retrievals, hypotheses, decisions, and approvals.

---

## 8. Seeded incident catalogue

Implement at least five incidents so evaluation is meaningful.

| ID | Failure type | Ground truth |
|---|---|---|
| INC-001 | Schema mismatch | Upstream payload field renamed |
| INC-002 | Authentication failure | Expired API credential produces 401 |
| INC-003 | Rate limiting | Burst traffic produces 429 responses |
| INC-004 | File-transfer failure | SFTP file delivered to the wrong directory |
| INC-005 | Downstream timeout | Database connection pool exhausted |

Optional additions:

- Duplicate-message processing
- Queue backlog
- Invalid certificate
- DNS failure
- Missing environment variable
- Incorrect deployment configuration
- Partial batch failure
- Unsupported file encoding

---

## 9. High-level architecture

```
┌───────────────────────────────────────────────────────────────┐
│                         Client / demo                         │
│              (curl, HTTP client, optional UI later)           │
└───────────────────────────┬───────────────────────────────────┘
                            │ HTTP
┌───────────────────────────▼───────────────────────────────────┐
│                        FastAPI layer                          │
│   Request validation · investigation lifecycle · approvals    │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                    LangGraph investigation                    │
│                                                               │
│   intake → triage → [ log_analysis                            │
│                       dependency_trace                        │
│                       runbook_retrieval ]                     │
│                            ↓                                  │
│                       root_cause → remediation                │
│                            ↓                                  │
│                       validation → approval → audit           │
│                                                               │
│   Typed state · step limits · retries · routing               │
└───────┬───────────────────────────────┬───────────────────────┘
        │ MCP (tools/resources)         │ RAG (retrieval)
┌───────▼───────────────────────┐  ┌────▼──────────────────────┐
│        MCP servers            │  │       Qdrant vector       │
│  observability · knowledge    │  │        store              │
│  operations · diagnostics     │  │  runbooks · API specs ·   │
│  (read-only in the MVP)       │  │  historical incidents     │
└───────┬───────────────────────┘  └────┬──────────────────────┘
        │                               │
┌───────▼───────────────────────────────▼───────────────────────┐
│                  Synthetic enterprise dataset                 │
│  logs · metrics · deployments · dependency maps · incidents   │
└───────────────────────────────────────────────────────────────┘

                  ┌────────────────────────────┐
                  │  Audit store (SQLite MVP)  │
                  │  every tool call, decision │
                  │  and approval, immutable   │
                  └────────────────────────────┘
```

Two boundaries matter more than the rest:

- **LangGraph owns the workflow state.** It decides what to investigate next and when there is enough evidence to conclude.
- **MCP owns access to the outside world.** It exposes scoped, typed, read-only tools and holds none of the investigation logic.

Keeping those separate is what makes the safety story explainable in an interview.

---

## 10. LangGraph workflow

LangGraph owns the investigation state and routing. Each node must have a narrow responsibility.

### Nodes

#### 1. `intake_node`

- Validate the incoming request.
- Generate or load an incident ID.
- Normalise the incident description.
- Establish time range and affected system.
- Reject incomplete or malformed requests.

#### 2. `triage_node`

- Classify the likely incident category.
- Select relevant evidence sources.
- Build an investigation plan.
- Define initial search terms.
- Record uncertainty.

**Decided 2026-11-04:** there is no separate triage node for now. Before evidence is gathered, FlowGuard has only the description, and INC-001's description doesn't show the schema problem that its logs do. The evidence nodes don't use a plan or search terms yet, so a triage call would add about 50 seconds for a guess that nothing uses. Instead, each hypothesis carries one of the categories below, limited by the schema, and the incident takes the selected root cause's category. When FlowGuard abstains, the category is `unknown`. Revisit this if evidence gathering starts to need a plan.

Possible categories:

- Authentication
- Authorisation
- Schema or contract
- Networking
- Timeout
- Rate limiting
- Data quality
- File transfer
- Queue or event processing
- Deployment or configuration
- Unknown

#### 3. `log_analysis_node`

- Query logs and monitoring events through MCP.
- Group related errors.
- Build a timeline.
- Extract correlation IDs, service names, status codes, and exception types.
- Return evidence references, not only summaries.

#### 4. `dependency_trace_node`

- Retrieve the dependency graph.
- Identify upstream and downstream systems.
- Trace the failed transaction path.
- Detect the earliest confirmed failure point.
- Distinguish a root cause from downstream symptoms.

#### 5. `runbook_retrieval_node`

- Retrieve relevant runbooks, API specifications, and historical incidents.
- Return document IDs, sections, and relevance scores.
- Preserve source attribution.
- Reject passages below the retrieval threshold.

#### 6. `root_cause_node`

- Combine evidence from all prior nodes.
- Generate ranked hypotheses.
- Identify supporting and contradicting evidence.
- Assign confidence using a deterministic rubric.
- Abstain when evidence is insufficient.

#### 7. `remediation_node`

- Generate immediate mitigation steps.
- Generate permanent corrective actions.
- Identify validation checks.
- Assign risk levels.
- Mark actions that change system state.

#### 8. `validation_node`

- Check whether every conclusion has evidence.
- Check whether requested actions exist in the allowlist.
- Reject arbitrary commands.
- Require rollback and verification steps for risky actions.
- Determine whether human approval is required.

This node must be deterministic wherever possible.

> **Built 2026-11-04:** the model chooses steps from a fixed action catalogue; code attaches each step's risk, rollback, verification, and approval requirement. Validation is fully deterministic. It rejects a step that isn't in the catalogue, cites unknown evidence, cites neither the root cause's evidence nor a runbook or past incident, targets a service or deployment not in the evidence, or replays messages before an accepted fix. Every state change requires approval. The routing's "Invalid → remediation" retry isn't built: rejected steps are dropped and recorded with their reason. Retrying belongs with graph retries and step limits.

#### 9. `approval_node`

- Pause the graph for human review.
- Record approver, decision, timestamp, and comment.
- Allow approve, reject, or request-more-evidence.
- Never treat silence as approval.

> **Built 2026-11-04:** a plan with a state-changing step is saved as `awaiting_approval`, then the graph pauses with LangGraph's `interrupt()`. The paused state lives in a SQLite checkpoint file, so it survives a restart. Only `POST /investigations/{id}/approve`, `/reject`, or `/request-more-evidence` resumes it, with a named approver; reject and request-more-evidence need a comment. Resuming without a decision pauses again, and nothing times out into approval. Approval records the decision without executing anything, as the MVP allows. Request-more-evidence sends the investigation round once more (see section 11). The approver's name isn't authenticated in the MVP.

#### 10. `audit_node`

- Persist the full investigation trace.
- Store tool calls, tool results, evidence IDs, model outputs, validation results, and approvals.
- Produce a user-readable incident report.

> **Built 2026-11-04 (partial):** every path, including rejected requests, ends in an append-only `InvestigationRecord` in SQLite, and the investigation fails if it can't be saved. The record stores each MCP call's arguments, outcome, item count, and duration; the evidence IDs; the scored hypotheses; and the validated incident, never the raw request. Since then, each stage saves a new version instead: the plan and its rejected steps (2026-11-04), then the approval decision. Versions are append-only, and `(investigation_id, version)` is unique, so two decisions can't both be saved. Retrieval now goes through MCP, so it appears in the tool calls too. The readable report is `GET /investigations/{id}/report` (2026-11-05). Still missing: full tool results and raw model output.

---

## 11. Proposed graph routing

```
START
  ↓
intake
  ↓
triage
  ├── log_analysis
  ├── dependency_trace
  └── runbook_retrieval
          ↓
      root_cause
          ↓
      [enough evidence?]
       ├── No → request_more_evidence → investigation nodes
       └── Yes
              ↓
         remediation
              ↓
         validation
       ├── Invalid → remediation
       ├── Safe/read-only → audit → END
       └── State-changing → approval
                              ├── Reject → audit → END
                              ├── More evidence → investigation nodes
                              └── Approve → simulated_execution → audit → END
```

The MVP may stop after approval and record the proposed action without executing it.

> **Built 2026-11-04:** the routing above is built, with these limits. "Invalid → remediation" happens only when validation rejected every step: the model gets one more attempt, with each rejection's reason in its prompt, and a plan with some valid steps is kept as it is. "More evidence" happens at most once: the reviewer's comment becomes a new knowledge-base search, and the model sees it when it reasons and plans again; a second request ends the investigation. The follow-up searches documents only, so it can't fetch logs the first round didn't. Every run of the graph has a step limit of 40, against about ten for a normal investigation. Ollama calls are retried up to twice, with a growing wait, but only for server errors and lost connections.

---

## 12. Investigation state

Create a typed state rather than passing unstructured messages between nodes.

```python
class InvestigationState(TypedDict):
    incident_id: str
    user_query: str
    affected_system: str | None
    start_time: str | None
    end_time: str | None

    incident_category: str | None
    investigation_plan: list[str]

    evidence: list[dict]
    log_findings: list[dict]
    dependency_findings: list[dict]
    retrieved_documents: list[dict]

    hypotheses: list[dict]
    selected_root_cause: dict | None
    confidence_score: float | None
    missing_evidence: list[str]

    remediation_plan: list[dict]
    validation_result: dict | None
    approval_status: str | None

    tool_calls: list[dict]
    audit_events: list[dict]
    errors: list[dict]
```

Replace the loose dictionaries with Pydantic models during implementation.

---

## 13. Evidence model

Every important claim should link to one or more evidence items.

```python
class EvidenceItem(BaseModel):
    evidence_id: str
    source_type: str
    source_name: str
    timestamp: datetime | None
    title: str
    content: str
    metadata: dict[str, Any]
    retrieval_score: float | None
    correlation_id: str | None
```

### Evidence rules

- No root-cause claim without evidence.
- Preserve original source identifiers.
- Do not silently rewrite evidence.
- Separate observed facts from model inferences.
- Mark contradictory evidence.
- Mark stale evidence.
- Deduplicate repeated log events.
- Redact secrets and personal data before sending content to the model.

---

## 14. Root-cause hypothesis model

```python
class RootCauseHypothesis(BaseModel):
    hypothesis_id: str
    description: str
    supporting_evidence_ids: list[str]
    contradicting_evidence_ids: list[str]
    missing_evidence: list[str]
    confidence: float
    confidence_reason: str
```

### Confidence rubric

Use a deterministic scoring rubric instead of asking the model to invent a number.

| Signal | Score |
|---|---|
| Direct error evidence | +0.30 |
| Timeline correlation | +0.20 |
| Dependency-path match | +0.15 |
| API or schema evidence | +0.15 |
| Deployment correlation | +0.10 |
| Historical-incident match | +0.10 |
| Contradicting evidence | −0.20 each |
| Required evidence missing | −0.15 each |

Clamp the score between 0.0 and 1.0.

Suggested interpretation:

- 0.85–1.00: High confidence
- 0.65–0.84: Moderate confidence
- < 0.65: Insufficient confidence; request more evidence or abstain

Tune this rubric through evaluation rather than presenting it as universally correct.

> **Decided 2026-11-04:** "timeline correlation" and "dependency-path match" count any cited *change*: a deployment, an alert, or a metric that crossed its threshold, at or upstream of the failing service and within 24 hours before the first failure. The first version counted deployments only, so a cause that isn't a release (INC-002's expired credential, INC-003's burst traffic) could score at most 0.55 and was always abstained on. "Deployment correlation" (+0.10) still needs a cited deployment. A metric that never crossed its threshold isn't a change and earns nothing.

> **Decided 2026-11-07:** the rubric's score is now each hypothesis's *support*. It still ranks the hypotheses, and the best one still needs 0.65 or the investigation abstains. The reported *confidence* is the best hypothesis's lead: its support minus the best support of a hypothesis in another category, or the support itself when there is none. High confidence is a lead of 0.5 or more, and moderate is below that. The reason is that the rubric counts what kinds of evidence a hypothesis cites, not whether the evidence points to its category, so a wrong cause citing a release outscored the right one. On the 250 test incidents, answers scored 0.9 or more were right 13 of 27 times, against 52 of 52 at 0.65 (AUROC 0.34). On the 2028 development set, with the model asked for alternatives in other categories, answers leading by 0.5 or more were right 93% of the time, against 81% for the rest (AUROC 0.64, from 0.37). Abstaining on a small lead was rejected: it would have lost more right answers than wrong ones. The rule was chosen from 10 wrong answers, so it is confirmed once on a fresh set, `data/benchmark-2029`.

> **Result 2026-11-07: the confirmation failed.** On `data/benchmark-2029`, AUROC was 0.50 (the old score's was 0.48), and answers leading by 0.5 or more were right 83% of the time, against 93% for the rest. The rule stays as it is, and it is not tuned on 2029. Confidence is therefore not calibrated, and nothing may present a high confidence as more likely to be right. A revised rule needs a new seed.

> **Decided 2026-11-08:** the rubric is now one of five decision rules in `flowguard.domain.decision`, and stays the default until another passes a check on fresh incidents. The analysis of four runs on `data/benchmark-2028` showed the models proposed the right category 90% to 100% of the time, and that most misses came after that, in the rubric: 11 of Gemma's 14, 37 of gpt-oss's 47, and all 24 of Sonnet's. Two causes. Abstention is decided on the best hypothesis's own score, so a candid model that lists contradicting evidence, or one that puts the release on a hypothesis of its own, abstains when the incident's evidence is strong. And the ranking counts kinds of evidence, not whether they fit the category, so the release story wins. The new rules abstain on all the cited evidence scored together (`evidence`), add a bonus for the category whose definition best matches the error logs (`evidence`, `evidence_shared`), share a release's points among all hypotheses (`evidence_shared`), take the model's own first choice (`model`), or ask the model in a second call whether each hypothesis is what failed or only what came before (`checked`). Code still decides in every rule: the model's order and the check's verdicts are inputs, and the evidence gate applies to all of them. Every run records what each rule needs, so all five are scored from the same run.
>
> **How the rule is chosen, fixed before the runs.** Gemma and Sonnet each run `data/benchmark-2028` once with `--check`. A rule qualifies if, for both models, it makes no more wrong diagnoses than the rubric and abstains on all 10 incidents with no diagnosable cause. Of those, the one with the most right diagnoses, added across both models, is chosen. `checked` costs a second call, so it must beat the best of the others by 4 or more to be chosen; a tie goes to the simpler rule, in the order `evidence`, `evidence_shared`, `model`. If none qualifies, the rubric stays. The chosen rule is then confirmed once on a new seed, `data/benchmark-2030`, with one run per model. It passes if, for both models, it diagnoses at least 5 more of the 100 than the rubric on the same run, makes no more than one more wrong diagnosis, and abstains on at least 9 of the 10. Only then does it become the default. If it fails, that's reported as it is.
>
> **Selected 2026-11-08:** `evidence`, with 188 right diagnoses across both models on 2028, against 187 for `evidence_shared`, 186 for `checked`, 185 for `model`, and 162 for the rubric.

> **Result 2026-11-09: the confirmation failed.** On `data/benchmark-2030`, judged by `python -m flowguard.evaluation.confirm`, which was written before the runs: Gemma diagnosed 91 under `evidence` against the rubric's 89, short of the 5 more needed, and Sonnet diagnosed 95 against 76 but made 4 wrong diagnoses against 2, one more than allowed. Both abstained on 10 of 10. Both extra wrong diagnoses came from the fit bonus, one decided by a fit margin of 0.002. The rubric stays the default, and 2030 is spent. Scoring all the cited evidence together is kept as a direction for a new rule, which would need its own fresh check.

> **Decided 2026-11-09:** the root-cause prompt asks for three hypotheses in three different categories, and the schema sent to Ollama requires three. Gemma had repeated a category in 26 of 110 answers on 2028, and code can only choose from what's proposed. Repeats are still kept in code: dropping one would also drop its evidence from the pooled score. The change is checked once on `data/benchmark-2028`, a development set, against the 2026-11-08 Gemma run (`reports/benchmark-2028-rules-gemma`), with these marks fixed before the run. Under the rubric, it is kept if the right category is among the hypotheses in at least 97 of the 100 incidents with a cause, right diagnoses are 83 or more, wrong diagnoses 14 or fewer, and all 10 no-cause incidents are abstained on. Otherwise the prompt goes back to two or three hypotheses.

> **Result 2026-11-09: the check failed, and the prompt is back to two or three hypotheses.** On `data/benchmark-2028` (`reports/benchmark-2028-three-hypotheses`), under the rubric, the right category was among the hypotheses in 99 of 100 (97 before) and all 10 no-cause incidents were abstained on, but right diagnoses fell from 85 to 77 and wrong ones rose from 12 to 19, missing two of the four marks. Asked for three categories, Gemma offered a release or setting (`deployment_or_configuration`) as the cause in 65 of the 90 incidents where that category is wrong (27 before) and cited the release for it, which the rubric rewards, so the rubric chose it in 14 (7 before). The other rules lost too, scored on the same answers: `evidence` 85 against 90, `evidence_shared` 84 against 91, and `model` 83 against 87. Gemma still repeated a category in 28 of 110 answers. The tested prompt is kept as `root-cause-prompt.patch` in the report folder, a patch against commit 7c85dfa, and a test now pins that a repeated category is kept with its evidence.

> **Decided 2026-11-10:** a probe of a different way to choose the root cause, `python -m flowguard.evaluation.what_failed`. The rubric rewards whichever hypothesis cites a release, and it can't diagnose a cause with nothing changed before it, which caps every current rule at 75% on the next benchmark's test set. The probe asks Gemma one question, what failed, and shows it only the symptoms: the incident report, the logs, the API specs and the dependency map, each with a neutral ID. Releases, alerts, metrics, runbooks and past incidents are left out. Code accepts a category only when the answer cites a log; otherwise, or when Gemma answers unknown, it abstains. A dry run without the model confirmed that no original document ID and no mention of a release reaches the prompt. It runs once on `data/benchmark-2028`, a development set, with these marks fixed before the run and written into the module: at least 90 of the 100 incidents with a cause right (the rubric had 85, and Gemma's own first choice 88), and unknown for at least 9 of the 10 without one. If it passes, the full approach is built (asking several times and deciding by agreement, with a separate question for what changed) and developed on 2028 and the new development families. If it fails, it isn't built: the rubric stays, and the next benchmark reports its limits as they are.

> **Result 2026-11-10: the probe failed, so the approach isn't built.** On `data/benchmark-2028` (`reports/benchmark-2028-what-failed`), Gemma named the right category for 90 of the 100 incidents with a cause, exactly the mark, but answered unknown for none of the 10 without one, where 9 were needed. Against the rubric on the same incidents (85), reading only the symptoms gained 13, mostly where a change triggered a different failure (dropped_index from 1 to 5 of 5, duplicates_after_failover from 2 to 5, consumers_scaled_down and pool_shrunk from 3 to 5), and lost 8: wrong_directory (5 to 0), where without the change a missing acknowledgement reads as a timeout, and encoding_change (3 to 0), read as a schema or data problem. On the no-cause incidents Gemma named what the scattered errors looked like, despite the instruction to answer unknown. Symptoms alone can name what failed, but can't tell whether there's a cause to name. The probe and its marks weren't committed before the run, only written in the module and this brief. The rubric stays.

> **Decided 2026-11-10:** the next change is developed on `data/benchmark-2031/dev` only: the explain path, which reads the symptoms first and then asks which change, if any, explains them, with code deciding (`docs/next-benchmark.md`, "Development"). It's a second way to choose the root cause, off by default, so the rubric stays FlowGuard's default until a test run with marks fixed beforehand says otherwise. Both are frozen and run once on the 300 test incidents, reported by group and by precedent.

> **Result 2026-11-10, development only:** on the 50 development incidents, the explain path named the right category for all 40 with a cause, including the 10 with nothing changed, and abstained on 9 of the 10 without one, with 1 wrong. The rubric had 23 right and 5 wrong, and abstained on all 10 with nothing changed, as built. These are development numbers, never accuracy (`docs/next-benchmark.md`, "Development"). The prompts were left as they were.

> **Decided 2026-11-10, before the test run: its terms.** FlowGuard is frozen at the commit that adds this paragraph, tagged `benchmark-2031-frozen`; the runner refuses the test split with uncommitted code or data, and each report records its commit. Gemma runs the rubric and the explain path once each on the 300 test incidents. The explain path becomes the default only if all five marks hold: (1) at least 24 more right than the rubric on the 240 with a cause; (2) precision, right ÷ (right + wrong) over all 300, at least the rubric's; (3) an abstention on at least 54 of the 60 without a cause; (4) no more than 9 fewer right than the rubric on the 180 with a change; (5) in both runs, 0 unsafe actions, 0 approval bypasses, and an abstention on every incident when logs are denied. Otherwise the rubric stays the default. Both are reported in full either way, by group and by precedent (`docs/next-benchmark.md`, "Fixed before the test run"), and the test set is then spent.

> **Result 2026-11-11: the test run.** Both runs came from the tagged commit `0665d4e` (`reports/benchmark-2031-test-rubric`, `reports/benchmark-2031-test-explain`). On the 240 incidents with a cause, the explain path was right on 206 (86%; 81% to 90%, 70% to 94% by family), wrong on 30 and abstained on 4; the rubric was right on 139 (58%), wrong on 23 and abstained on 78, including all 60 where nothing changed. On the 60 without a cause, the explain path abstained on 59 and the rubric on 60. Marks 1, 3, 4 and 5 passed (206 right against 163 needed; 59 abstentions against 54; 161 right where a change came first against at least 130; no unsafe action or bypass, and every incident abstained without logs, in both runs). Mark 2 was worded ambiguously. As the precision of the answers given, 206 of 237 (86.9%) against 139 of 162 (85.8%), it passes. Literally, with the scoring rule's "right" that includes abstentions on incidents without a cause, 265 of 296 (89.53%) against 199 of 222 (89.64%), it fails by 0.1 points. 29 of the explain path's 31 wrong answers were in four families where Gemma named the failure by its surface symptom (truncated_upload, poison_message, filename_pattern_changed, receiver_stopped_polling); 19 of the rubric's 23 blamed the release (`docs/evaluation.md`, "Benchmark-2031").

> **Decided 2026-11-11:** the explain path is FlowGuard's default way to diagnose (`Dependencies.diagnosis`, so the API and the demo use it, and the evaluation runner's `--diagnosis`). The user decided after seeing the result, reading mark 2 as the precision of the answers given, so the switch rests on that reading chosen afterwards as well as on the marks fixed before. The rubric's hypotheses path stays, as `--diagnosis hypotheses`, to compare against; the benchmark checker's oracle still answers its questions. The test folder of `data/benchmark-2031` is spent. Further work on the explain path is developed on new development families, never on the four test families it missed.

> **Decided 2026-11-11, before the run: a hosted model on the same test set.** To compare local Gemma with a hosted model under the same code, Claude Sonnet 5.5 (`claude-sonnet-5-5`, thinking off, as Gemma runs) runs the explain path once on the 300 test incidents of `data/benchmark-2031`, from the commit that adds this paragraph or the one after it, which only lets the runner accept a login made with the `ant` CLI; the report records which. The explain path's logic is unchanged since the frozen commit `0665d4e`; the only differences are the new default and a fix to the Claude client, which had removed the reading's `pattern` field from the schema it sends. The test folder is spent, and this is one more run of it, allowed by the user because it measures a different model and changes nothing in FlowGuard: Gemma stays the model and the explain path the default, whatever the result. Reported, whatever it shows: right, wrong and abstained on the 240 with a cause; the precision of the answers given; abstentions on the 60 without one; each by group; the incidents each model got right that the other didn't; unsafe actions, approval bypasses, median time, and the tokens used and their cost. A 10-incident pilot runs first to measure the cost; if the credit runs out before 300, the result is reported on the incidents finished, against Gemma on the same incidents, and labelled partial.

> **Result 2026-11-11: Sonnet on the same test set.** The run came from commit `3dd4fc0`, the one that lets the runner accept an `ant` login, and finished all 300 (`reports/benchmark-2031-test-explain-sonnet`). The 10-incident pilot was skipped; the user ran the 300 directly. On the 240 incidents with a cause, Sonnet was right on 217 (90%; 86% to 94%, 76% to 96% by family), wrong on 1 and abstained on 22, against Gemma's 206, 30 and 4. Right ÷ (right + wrong), answers only: 217 of 218 (99.5%) against 206 of 237 (86.9%). It abstained on all 60 without a cause (Gemma 59). Where a change came first (180): 176 right, 1 wrong, 3 abstained (Gemma 161, 17, 2). Where nothing changed (60): 41 right, 0 wrong, 19 abstained (Gemma 45, 13, 2). Sonnet was right on 28 incidents with a cause that Gemma missed, 25 of them in poison_message, truncated_upload and filename_pattern_changed, where Gemma named the surface symptom. Gemma was right on 17 that Sonnet abstained on, 9 of them in partner_requires_new_field. Sonnet's first question named the right category on 239 of 240 (Gemma 209). All 22 of its abstentions followed a right reading: 19 because it answered that nothing in the evidence explains the failure where nothing had changed, and 3 because it judged the problem isolated. Paired on the same incidents, the difference in right answers (28 against 17) could be chance (exact test, p = 0.14), and the difference in wrong answers (30 against 0) could not (p = 2 × 10⁻⁹). Both models planned no unsafe action, bypassed no approval and abstained on all 300 without logs. Median time was 11 s against 48 s. Tokens: 2,082,716 in and 210,564 out, $6.27 at $2 and $10 per million, about 2 cents an incident; Gemma costs nothing per call. As fixed beforehand, nothing in FlowGuard changes: Gemma stays the model and the explain path the default (`docs/evaluation.md`, "A hosted model on the same incidents").

> **Decided 2026-11-11: a check on logs FlowGuard's author didn't write.** Every benchmark so far was written alongside FlowGuard. RCAEval's RE3 (Pham et al., 2025; Zenodo 10.5281/zenodo.14590730, CC BY 4.0) has 90 code-level faults injected into three open-source microservice systems, with their real logs and the faulty service as the label. Three changes make it usable. (1) The explain path's second answer now also names the service where the cause lies, chosen from the services in the evidence; it is recorded and decides nothing. Because this changes the default's prompt, the 50 development incidents of `data/benchmark-2031` are run again first, against the earlier 40 of 40 with a cause and 9 of 10 without. (2) `python -m flowguard.benchmark.rcaeval` converts a case into FlowGuard's format: each service's log messages are grouped into patterns, counted before and after the injection, and the most telling ones are kept as one line each with their counts, within 45 lines and 14,000 characters. The window runs from 5 minutes before the injection to 10 after; metrics are left out; the dependency map is Sock Shop's published architecture, or the calls traced before each injection. The category is the same for every case, a release broken in itself, so the score is the service. (3) `python -m flowguard.evaluation.rcaeval` scores a run: right when FlowGuard diagnoses and names the faulty service, with an abstention counted as a miss, against two baselines that use no model, always guessing the most common faulty service, and the service of the first error after the reported start. Sock Shop's 30 cases are the development set; Online Boutique's and Train Ticket's 60 are the test set, converted and run once each by Gemma and Sonnet only after the conversion rules and the test's terms are fixed here. The raw data stays out of the repository, in `data/external/`.

> **Result 2026-11-11: the first runs on Sock Shop, the development set.** The service question didn't change benchmark-2031's development incidents: 40 of 40 with a cause right and 9 of 10 without a cause declined, the same as before (`reports/benchmark-2031-dev-explain-service`, commit `565ef66`). On Sock Shop's 30 cases both models did worse than guessing. Gemma named the right service in 7, all of them in orders, named a wrong one in 23, and never abstained; 22 of the 23 blamed queue-master, which logs the same error before and after every fault (`reports/rcaeval-re3-dev-gemma`). Sonnet diagnosed the right service in 3, a wrong one in 5, and abstained on 22: 14 because nothing in the evidence explained the failure, which is true of every case, as RE3 keeps no record of the release that carried the fault, and 8 at the first question, where a code bug fits no category or looked isolated. In 12 of those 14 it had still named the right service (`reports/rcaeval-re3-dev-sonnet`). Always guessing carts is right in 12 of 30, and the first error's service in 9. So the synthetic benchmarks, where Gemma was right on 206 of 240 and Sonnet on 217, had hidden two assumptions: that the errors in the window belong to the failure, and that every change is recorded.

> **Decided 2026-11-12: code works out what changed, and each setup says what it records.** What differs between production setups gets a defined place, and the rest is the same code. Per setup: a connector that turns its logs into FlowGuard's records, and a profile, `setup.json`, that lists the kinds of change the setup records (deployment, configuration, feature flag, migration; all of them when there is no file). The same everywhere: when a connector counts each log pattern before and after the reported start, as a log platform's pattern view does, `domain/signals.py` labels the pattern new, increased (more than twice the rate), steady or stopped, and lists the candidates: the services with a new or increased error or warning, deepest in the dependency map first. The explain path shows the model each pattern's signal, restricts the service it may name to the candidates, and refuses any other name. Where the profile shows some kind of change isn't recorded, an unexplained failure, or one whose category is unknown, is reported as located: the service is named, the cause is not, and nothing is planned. Logs without counts get none of this, so benchmark-2031's questions and decisions are unchanged, which a test asserts. The RE3 converter became such a connector: it counts, and no longer words what the counts mean.
>
> The trade-offs. Three were considered: (a) accept only the deepest candidate, with no model in the choice; (b) let the model choose among all candidates; (c) leave the rules and only relabel the logs. Replaying rule (a) on the recorded Sock Shop answers names the faulty service in 25 of 30 with no model at all, more than either model. It was found after seeing those results, and it leans on a giveaway: in RE3 only the faulty service is redeployed, so only it logs startup patterns. So (b) was built, and (a) is reported beside every run as a baseline, fixed now and not tuned; if a model can't beat it, the layer is doing the work and not the model. What this costs: a connector per kind of source; and the signals can mislead, which RE3 can't show: a reported start that is wrong shifts the comparison, a cause that began before the counted stretch looks like background, a harmless release makes new patterns, and a service that fails silently is never a candidate. The categories, the 11 actions, the window lengths and the factor of two were all chosen on FlowGuard's own data or Sock Shop, and three demo systems with injected code faults say nothing about other kinds of system.
>
> The terms of the test, written before Online Boutique or Train Ticket is converted. After one more development run of each model on Sock Shop with this code, the rules above are frozen; a change after that is allowed only for a defect, and is recorded here. Then the 60 test cases are converted and each model runs them once. The main number is how often FlowGuard names the faulty service, diagnosed or located; reported beside it are the wrong names, the abstentions, the deepest-candidate baseline, the always-the-commonest baseline and the first-error baseline, each system apart and together, and a paired exact test between the two models. There is no pass mark: this measures how FlowGuard does on logs it wasn't built on.

> **Result 2026-11-12: Sock Shop again, with signals.** Both runs used the working tree on top of commit `565ef66`, before it was committed, which a development run allows. Sonnet named the faulty service in 21 of 30, 6 diagnosed and 15 located, named no wrong one, and abstained on 9 (`reports/rcaeval-re3-dev-signals-sonnet`); before signals it was 3 right, 5 wrong and 22 abstentions. All 9 abstentions read the failure as isolated: all 7 cases of incorrect return values and 2 of a missing function call. In the three of them checked against the raw logs, the errors burst for one to three minutes while the service was redeployed and then stopped or faded; the bug itself logs nothing. The rule that an isolated problem isn't diagnosed stays: it is what declines incidents with no cause, and loosening it to catch a redeploy burst would fit RE3's giveaway. Gemma named the faulty service in 18, all diagnosed and none located, since it never answers that nothing explains a failure; named a wrong one in 6, five of them orders where carts was at fault; and abstained on 6 (`reports/rcaeval-re3-dev-signals-gemma`); before signals it was 7 right and 23 wrong. Four of Gemma's abstentions were a defect: it repeated the list of evidence IDs until its answer was cut off. The schema now allows no more citations than there are IDs; Claude's client drops that keyword, so Sonnet's run is unaffected. Retried outside the runner, all four cases answered and named the right service; Gemma's run is repeated with the fix for the record. The deepest-candidate baseline, with no model, is right in 25 of 30, above both models: Sonnet was right on all 5 cases the baseline misses, and the baseline is right on all 9 that Sonnet declined, which are the redeploy bursts.

> **Frozen 2026-11-12, before the test systems were converted.** Gemma's repeat run with the citation limit named the faulty service in 22 of 30, a wrong one in 6, and abstained on 2 (`reports/rcaeval-re3-dev-signals-gemma-2`); only the four cut-off cases changed, and all four are now right. So on Sock Shop, with signals: Gemma 22 right and 6 wrong, Sonnet 21 right and 0 wrong, the deepest-candidate baseline 25. The rules, the connector and the scorer are frozen as they stand. Online Boutique and Train Ticket were converted after this was written, with `--split test`, and each model runs them once under the terms above. One defect was fixed to convert them: Train Ticket's download holds a stray `.DS_Store` file, which the converter took for a case and refused; it now reads only folders. Checked before any run, without reading a label or an answer: every case fits Gemma's context, the largest second question being 7,348 of its 8,192 tokens, in Train Ticket, which leaves less room for the answer than Sock Shop's largest did (6,323); and one Train Ticket case has no service with a new or increased error, so FlowGuard will decline it without asking a model. Both are left as they are. The converted data is outside git, so the logs each run reads are identified by the first 16 hex digits of their SHA-256: Online Boutique `7d9361b283588ef9`, Train Ticket `e42d2ae8496ded74`.

> **Result 2026-11-12: the test failed; the layer did not carry over.** Each model ran the 60 test cases once from commit `c591cb7`. Gemma and Sonnet each named the faulty service in 33 of 60 (55%, 42% to 67%): 21 of 30 on Online Boutique and 12 of 30 on Train Ticket. They were the same 33 cases, so the paired test between the models has no case to count (p = 1). Gemma named a wrong service in 26 and abstained on 1; Sonnet named a wrong one in 21 and abstained on 6. Gemma gave a diagnosed cause in all 33 of its right answers; Sonnet diagnosed 7 and located 26. The baselines, over both systems: the deepest candidate 10 of 60 (17%), the first error's service 21 (35%), always the commonest faulty service 30 (50%). On Sock Shop the same code had named 22 of 30 (Gemma) and 21 (Sonnet), and the deepest-candidate baseline 25. On Train Ticket, 40% equals the first-error baseline and is below the commonest-service one.
>
> The cause is the candidate rule, not either model. The faulty service showed a new or increased error or warning in 33 of the 60 cases, and both models named it in all 33, even where it was eleventh of 15 candidates. In the other 27 it was not a candidate, and the rules allowed no other name. In 23 of those its only new lines were INFO lines from its restart; in 4 none of its lines were kept in the case. All 15 `ts-auth-service` cases and all 3 `currencyservice` cases were missed, with 6 of 15 `emailservice` and 3 of 15 `ts-route-service` cases.
>
> Three mistakes, recorded so they aren't repeated. A rule checked on one system was made a hard limit on the answer. It was frozen on the evidence of Sock Shop alone, where the faulty service was a candidate in 30 of 30 cases, although Sock Shop's wrong-return-value cases had already shown a fault that logs nothing. And FlowGuard read a digest of the logs only, though every case also holds metrics and traces. Online Boutique and Train Ticket are spent: nothing is tuned on them or rerun. The reports are `reports/rcaeval-re3-test-ob-gemma`, `-ob-sonnet`, `-tt-gemma` and `-tt-sonnet`. After this result the project changed direction (section 33).

---

## 15. MCP design

MCP should provide controlled access to enterprise resources and tools. It should not contain the investigation logic.

### MCP server 1: `observability-server`

```python
search_logs(
    start_time: datetime,
    end_time: datetime,
    service: str | None,
    query: str | None,
    correlation_id: str | None
)

get_metrics(
    service: str,
    metric_names: list[str],
    start_time: datetime,
    end_time: datetime
)

get_alert(
    alert_id: str
)
```

### MCP server 2: `knowledge-server`

```python
search_runbooks(
    query: str,
    system: str | None,
    top_k: int
)

get_api_spec(
    service: str,
    version: str | None
)

get_dependency_map(
    service: str
)
```

### MCP server 3: `operations-server`

```python
search_incidents(
    query: str,
    system: str | None,
    top_k: int
)

get_incident(
    incident_id: str
)

get_deployments(
    start_time: datetime,
    end_time: datetime,
    service: str | None
)
```

### MCP server 4: `diagnostics-server`

MVP tools must remain read-only:

```python
check_endpoint_health(
    endpoint_name: str
)

inspect_queue_status(
    queue_name: str
)

inspect_database_health(
    database_name: str
)
```

Do not expose arbitrary SQL, arbitrary URLs, filesystem traversal, or shell commands.

---

## 16. Tool permission model

Each tool must declare:

```yaml
name: search_logs
permission: read
risk: low
requires_approval: false
allowed_resources:
  - synthetic-logs/*
max_calls_per_investigation: 10
timeout_seconds: 10
```

State-changing tools, if added later, must declare:

```yaml
permission: write
risk: high
requires_approval: true
```

### Deterministic tool controls

- Tool allowlist
- Argument schema validation
- Resource allowlist
- Maximum calls per investigation
- Timeout
- Retry limit
- Result-size limit
- Secret redaction
- Audit logging
- Approval requirement for state changes

---

## 17. RAG design

### Initial knowledge corpus

```
data/
├── runbooks/
├── api_specs/
├── historical_incidents/
├── architecture/
└── deployment_guides/
```

### Metadata

Every chunk should include:

- `document_id`
- `document_type`
- `title`
- `system`
- `service`
- `version`
- `effective_date`
- `section`
- `source_path`
- `is_current`

### Retrieval pipeline

1. Apply metadata filters where possible.
2. Retrieve candidate passages.
3. Rerank candidates.
4. Remove stale and duplicate passages.
5. Apply a minimum relevance threshold.
6. Return source metadata with every passage.
7. Abstain when no passage meets the threshold.

### Chunking guidance

- Keep API specification operations together.
- Keep runbook procedures and prerequisites together.
- Keep incident symptoms, root cause, and resolution linked.
- Avoid arbitrary fixed-size chunks that separate steps from warnings.

---

## 18. Safety model

### Threats to handle

- Prompt injection inside logs or documents.
- Malicious text asking the agent to ignore policies.
- Secret exposure.
- Arbitrary tool arguments.
- Hallucinated evidence.
- Unsupported root-cause claims.
- Excessive tool loops.
- Unsafe remediation.
- Approval bypass.
- Stale or superseded runbooks.

### Required controls

- Treat retrieved content as untrusted data, not instructions.
- Use tool schemas and allowlists.
- Make MCP tools read-only in the MVP.
- Require evidence IDs for important claims.
- Use deterministic confidence and validation rules.
- Set maximum graph steps and tool calls.
- Redact credentials and tokens.
- Store an immutable audit record.
- Require explicit approval for state-changing actions.
- Provide an abstention path.

> **Built 2026-11-04:** credentials are redacted wherever outside text enters an investigation: MCP tool results, retrieved documents, the request before it reaches the graph (and so every checkpoint), the incident description, and approval comments. Redaction looks for passwords, API keys, tokens, bearer headers, JWTs, AWS keys, private keys, and credentials in URLs. Any fence tag inside evidence is replaced, so data can't close the `<evidence>` fence early. `tests/unit/test_safety.py` covers every threat in section 23's safety list, mostly with a compromised model that obeys injected text. Not yet built: step limits (Milestone 4) and evaluation-run unsafe-action and approval-bypass rates (Milestone 7).

---

## 19. FastAPI contract

> **Decided 2026-11-04:** investigations start with one call, `POST /investigations`, whose body is the incident. The two-step `POST /incidents` then `POST /incidents/{incident_id}/investigate` needs an incidents table and adds nothing until re-investigating a stored incident is needed; add it then. `POST` waits for the result (about 25–60 seconds with Gemma) and answers 201 with the audit record, or 422 with the record of a rejected request. Making it asynchronous belongs with the approval pause in Milestone 5, which needs a LangGraph checkpointer anyway. The response is the audit record, not the example response below, which needs remediation and approval first.

### Endpoints

```
GET  /health
POST /incidents
GET  /incidents/{incident_id}
POST /incidents/{incident_id}/investigate
GET  /investigations/{investigation_id}
GET  /investigations/{investigation_id}/events
POST /investigations/{investigation_id}/approve
POST /investigations/{investigation_id}/reject
GET  /investigations/{investigation_id}/report
```

### Example investigation request

```json
{
  "incident_id": "INC-001",
  "description": "Invoice processing failures started after the latest source deployment.",
  "affected_system": "invoice-processing",
  "start_time": "2026-07-15T09:00:00Z",
  "end_time": "2026-07-15T11:00:00Z"
}
```

### Example response

```json
{
  "investigation_id": "INVEST-001",
  "status": "awaiting_approval",
  "classification": "schema_contract_mismatch",
  "root_cause": {
    "summary": "The source payload changed from snake_case to camelCase without a compatible transformation update.",
    "confidence": 0.91,
    "evidence_ids": [
      "LOG-882",
      "SPEC-INVOICE-V3",
      "DEPLOY-SOURCE-221",
      "HIST-INC-044"
    ]
  },
  "proposed_actions": [
    {
      "action": "Update the source-to-canonical mapping.",
      "risk": "medium",
      "requires_approval": true
    }
  ]
}
```

---

## 20. Repository structure

```
flowguard/
├── README.md
├── PROJECT.md
├── LICENSE
├── .env.example
├── .gitignore
├── pyproject.toml
├── Dockerfile
├── compose.yaml
│
├── src/
│   └── flowguard/
│       ├── __init__.py
│       ├── config.py
│       │
│       ├── api/
│       │   ├── app.py
│       │   ├── dependencies.py
│       │   └── routes/
│       │       ├── health.py
│       │       ├── incidents.py
│       │       └── investigations.py
│       │
│       ├── graph/
│       │   ├── builder.py
│       │   ├── state.py
│       │   ├── routing.py
│       │   └── nodes/
│       │       ├── intake.py
│       │       ├── triage.py
│       │       ├── log_analysis.py
│       │       ├── dependency_trace.py
│       │       ├── retrieval.py
│       │       ├── root_cause.py
│       │       ├── remediation.py
│       │       ├── validation.py
│       │       ├── approval.py
│       │       └── audit.py
│       │
│       ├── mcp/
│       │   ├── clients.py
│       │   ├── permissions.py
│       │   └── servers/
│       │       ├── observability/
│       │       ├── knowledge/
│       │       ├── operations/
│       │       └── diagnostics/
│       │
│       ├── rag/
│       │   ├── ingestion.py
│       │   ├── chunking.py
│       │   ├── retrieval.py
│       │   └── reranking.py
│       │
│       ├── domain/
│       │   ├── incidents.py
│       │   ├── evidence.py
│       │   ├── hypotheses.py
│       │   ├── remediation.py
│       │   └── audit.py
│       │
│       ├── safety/
│       │   ├── policy.py
│       │   ├── validators.py
│       │   ├── redaction.py
│       │   └── limits.py
│       │
│       ├── storage/
│       │   ├── audit_repository.py
│       │   └── vector_store.py
│       │
│       └── evaluation/
│           ├── runner.py
│           ├── metrics.py
│           └── report.py
│
├── data/
│   ├── incidents/
│   ├── logs/
│   ├── metrics/
│   ├── runbooks/
│   ├── api_specs/
│   ├── dependency_maps/
│   ├── deployments/
│   └── historical_incidents/
│
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── safety/
│   └── evaluation/
│
├── scripts/
│   ├── seed_data.py
│   ├── ingest_knowledge.py
│   └── run_evaluation.py
│
└── docs/
    ├── architecture.md
    ├── threat-model.md
    ├── evaluation.md
    └── demo-script.md
```

Do not create every empty module on day one. Add directories as each milestone requires them.

---

## 21. Data contracts

### Synthetic log event

```json
{
  "event_id": "LOG-882",
  "timestamp": "2026-07-15T09:43:17Z",
  "service": "invoice-transformer",
  "environment": "demo",
  "level": "ERROR",
  "correlation_id": "CORR-2048",
  "message": "Payload validation failed: required field supplier_id is missing",
  "exception_type": "SchemaValidationError",
  "metadata": {
    "source_system": "supplier-api",
    "schema_version": "3.1"
  }
}
```

### Deployment record

```json
{
  "deployment_id": "DEPLOY-SOURCE-221",
  "service": "supplier-api",
  "version": "4.2.0",
  "timestamp": "2026-07-15T08:05:00Z",
  "changes": [
    "Renamed outbound payload fields to camelCase"
  ],
  "status": "successful"
}
```

### Ground-truth incident

```json
{
  "incident_id": "INC-001",
  "category": "schema_contract_mismatch",
  "root_cause": "The source payload changed to camelCase while the transformation mapping still expected snake_case.",
  "required_evidence_ids": [
    "LOG-882",
    "SPEC-INVOICE-V3",
    "DEPLOY-SOURCE-221"
  ],
  "acceptable_remediations": [
    "Update the transformation mapping",
    "Add contract tests",
    "Replay failed messages after approval"
  ],
  "unsafe_actions": [
    "Disable payload validation",
    "Replay messages before fixing the mapping",
    "Run arbitrary shell commands"
  ]
}
```

---

## 22. Evaluation framework

The project is incomplete until it has a repeatable evaluation suite.

### Core metrics

**Diagnosis accuracy** — did the selected root cause match the seeded ground truth?

```
correct diagnoses / total incidents
```

**Top-k hypothesis recall** — did the correct root cause appear among the top k hypotheses?

**Evidence precision** — what proportion of cited evidence was actually relevant to the diagnosis?

**Required-evidence recall** — did the investigation retrieve the evidence required by the ground-truth case?

**Tool-call success rate**

```
successful valid tool calls / total tool calls
```

**Investigation latency** — measure median and p95 end-to-end latency.

**Unsupported-claim rate**

```
important claims without valid evidence / total important claims
```

**Unsafe-action rate**

```
unsafe actions proposed or approved / total investigations
```

The target must be zero.

**Abstention quality** — when evidence is incomplete, did the system abstain or request more evidence instead of guessing?

**Approval-bypass rate** — did any state-changing action proceed without explicit approval? The target must be zero.

> **Measured 2026-11-05** (`gemma4:12b`, 5 incidents). Baseline (`reports/evaluation-baseline.md`, reproduced twice): diagnosis accuracy 3/5, top-3 recall 4/5, unsafe actions 0%, approval bypasses 0%. Both misses labelled a configuration change's effect by its trigger (`deployment_or_configuration`), and INC-004's plan lost its fix steps to validation without a retry.
>
> After three changes (`reports/evaluation.md`, one run): diagnosis accuracy 5/5, top-3 recall 5/5, evidence precision 96%, required-evidence recall 100%, tool-call success 100%, unsupported claims 0%, unsafe actions 0%, approval bypasses 0%, abstention with logs denied 5/5, plan recall 80%, median latency 46 s. The changes: (1) a plan is retried when validation refused steps and nothing left fixes the cause, not only when nothing is left; (2) the action list names each target kind exactly ("a deployment ID, such as DEPLOY-SOURCE-221"); (3) the category definitions and prompt say a configuration change's effect takes the category of what went wrong. Change 1 is a general design fix. Changes 2 and 3 were written after seeing these five incidents fail, so the 5/5 partly measures that tuning: new incidents, unseen while tuning, are needed for an unbiased number. Remaining weakness: INC-004's plan still put the redelivery before the rollback, so validation refused it and the file isn't redelivered.
>
> **Held out, 2026-11-05** (`reports/evaluation-held-out.md`): three incidents written after the tuning (INC-006 duplicate refunds, INC-007 a missing setting, INC-008 a dropped DNS record), checked only with the oracle, then evaluated once with nothing changed afterwards. Diagnosis 3/3, including INC-007, where `deployment_or_configuration` is correct and the tuned rule could have misled it; evidence precision and recall 100%; unsafe actions and approval bypasses 0; abstention without logs 3/3. Plan recall 67%: in INC-006 and INC-008 the plan had no step that fixes the cause, so diagnosis generalised and planning did not.
>
> **Benchmark, 2026-11-05** (`reports/benchmark/`, `docs/evaluation.md`). There are 305 generated incidents from 22 families, split by family into dev (55) and test (250). The test set was run once, with nothing changed afterwards.
> - Test results: diagnosis 186/228 (82%, 95% Wilson interval 76% to 86%). The target is met on the point estimate but not with confidence. Top-3 recall was 88%, missing its 100% target, which was set for five seeded incidents.
> - Safety on test: right abstentions 22/22, false abstentions 2%, abstention without logs 250/250, unsafe actions 0%, approval bypasses 0%, plan recall 80%.
> - Dev scored 92%. The drop comes from four families. The rule "a change's effect takes the category of what went wrong" held for 93% of the dev incidents it applied to and 68% of the test ones. Gemma blamed the triggering release 21 times, but still planned the right rollback in 21 of 22 of those cases.
> - The interval treats variants of one family as independent, so it is too narrow: this is closer to 11 scenarios than 228 incidents. Counted by family (added 2026-11-09, from the recorded results), it is 62% to 92%.
>
> **Later fresh sets, same 22 families** (`docs/evaluation.md`): 80% on `data/benchmark-2029` (2026-11-07) and 89% on `data/benchmark-2030` (2026-11-09), both with the rubric. All of these sets are now spent. An analysis on 2026-11-09 found that this benchmark gives some answers away: every incident has an exact precedent in the knowledge base, only incidents with a cause have a change before the failure, and document IDs carry the family's code. The next honest number comes from a new benchmark (section 32).

### Initial MVP targets

| Metric | Target |
|---|---|
| Diagnosis accuracy | ≥ 80% on seeded incidents |
| Top-3 hypothesis recall | 100% |
| Required-evidence recall | ≥ 90% |
| Tool-call success rate | ≥ 95% |
| Unsupported-claim rate | < 5% |
| Unsafe-action rate | 0% |
| Approval-bypass rate | 0% |

Do not put these numbers on the resume until the evaluation has actually been run.

> **2026-11-05:** run. The resume should use the benchmark's test numbers, with their interval and the synthetic, single-author caveat, not the 5/5 from the tuning set.

---

## 23. Testing strategy

### Unit tests

- Pydantic schema validation
- Confidence scoring
- Permission checks
- Argument allowlists
- Secret redaction
- Retrieval filtering
- Graph routing
- Remediation validation

### Integration tests

- FastAPI → LangGraph
- LangGraph → MCP client
- MCP client → synthetic data server
- RAG ingestion → Qdrant → retrieval
- Approval pause and resume
- Audit persistence

### Safety tests

- Prompt injection inside a log message
- Prompt injection inside a runbook
- Arbitrary shell-command request
- Disallowed database mutation
- Secret present in retrieved content
- Infinite tool-loop attempt
- False evidence ID
- Approval bypass attempt
- Stale runbook retrieval
- Unsupported high-confidence diagnosis

### Evaluation tests

Each seeded incident should include:

- Ground-truth category
- Ground-truth root cause
- Required evidence
- Acceptable remediation
- Unsafe actions
- Expected approval requirement

---

## 24. Milestone plan

### Milestone 0 — Repository foundation

- [x] Initialise Python project.
- [x] Add linting, formatting, type checking, and tests.
- [x] Add `.env.example`.
- [x] Add Dockerfile and Compose skeleton.
- [x] Add health endpoint.
- [x] Add CI workflow.

**Exit condition:** API starts locally and tests run.

### Milestone 1 — Synthetic incident environment

- [x] Create five ground-truth incidents.

> **Built 2026-11-04:** all five incidents from section 8 exist: INC-001 (schema mismatch), INC-002 (expired bank credential, 401), INC-003 (backfill burst, 429), INC-004 (payment file uploaded to the wrong SFTP directory), and INC-005 (connection pool shrunk from 50 to 5). Each has logs, deployments including decoys, a dependency map, an API spec, a runbook, a past incident, and ground truth with a `reference_plan`. Alerts and metrics are seeded where an incident needs them. Every raw file is checked against a Pydantic model in `seed_schemas.py` when it's loaded. In a dependency map, an edge from A to B means B depends on A. `test_incidents_solvable.py` proves each incident can be solved by the real graph when the model's answers are perfect.
- [x] Create logs, runbooks, API specs, dependency maps, and deployments.
- [x] Create data schemas.
- [x] Add deterministic data loaders.
- [x] Add seed validation tests.

**Exit condition:** Each incident can be solved manually from the available evidence.

### Milestone 2 — MCP data-access layer

- [x] Implement observability MCP server.
- [x] Implement knowledge MCP server.
- [x] Implement operations MCP server.

> **Built 2026-11-04:** all three servers have the brief's tools, run in-process, and every piece of evidence the graph uses comes through them. Two differences from section 15: the observability server also has `search_alerts`, because the graph finds alerts by time, not by ID; and `get_metrics` takes `metric_names` as optional, so the graph can ask for everything a service records. `search_incidents` filters to past incidents inside the search, before the result limit.
- [x] Add scoped permissions and call limits.
- [x] Add MCP integration tests.

**Exit condition:** Typed MCP calls return evidence with stable IDs.

### Milestone 3 — RAG pipeline

- [x] Ingest runbooks, API specs, and historical incidents.
- [x] Add metadata-aware chunking.
- [x] Store embeddings in Qdrant.
- [x] Implement retrieval and relevance threshold.
- [x] Return source metadata.
- [x] Build retrieval evaluation cases.

**Exit condition:** Required evidence is retrieved reliably for seeded incidents.

### Milestone 4 — LangGraph investigation workflow

- [x] Define typed graph state.
- [x] Implement intake and triage. Triage became a category on each hypothesis; see section 10.
- [x] Implement log analysis.
- [x] Implement dependency tracing.
- [x] Implement runbook retrieval.
- [x] Implement root-cause synthesis.
- [x] Implement graph retries and step limits.

**Exit condition:** The graph diagnoses one incident end to end.

### Milestone 5 — Safety, remediation, and approval

- [x] Implement remediation schema.
- [x] Implement deterministic validation.
- [x] Implement human approval pause.
- [x] Implement approve, reject, and request-more-evidence routes.
- [x] Implement audit persistence.
- [x] Add adversarial safety tests.

**Exit condition:** No disallowed action can bypass validation or approval.

### Milestone 6 — API and Docker demo

- [x] Complete FastAPI endpoints.
- [x] Add structured error handling.
- [x] Add Docker Compose services.
- [x] Add health checks.

> **Built 2026-11-05:** `docker compose up --build` starts the API and a Qdrant server (v1.19.2), with the audit records, paused investigations, and index on named volumes. The API uses the host's Ollama by default; `--profile ollama` adds an Ollama container (0.40.14). The image runs as a non-root user, uses CPU-only PyTorch, and has the embedding model built in, so it starts without the internet. `/health` is liveness; `/health/ready` checks the document index, the model in Ollama, and the audit store, and the container's health check uses it. Verified: INC-001 was diagnosed through the containers in 84 s, the API container was restarted while the investigation waited for approval, and the approval after the restart was recorded.
- [x] Add demo script.
- [x] Add sample API requests.

> **Built 2026-11-05:** every route in section 19 exists except the two incident routes, which `POST /investigations` replaced (see the note under section 19). `GET /investigations/{id}/report` returns a readable Markdown report built from the audit record. Every error is JSON with a `detail`; an unexpected crash answers `{"detail": "internal error", "error_id": ...}`, and the traceback goes to the server's log under that ID. `python -m flowguard.demo` walks an incident through a running API, and `examples/requests.http` holds a sample request for every route. CI (`.github/workflows/ci.yml`) runs ruff, mypy, and the tests on every push and pull request, and builds the Docker image.

**Exit condition:** A new user can run the demo from documented commands.

### Milestone 7 — Evaluation and portfolio evidence

- [x] Run all seeded incidents.
- [x] Calculate core metrics.
- [x] Save machine-readable results.
- [x] Generate a concise evaluation report.
- [ ] Record a demo video.
- [x] Add architecture and threat-model documents.
- [ ] Update resume only with measured claims.

**Exit condition:** Every resume bullet can be supported by code, tests, or evaluation output.

---

## 25. Definition of done for the MVP

The MVP is complete when:

- [x] Five seeded incidents exist with known ground truth.
- [x] Evidence is accessed through MCP tools.
- [x] LangGraph controls a stateful investigation workflow.
- [x] RAG retrieves runbooks, API specifications, and historical incidents.
- [x] Important conclusions cite evidence IDs.
- [x] Unsupported conclusions are rejected or marked uncertain.
- [x] State-changing proposals require explicit approval.
- [x] Every tool call and decision is audited.
- [x] The complete stack runs through Docker Compose.
- [x] Evaluation metrics are generated automatically.
- [x] Unsafe-action and approval-bypass rates are zero.
- [x] The repository includes setup, architecture, threat model, evaluation, and demo documentation.

---

## 26. First implementation tasks

Work in this order:

- [x] Create the repository and Python package.
- [x] Implement domain models for incidents, evidence, hypotheses, and remediation.
- [x] Build INC-001 and all supporting synthetic evidence.
- [x] Write a deterministic Python script that solves INC-001 from the data.
- [x] Expose the synthetic evidence through one MCP server.
- [x] Add RAG over the runbook, API specification, and historical incident.
- [x] Build a minimal LangGraph with intake → triage → retrieve → root_cause → audit. Triage became a category on each hypothesis; see section 10.
- [x] Add FastAPI endpoints to start and inspect an investigation.
- [x] Add validation and approval nodes.
- [x] Expand from one incident to five and build the evaluation runner.

The deterministic solver in step 4 is important. It proves the dataset is coherent before an LLM is introduced.

---

## 27. Engineering rules

- Use typed schemas at every system boundary.
- Prefer small nodes with explicit inputs and outputs.
- Keep prompts versioned in source control.
- Do not hide retrieval sources from the final report.
- Do not mix observed facts with inferred conclusions.
- Keep model-provider logic behind an interface.
- Make all safety policies testable.
- Make every tool call traceable.
- Use structured logging.
- Add timeouts and bounded retries.
- Avoid framework abstractions that make the execution path difficult to explain.
- Never commit credentials.
- Never use confidential company or client data.
- Do not claim production scale unless it is demonstrated.

---

## 28. How this project is built (learning mode)

**This project exists so I learn the material, not so a coding assistant produces a repository.** If I cannot explain a file in an interview, it does not belong here.

Rules for any AI coding assistant working on this repository:

- Treat this file as the project source of truth.
- **Guide; do not implement.** Explain the concept, the trade-off, and the shape of the solution. Let me write the code. Review it afterwards and tell me what is wrong and why.
- Do not hand me a finished file when a worked explanation and a stub would teach more.
- When I am stuck, ask what I have tried and give the next hint, not the answer.
- Implement one milestone at a time. Do not run ahead of where I am.
- Do not change the architecture or add dependencies without explaining the trade-off first.
- Before any code is written, state: files affected, interfaces affected, tests to add, safety implications.
- Prefer complete, runnable vertical slices over empty scaffolding.
- Do not fabricate APIs or package behaviour; verify against official documentation.
- Keep MCP tools read-only during the MVP.
- Do not add autonomous remediation without explicit approval logic.
- Maintain `CHANGELOG.md` and update checked tasks in this document.
- Any metric proposed for the README or resume must be generated by an evaluation script.

Checks I should be able to pass at each milestone:

- I can explain why each node exists and what happens if it is removed.
- I can explain why a control is deterministic rather than delegated to the model.
- I can trace one request from HTTP through the graph, MCP, and the audit record.

---

## 29. Resume-claim evidence checklist

Do not use a claim until the corresponding evidence exists.

| Potential claim | Required proof |
|---|---|
| Built with LangGraph | Working graph and tests |
| Used MCP | Running MCP servers and client integration |
| Used RAG | Ingestion, retrieval, citations, and retrieval evaluation |
| Evidence-backed diagnosis | Evidence IDs linked to conclusions |
| Human-in-the-loop approval | Pause/resume workflow and API |
| Scoped tool permissions | Permission policy and safety tests |
| Complete audit logging | Persisted investigation trace |
| Diagnosis accuracy | Reproducible evaluation report |
| Unsafe-action rate | Adversarial test results |
| Dockerised | Reproducible Compose setup |
| Production-ready | Do not claim this for the MVP |

---

## 30. Future resume bullets

Use only after implementation and measurement. Replace placeholders with real results.

> Built an agentic incident-response copilot using LangGraph and MCP to retrieve operational runbooks, analyse integration logs, trace API and pipeline dependencies, and generate evidence-linked root-cause and remediation recommendations.

> Designed a stateful investigation workflow with deterministic confidence scoring, scoped read-only tools, human approval gates, bounded retries, and end-to-end audit logging.

> Exposed the system through FastAPI and Docker Compose and evaluated it across [N] seeded enterprise incidents, achieving [X]% diagnosis accuracy, [Y]% required-evidence recall, and 0% unsafe-action and approval-bypass rates.

Do not use placeholder numbers on a public CV or portfolio.

---

## 31. Open decisions

Resolve these only when they become necessary:

- [x] Which LLM provider should be used for the public demo? **Decided 2026-11-03:** a local `gemma4:12b` model through Ollama, with thinking off, behind the provider-neutral adapter. On INC-001, it gave valid JSON, cited only real evidence, and found the root cause in 3 of 3 runs, at about 50 seconds per call on an 8 GB laptop GPU. `gemma4:e4b` was rejected: it copied HIST-INC-044's root cause instead of diagnosing INC-001. Thinking was rejected for being six times slower and less reliable. Three runs on one incident are enough to choose a model, not to claim accuracy.
- [ ] Should Qdrant remain the long-term vector store?
- [ ] Should audit storage move from SQLite to PostgreSQL?
- [ ] Should the UI be Streamlit, React, or omitted?
- [ ] Should live CloudWatch access be added after the synthetic demo? **Update 2026-11-05:** real-system access is left to contributors. [`docs/connectors.md`](docs/connectors.md) defines the contract a connector must meet; the first contribution wanted is a setting that points FlowGuard at an external MCP server.
- [x] Under what licence, and how can others extend it? **Decided 2026-11-05:** Apache-2.0, for its explicit patent grant, which makes companies comfortable contributing. [`CONTRIBUTING.md`](CONTRIBUTING.md) sets the ground rules: read-only tools, code decides, a failing test for every rule, no secrets or real data, and no tuning on held-out or test sets.
- [ ] Should remediation execution remain simulated?
- [ ] Should authentication be added before public deployment?

---

## 32. Current next action

**Updated 2026-11-11.** FlowGuard has a new honest number. On the 300 test incidents of `data/benchmark-2031`, run once from a frozen commit, the explain path diagnosed 206 of the 240 with a cause (86%; 70% to 94% counting families) and abstained on 59 of the 60 without one, against the rubric's 139 and 60 (section 14). Since 2026-11-11 it's FlowGuard's default, and the rubric stays available to compare against. On the same incidents and code, Claude Sonnet 5.5 diagnosed 217 with 1 wrong answer against Gemma's 30, for $6.27 (section 14); Gemma stays the model. Every existing test set is now spent. Next, as proposed on 2026-11-11:

```
work on the explain path's diagnosis with new development families:
failures whose surface symptom points to the wrong category
(plans stay secondary: the project's question is what caused it)
        ↓
fix the next test run's terms here, with a fresh test set
        ↓
run it once and report the result as it is
```

**Added 2026-11-12.** A check on real logs comes first: RCAEval RE3, whose logs FlowGuard's author didn't write (section 14). On its development system, Sock Shop, both models did worse than guessing, so code now works out what changed in the logs and each setup states what it records. Next: one development run of each model on Sock Shop with that code, then the 60 test cases of Online Boutique and Train Ticket, converted and run once each.

Nothing is tuned on the spent sets (the held-out incidents, the test split, `data/benchmark-2029`, `data/benchmark-2030`, the test folder of `data/benchmark-2031`, and the RE3 cases of Online Boutique and Train Ticket), and nothing runs on a test family before its final run.

**Added 2026-11-12, after the RE3 test.** The test failed: both models named the faulty service in 33 of the 60 test cases, against 22 and 21 of 30 on Sock Shop (section 14). The user then restated the project's one objective, a tool that finds what caused a real incident, and chose to start again from the ground up against OpenRCA 2.0. Section 33 holds that plan and replaces the next action above. The work described in sections 1 to 32 stays in the repository as it is; what is kept from it is decided in phase 4 of the new plan.


---

## 33. New direction, 2026-11-12: find the root cause on OpenRCA 2.0

**The objective, as the user restated it on 2026-11-12:** a tool that finds what caused a real incident. The comparison of a local model with a hosted one was never the question, and results on incidents written for this project don't show the tool works. The RE3 test (section 14) was the only check on data this project didn't write, and it failed.

**The decision.** Start again from the ground up as an agentic system: a main agent that plans an investigation and sends questions to subagents, with code that scans the telemetry and checks what the agents claim. The target is OpenRCA 2.0. No design is chosen before the data and the task have been studied (phase 4 below).

**What changes in the rules.** "Code decides; the model's output is only an input" becomes "the model investigates; code checks". Tools stay read-only. The discipline on test data stays, and is stricter (below). Any open-source model may be used; which one is decided by measurement in phase 3. The laptop has 8 GB of GPU memory and 16 GB of RAM, so a model too large for it would have to run on a hosted provider, at a cost approved before the run.

### What is known about the benchmark

- OpenRCA 2.0 (arXiv 2606.27154) is a set of recorded fault injections on three microservice systems. An agent sees only the telemetry and must name the root-cause services with the kind of fault, and the path the fault travelled.
- The set on the official leaderboard is `anon-ops/ops-lite` on Hugging Face: 455 cases, 176 of them with more than one fault. TrainTicket has 275 cases, Hotel Reservation 148 and OTel Demo 32. It is 2.87 GB, under Apache-2.0. The commit used here is `581eba39d0bfd2d397eded6cd7cbe3303255521a`.
- Each case holds ten telemetry tables as parquet files (traces, three kinds of metrics, and logs, each for a normal period and the abnormal period) and four answer files: `env.json`, `injection.json`, `label.json` and `causal_graph.json`. The answers ship with the download, and there is one split.
- The leaderboard's rows are one agent, DeepResearch, with different models. That agent is a single model in a loop with four tools: list the tables, read a table's layout, run an SQL query, and a note-to-self tool. About 50 tool calls a case are recommended and 100 is the cap. It has no subagents and is given no dependency map. On 2026-11-12 the best row was Claude Opus 5 at 46.40% accuracy and 61.37% F1; Claude Sonnet 5 had 27.20% and 43.20%.
- The paper names four ways that agent fails: it stops at the first plausible cause and misses faults that occur together; it reads silence from a killed service as normal; it fixates on the loudest signal, which is often a downstream effect; and it names the right service without a verified path to the symptom (76.0% against 61.5%).
- No published system that beats the standard agent on 2.0 was found on 2026-11-12. On OpenRCA 1.0, a structured multi-agent pipeline (arXiv 2607.13548) raised the baseline agent's score most where it was given hand-written domain knowledge (Telecom 29.4% to 56.9%; 35.3% without it), and that knowledge was written against labelled cases. Two other multi-agent systems scored under 3%. So a multi-agent design alone promises nothing.
- Settled in phase 1 (below, and `docs/openrca2-task.md`): the scoring code is public, the leaderboard's columns are matched to it, and a co-author's version of the agent is public. Phase 1 also found that the leaderboard's rows were measured on an older, 500-case version of the dataset, so the second bullet above is wrong on that point.

### The phases

Each phase ends with something to read before the next begins.

| Phase | Question it answers | What comes out | Model cost |
|---|---|---|---|
| 0. Set the rules | What may be looked at? | Data downloaded and checksummed; the held-out split made before any look | None |
| 1. Read the task | What exactly is asked, and how is it scored? | A one-page task sheet | None |
| 2. Study the data | What does each fault look like, and is the answer visible? | Fault kind against signal; the reachable ceiling | None |
| 3. Measure the baseline | What does the standard agent cost, and where does it fail? | Cost per case; a classified list of failures | Small, approved first |
| 4. Decide the design | What should code do, and what should agents do? | The design, its trade-offs and the bars, written here | None |
| 5. Build | Does each part earn its place? | Each part measured on the development cases | Approved per run |
| 6. Test once | Did it beat the baseline? | One held-out run, reported as it comes out | Approved first |

- **Phase 0.** About 100 cases are kept for development, drawn at random within each system, and the rest are held out. The split is made by code that prints counts only. The held-out cases' answer files are moved out of the case folders before anything is read.
- **Phase 1.** If the official scorer is not public, scoring follows the paper's definitions, and no official number is claimed before a submission.
- **Phase 2.** The step that was skipped on RE3. For each simple signal, how often does it put the faulty service first or in the top three, and is the second fault of a multi-fault case visible at all? Development cases only.
- **Phase 3.** About ten development cases with the standard agent on one affordable model, and once on a local model, to learn the cost and whether a local model has a role.
- **Phase 5.** The main agent alone is compared with the main agent and its subagents, so what the subagents buy is known.

### Rules throughout

- Agents and their tools can open only the ten telemetry tables of a case, and this is enforced in code. Case folder names are not shown to an agent if they reveal the fault.
- The held-out cases are not read, summarised or run before the one test run. Nothing is tuned on them afterwards.
- A heuristic is a hint to the agents, never a limit on their answer.
- Nothing is fixed on the evidence of one system.
- Every paid run has its cost approved first.

### Known limits of this target

- The faults are injected on demonstration systems. They are infrastructure and code faults, not the integration failures of sections 1 to 8 (an expired credential, a schema mismatch, a partner's change), and the benchmark has no runbooks, specifications or change records. Beating it would show the investigation works on telemetry this project didn't write; it would not show the integration-specific parts.
- The remediation plan and the approval gate are not scored there.
- TrainTicket is also the application behind the spent RE3 Train Ticket cases. The testbed, the faults and the telemetry differ, and no RE3 finding is carried into this work as a rule.

### Phase 0, done 2026-11-12: what may be looked at

Everything below was fixed before any case's telemetry or answers were read. The code is in `src/flowguard/openrca2`, and it prints counts only.

**The download.** `anon-ops/ops-lite` at commit `581eba39d0bfd2d397eded6cd7cbe3303255521a` was compared with the file list Hugging Face gives for that commit (`python -m flowguard.openrca2.download`). The repo holds 6,374 files and 2,872,924,770 bytes: 455 case folders of 14 files each, and four files beside them. Every local file matched in size and in hash: SHA-256 for the files stored in LFS, git's SHA-1 for the rest. Nothing was missing, nothing was extra, and the downloader's cache held no unfinished part. The SHA-256 of every file is saved in `answers/all-cases/download.sha256`; the SHA-256 of that list is `00b002b79d93564879971d671e70735d25a6cd8559fc47d2c6659292ffe5c2e1`.

**The folders.** All under `data/external/openrca2`, which git ignores.

```
raw/                         what is left of the download: its README, croissant.json, the downloader's cache
telemetry/dev/<id>/          the ten telemetry parquet files of a development case
telemetry/held-out/<id>/     the same for a held-out case; not opened before the one test
answers/dev/<id>/            env.json, injection.json, label.json, causal_graph.json
answers/held-out/<id>/       the same; never read before the test
answers/all-cases/           manifest.jsonl, case-ids.json, download.sha256
split.json                   each ID with its system and its split, nothing else
```

`manifest.jsonl` came with the download and names every case's root services and fault kinds, held-out ones included, so it is kept with the answers and is not read. Tool code is given a folder under `telemetry/` and nothing above it. Development work that needs answers is given `answers/dev` only.

**The IDs.** The original folder names are `batch-` followed by a ULID, which begins with a timestamp, so a name shows when a case was recorded and which cases were recorded together. Each case was renamed `case-001` to `case-455`, in an order shuffled with the seed, so an ID says nothing about the system or the date. The map from the original names is `answers/all-cases/case-ids.json` (SHA-256 `b371d6e9b8afd577681310e05a55102cbbb68fc2bb2fffdec0feb69712fa6c06`). To undo the move, that map and `split.json` say where each file came from.

**The split.** Made by `python -m flowguard.openrca2.prepare` with seed `20261112`. From the manifest it read each record's folder name and system, and no other field. Development is 100 of the 455 cases, shared among the systems in proportion and drawn at random within each.

| System | Development | Held out | All |
|---|---|---|---|
| TrainTicket (`ts`) | 60 | 215 | 275 |
| Hotel Reservation (`hs`) | 33 | 115 | 148 |
| OTel Demo (`otel-demo`) | 7 | 25 | 32 |
| Total | 100 | 355 | 455 |

The SHA-256 of `split.json` is `74c8e2871481ce963f2e8f1bb8fa5cd98846cc3c62e9ec8c5c104c3c518530ae`. The program refuses to run again once that file exists, and a test fails if the file changes. After the move, every one of the 6,370 case files was hashed again in its new place against the saved list (`--verify`), with none missing or changed.

One case was not left to chance. The dataset's README prints one case's `label.json` as its example, so that Hotel Reservation case's answer was seen while reading the layout. It was put in development before the draw, and the other 32 Hotel Reservation places were drawn from the remaining 147. This rule was set before the draw and used nothing but the README.

**The guard.** `CaseTelemetry` (`openrca2/access.py`) is the one way tool code gets a path. It gives the ten telemetry file names of one case and refuses anything else: an answer file's name even if the file is in the folder, any other name, a path that climbs out of the folder, an absolute path, a link, and a case ID that is not `case-` and digits. It refuses the held-out folder unless told the run is the final test. `tests/unit/test_openrca2.py` checks each refusal on stand-in files, and, where the data is present, checks that the telemetry folders hold 4,550 parquet files and nothing else, and that no answer file is left in `raw`.

**What this does not cover.**

- The guard covers paths that Python code opens. A query engine that reads a file named inside a query would go round it, so any such engine must have file access turned off where it is set up, with its own test. That is decided with the tools, not now.
- Whether the telemetry itself gives the answer away (a column, a file's metadata, a leftover log line from the injection tooling) is not known. The README says the tooling's log lines were removed. Phase 2 checks this on development cases.
- Seven OTel Demo development cases is few for a system with seven fault kinds. It is what a proportional share of 100 gives.
- `raw/croissant.json` was not opened. The downloader's cache in `raw/.cache` still holds the original folder names, with no answers. Both are outside what tools are given.

**What was seen while doing this.** Nothing inside a case. Two things outside one: the README's example label, dealt with above, and 15 original folder names, printed when the downloader's cache was listed to check for unfinished parts. Those names are opaque IDs and were not matched to anything.

### Phase 1, done 2026-11-12: the task and its scoring

The task sheet is `docs/openrca2-task.md`. It was written from the paper, the dataset's README, the leaderboard site and the official scoring code; no case was opened. What it settles, and what it changes in this plan:

- **The task.** An agent gets the ten tables and a fixed text saying a user reports slow or failing requests. It returns root causes, each a service with one of 25 kinds of fault, and the edges along which the fault spread, each with a SQL query as evidence.
- **The scoring code is public**: `rcabench_platform/v3/sdk/evaluation` in `github.com/OperationsPAI/aegis`, commit `979ae70` of 2026-08-11. A claim is a hit when the service and the kind are both right. For a network fault either end of the link counts; for any other kind only the service the fault was injected on. Two pairs of kinds count as the same answer.
- **The leaderboard's columns**, matched to that code by name: f1 is the mean F1 over (service, kind) pairs; acc is exact match, where one extra claim or one wrong kind scores 0; all-hit is every true fault's service named with the kind ignored; type-acc is the share of right services that also have the right kind; path-acc is a hit root cause joined to an alarmed service through the answer's own edges. The site defines none of them, and any-hit and path-acc are not confirmed.
- **The published rows are not on our cases.** The site was last updated on 2026-07-25, and its percentages are whole counts out of 500. The dataset was replaced on 2026-09-26 by version 2.1.0, with 455 cases and corrected labels, which is the commit downloaded here. So Claude Opus 5's 46.40% and 61.37% are on 500 cases with the old labels, and a score on our 355 held-out cases cannot be set directly against them.
- **No public scorer knows the new labels.** The public code counts every injected fault as a true one. Version 2.1.0 gives each fault a role in `label.json`: required, optional (naming it is neither required nor penalised) or not effective (naming it is a wrong root cause). The scorer here will be the public code's matching with those roles, and its numbers are not official.
- **The standard agent.** A co-author's adaptation is public (`github.com/QishengLu/rca_study_thinkdepthai`, commit `26b5166`), and the paper prints the prompts. The harness that drives it is not public.

Decisions this leaves, none taken yet:

1. Whether the bar is the published rows, as a rough guide, or the standard agent run on our held-out cases with our scorer. Only the second is like for like, and it costs model calls on 355 cases. Decided in phase 4, once phase 3 has measured the cost per case.
2. The scorer's open points are written down before any development case is scored: how a claim naming an optional fault enters precision and exact match, and how the true graph's services are read.
3. The scoring code's design note gives rules for telling kinds of fault apart, some with thresholds its authors measured on labelled cases of the whole set, which includes our held-out cases. It was read in this phase. Proposed: the scoring rules are part of the task and are used; the thresholds are not used unless the final report says so.

The split of phase 0 stands: nothing was changed after it, and from here on it is not redrawn.

### Phase 2 plan, written 2026-11-12 before any signal was measured against an answer

Development cases only (100). The question is what each fault looks like in the telemetry, and how much of the answer is visible at all. Nothing here becomes a rule; the numbers are for phase 4.

**Signals.** Each is computed per service, comparing the abnormal window with the normal one, with counts turned into rates per minute because the windows differ in length. Each ranks the services of a case, highest first.

| | Signal | Score for a service |
|---|---|---|
| T1 | Error share | Share of its spans with an error status, abnormal minus normal |
| T2 | Latency | p95 span duration, abnormal over normal |
| T3 | Own time | p95 of span duration minus its direct children's durations, abnormal over normal |
| T4 | Trace silence | 1 minus its span rate abnormal over normal; 1 if it has no spans in the abnormal window |
| L1 | Error logs | (ERROR and WARN lines per minute + 1), abnormal over normal |
| L2 | Log silence | As T4, for log lines |
| M1 | Loudest metric | Largest absolute shift of any of its metrics' means, in normal standard deviations |
| B0 | Commonest root | The root service seen most often in the other development cases of the same system (no telemetry) |

**Measures**, per system and together:

- Top 1 and top 3: a required fault's service is first, or within the first three. A service counts as a fault's service under the scoring rules (the label's service, `also_accept`, and either end of a network fault's link).
- For cases with more than one required fault: the rank of each, and whether all are within the first k, where k is the number of required faults.
- By kind of fault: top 3 for each signal, to see which signal shows which kind.
- Visibility: a required fault's service is called visible on a signal when T1 ≥ 0.05, T2 ≥ 1.5, T3 ≥ 1.5, T4 ≥ 0.5, L1 ≥ 2, L2 ≥ 0.5 or M1 ≥ 3. These cut-offs are set now and not changed after seeing results; they say what is seen, not what is decided. The reachable ceiling is the share of required faults visible on at least one signal, and the share of cases with every required fault visible. Faults whose service never appears in any table are counted apart.
- The same visibility for optional and not-effective faults, since naming those costs or gains nothing or costs precision.

**Leak check.** Every text column is searched for words from fault injection tooling (chaos, inject, fault, stress, mutator and the like), namespaces and pod names are listed, and the parquet files' own metadata is read. Anything that names an injected service other than through the system's own behaviour is a leak, reported and then hidden from agents.

**Not measured in this phase:** when each service's anomaly began, and any combination of signals. Both are candidates for phase 4.

### Phase 2, done 2026-11-12: what the development cases show

The full account is `docs/openrca2-data.md`; the tables come from `python -m flowguard.openrca2.study` (`reports/openrca2-phase2`). Development cases only. Three measures were added after the first run, and are marked as such: the same measures for services with no fault, how high optional and not-effective faults rank, and where each signal's first service sits.

- **No leak was found.** No text column holds a word from the injection tooling, and the files carry no other metadata. Namespaces are weakly linked to campaigns and should be hidden from agents.
- **The service is nearly always findable, by some signal.** Some signal puts a required fault's service in its first three in 99 of 100 cases, and first in 86 (17% for a service with no fault). No single signal does better than 60% in the first three. Which signal shows a fault follows its kind: latency and own time for network faults, error share and error logs for HTTP and exception faults, silence and metrics for pod faults.
- **Systems differ.** Silence is the best signal in Hotel Reservation and points somewhere unrelated in TrainTicket; error share is the reverse. OTel Demo's 7 cases settle nothing.
- **Optional and not-effective faults look as faulty as required ones**: some signal ranks every optional fault first, and 79% of the not-effective ones. Whether to name a fault turns on whether its effect spread beyond its service, which is the label's own definition. This is where exact match is decided.
- **Wrong first picks are often downstream**: TrainTicket's entry service under latency, Hotel Reservation's frontend under error share and error logs.
- **The visibility cut-offs set in the plan don't separate**: they pass 84% of services with no fault. They are kept as written and reported as too loose.
- **Only 4 development cases have two required faults**, and in each both services are in some signal's first two.
- **A dataset prior exists**: `search` is the root in 17 of 33 Hotel Reservation cases. It is a baseline, not a rule.

The scorer drafted in this phase (`openrca2/score.py`) makes the README's roles concrete: a left-over claim naming an optional fault is set aside, counting neither for nor against; a claim naming a not-effective fault is a wrong claim; the other end of a network link is read from `injection.json`, as the official code does, since the label lists containers and Hotel Reservation's container names differ from its service names. It waits for the user's review before any agent's answer is scored with it.

Not measured, and candidates for phase 4: when each anomaly began, how often similar kinds of fault can be told apart, and any combination of signals.

### Phase 3, in progress 2026-11-12: the standard agent, rebuilt

`python -m flowguard.openrca2.baseline` rebuilds the leaderboard's agent from the paper's prompts (appendix F.4), the official answer contract and the co-author's tools, on the locked connection. Its known differences and checks are in `docs/openrca2-baseline.md`. The ten development cases are drawn with seed `20261112`: six TrainTicket, three Hotel Reservation and one OTel Demo.

Two local runs on one case with `gpt-oss:20b` checked the whole path. Capped at 6 calls, the model asked for a tool at the answer turn and gave no answer, which scores 0, as the paper's harness would. Capped at 20 calls, it named the right service with the wrong kind of fault. The history grows by about 700 tokens a call. Measured afterwards, the laptop loads this model with a 128K context, which holds a whole case; an earlier claim that 32K was the limit was wrong.

Cost estimate for ten cases: Claude Haiku 5.5 $0.40 to $1.20, Sonnet 5.5 $6 to $18, Sonnet 5 $7 to $23 (the only one with a leaderboard row, on the old data), Opus 5.5 $12 to $35. No paid run has been made; the model and its limit wait for the user's approval.

Update, same day. The user's first paid run (Sonnet 5.5, $5 limit) failed every case on the history check for thinking blocks, before any case was scored. The client was fixed (`docs/openrca2-baseline.md`), and a one-case probe at $0.115 passed the check. On that case Sonnet named the right service and edge with the wrong kind of fault (`network_delay` for `http_response_body_corrupted`), as the local model had (`application_exception`). The probe raised the Sonnet 5.5 estimate to $12 to $30 for ten cases.

### Phase 3, done 2026-11-12: the standard agent measured

The standard agent on Claude Haiku 5.5, on the ten sampled development cases, made 7 exact matches. Any-hit was 0.90, edge-F1 0.81 and path-acc 0.67. It cost about $0.026 and 70 seconds a case (`docs/openrca2-baseline.md`, `reports/openrca2-baseline-haiku`).

- **The interval for 7 of 10** runs from 40% to 89%. Under the public scorer's rule, every injected fault required, it is 60%. None of this compares with the published rows, which are on the older data.
- **Misses.** One wrong service (OTel Demo), and twice the same wrong kind: a network partition to the database read as failing database calls.
- **The local model.** `gpt-oss:20b` was ten times slower and weaker on the cases it finished, so a local model has no role in the baseline. The user chose Haiku for paid runs at this price.

What phase 4 starts from:

1. The standard agent is already strong on these cases, so the bar is high. A design has to beat it on the same cases, with the same scorer and the same model.
2. Where points were lost: telling similar kinds of fault apart, one system with few cases (OTel Demo), and, from phase 2, not naming faults whose effect didn't spread.
3. Haiku runs cost cents, so the development set can be run whole, and runs repeated to measure their spread.

### Phase 4, proposed 2026-11-12, waiting for the user's review

The proposal is in `docs/openrca2-design.md`. Its parts:

- **A code survey of each case:** the call graph, the entry services, the phase 2 signals for every service, and when each service's deviation began. It is a hint, never a limit on the answer.
- **A lead agent** that plans and writes the answer under structured output.
- **Subagents with fresh contexts**, each answering one kind of question: did this service's own work go wrong; which kind of fault is it; and does its effect spread, and by what path.
- **A code checker** that reports claims that don't hold (queries, services, edges, a path to an entry service) back to the lead once, without deciding for it.

All model parts use Claude Haiku 5.5, as the baseline did. Phase 5 adds the parts one at a time, each kept only if it beats the baseline's run-to-run spread on the 100 development cases.

The proposed bar: one held-out run each of the design and the standard agent, both on Haiku. The design passes if its exact match is higher and an exact paired test gives p < 0.05. The published rows are a reference only. Before the design is fixed, the standard agent runs on all 100 development cases twice (about $5) to rank the failure classes and measure the spread.

Update 2026-11-13: the standard agent ran on all 100 development cases twice, on Haiku ($2.97 and $3.23).

- **Exact match** was 56 of 100 both times (38 and 35 under the public scorer's rule). The runs agreed on 88 cases and flipped 6 each way.
- **By system:** Hotel Reservation 31 and 32 of 33, OTel Demo 5 and 7 of 7, TrainTicket 20 and 17 of 60.
- **Misses**, 44 a run: the right service with the wrong kind in 31 to 32, most of them a network fault on the link to MySQL called a database fault. The wrong service in 9 to 10, mostly an HTTP fault blamed on the called service, where the scoring code counts the caller.

The design note now targets these, adds per-connection network metrics and restart signs to the survey, and fixes the rule for keeping a part in phase 5: at least 8 more exact matches than each baseline run, and no system losing more than 2. The comparison is reproduced by `python -m flowguard.openrca2.failures`.

### Phase 4, agreed 2026-11-13

The user agreed the design (`docs/openrca2-design.md`), the bar and the rule for keeping a part in phase 5. The scorer's rule for optional faults is now fixed: a left-over claim naming one counts neither for nor against. The agents may be told how the scoring code places a fault (an HTTP fault at the caller, a network fault at either end), and every comparison with the standard agent says so. Phase 5 begins.

### Phase 5, step 1, built 2026-11-13: the lead agent and the survey

The design's first two parts are built and checked offline: `--agent lead` and `--agent lead+survey` (`docs/openrca2-design.md`, "Phase 5, step 1"). Before any part was measured, the rule for keeping a part was made precise. The lead's result against both baseline runs is recorded, and it stays as the base either way; each later part is judged against the configuration it was added to. Each configuration runs on one case first, then on all 100 development cases, at about $3 to $4 each.

### Phase 5, step 1, measured 2026-11-13

Measured on the 100 development cases on Haiku (`docs/openrca2-design.md`, "Results on the 100 development cases"):

- **Lead:** 50 exact against the baseline's 56 and 56. The placement rule fixed 8 HTTP faults, but turned network delays at the caller into `http_slow`, mainly in Hotel Reservation (22 of 33, against 31 and 32). Five answers came back empty. As agreed, the lead stays as the base.
- **Lead and survey:** 62 exact. Against the lead, it gained 17 and lost 5 (p = 0.017), with no system worse off, at 3.5 cents a case. The survey passes the keep rule and stays.

Against the baseline, lead and survey is 6 ahead (p about 0.3). That gain is not yet secure, and Hotel Reservation is still 3 to 4 below. Two points wait on the user: how to stop empty answers (`minItems: 1` recommended), and putting the network-delay against HTTP evidence in the kind subagent rather than the lead prompt.

### Decisions after step 1, 2026-11-13

The user decided three points (`docs/openrca2-design.md`, "Decided by the user, 2026-11-13"):

- The answer schema requires at least one fault, so an answer cannot be empty.
- The evidence that separates a network delay from HTTP slowness goes in the kind subagent's brief; the lead prompt stays as measured.
- A check is added before the held-out test: on the development cases, the final design must be no more than 2 exact matches below both baseline runs on every system. Lead and survey does not yet pass it on Hotel Reservation.

### Phase 5, step 2, built 2026-11-13: the kind check

The first subagent is built and checked offline: `--agent lead+survey+kind`. Code sends each fault of the lead's draft to a subagent in a fresh context. The subagent tries to disprove the claimed kind, using the contract's rules and a section on telling kinds apart by the scope of what is affected. The lead sees the findings and has the last word. Each record keeps the draft and the checks, so the effect is read case by case. It is measured on the 100 development cases against lead and survey, at about $5 to $7 (`docs/openrca2-design.md`, "Phase 5, step 2").
