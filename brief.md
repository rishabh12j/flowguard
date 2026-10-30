# FlowGuard — Agentic Integration Incident Copilot

> **Project status:** Planning / MVP not yet implemented
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

#### 9. `approval_node`

- Pause the graph for human review.
- Record approver, decision, timestamp, and comment.
- Allow approve, reject, or request-more-evidence.
- Never treat silence as approval.

#### 10. `audit_node`

- Persist the full investigation trace.
- Store tool calls, tool results, evidence IDs, model outputs, validation results, and approvals.
- Produce a user-readable incident report.

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
    service: str,
    start_time: datetime,
    end_time: datetime
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

---

## 19. FastAPI contract

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

- [ ] Initialise Python project.
- [ ] Add linting, formatting, type checking, and tests.
- [ ] Add `.env.example`.
- [ ] Add Dockerfile and Compose skeleton.
- [ ] Add health endpoint.
- [ ] Add CI workflow.

**Exit condition:** API starts locally and tests run.

### Milestone 1 — Synthetic incident environment

- [ ] Create five ground-truth incidents.
- [ ] Create logs, runbooks, API specs, dependency maps, and deployments.
- [ ] Create data schemas.
- [ ] Add deterministic data loaders.
- [ ] Add seed validation tests.

**Exit condition:** Each incident can be solved manually from the available evidence.

### Milestone 2 — MCP data-access layer

- [ ] Implement observability MCP server.
- [ ] Implement knowledge MCP server.
- [ ] Implement operations MCP server.
- [ ] Add scoped permissions and call limits.
- [ ] Add MCP integration tests.

**Exit condition:** Typed MCP calls return evidence with stable IDs.

### Milestone 3 — RAG pipeline

- [ ] Ingest runbooks, API specs, and historical incidents.
- [ ] Add metadata-aware chunking.
- [ ] Store embeddings in Qdrant.
- [ ] Implement retrieval and relevance threshold.
- [ ] Return source metadata.
- [ ] Build retrieval evaluation cases.

**Exit condition:** Required evidence is retrieved reliably for seeded incidents.

### Milestone 4 — LangGraph investigation workflow

- [ ] Define typed graph state.
- [ ] Implement intake and triage.
- [ ] Implement log analysis.
- [ ] Implement dependency tracing.
- [ ] Implement runbook retrieval.
- [ ] Implement root-cause synthesis.
- [ ] Implement graph retries and step limits.

**Exit condition:** The graph diagnoses one incident end to end.

### Milestone 5 — Safety, remediation, and approval

- [ ] Implement remediation schema.
- [ ] Implement deterministic validation.
- [ ] Implement human approval pause.
- [ ] Implement approve, reject, and request-more-evidence routes.
- [ ] Implement audit persistence.
- [ ] Add adversarial safety tests.

**Exit condition:** No disallowed action can bypass validation or approval.

### Milestone 6 — API and Docker demo

- [ ] Complete FastAPI endpoints.
- [ ] Add structured error handling.
- [ ] Add Docker Compose services.
- [ ] Add health checks.
- [ ] Add demo script.
- [ ] Add sample API requests.

**Exit condition:** A new user can run the demo from documented commands.

### Milestone 7 — Evaluation and portfolio evidence

- [ ] Run all seeded incidents.
- [ ] Calculate core metrics.
- [ ] Save machine-readable results.
- [ ] Generate a concise evaluation report.
- [ ] Record a demo video.
- [ ] Add architecture and threat-model documents.
- [ ] Update resume only with measured claims.

**Exit condition:** Every resume bullet can be supported by code, tests, or evaluation output.

---

## 25. Definition of done for the MVP

The MVP is complete when:

- [ ] Five seeded incidents exist with known ground truth.
- [ ] Evidence is accessed through MCP tools.
- [ ] LangGraph controls a stateful investigation workflow.
- [ ] RAG retrieves runbooks, API specifications, and historical incidents.
- [ ] Important conclusions cite evidence IDs.
- [ ] Unsupported conclusions are rejected or marked uncertain.
- [ ] State-changing proposals require explicit approval.
- [ ] Every tool call and decision is audited.
- [ ] The complete stack runs through Docker Compose.
- [ ] Evaluation metrics are generated automatically.
- [ ] Unsafe-action and approval-bypass rates are zero.
- [ ] The repository includes setup, architecture, threat model, evaluation, and demo documentation.

---

## 26. First implementation tasks

Work in this order:

- [ ] Create the repository and Python package.
- [ ] Implement domain models for incidents, evidence, hypotheses, and remediation.
- [x] Build INC-001 and all supporting synthetic evidence.
- [x] Write a deterministic Python script that solves INC-001 from the data.
- [ ] Expose the synthetic evidence through one MCP server.
- [ ] Add RAG over the runbook, API specification, and historical incident.
- [ ] Build a minimal LangGraph with intake → triage → retrieve → root_cause → audit.
- [ ] Add FastAPI endpoints to start and inspect an investigation.
- [ ] Add validation and approval nodes.
- [ ] Expand from one incident to five and build the evaluation runner.

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

- [ ] Which LLM provider should be used for the public demo?
- [ ] Should Qdrant remain the long-term vector store?
- [ ] Should audit storage move from SQLite to PostgreSQL?
- [ ] Should the UI be Streamlit, React, or omitted?
- [ ] Should live CloudWatch access be added after the synthetic demo?
- [ ] Should remediation execution remain simulated?
- [ ] Should authentication be added before public deployment?

---

## 32. Current next action

Build one coherent vertical slice for INC-001:

```
synthetic incident
    → MCP evidence access
    → RAG retrieval
    → LangGraph investigation
    → evidence-backed root cause
    → remediation proposal
    → validation
    → human approval
    → audit report
```

Do not start with all five incidents, a frontend, or real cloud integrations. Prove the complete control flow first.

Immediate order of work:

```
M0: repository foundation
        ↓
M1: one coherent INC-001 dataset
        ↓
deterministic Python solver
        ↓
first read-only MCP server
```

Do not introduce the LLM until a normal Python program can solve INC-001 from the supplied evidence. That prevents debugging bad synthetic data, retrieval, MCP, LangGraph, and model behaviour simultaneously.
