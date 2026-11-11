# FlowGuard

An incident-response copilot for enterprise integration failures. Given an incident, FlowGuard gathers evidence through MCP tools, retrieves runbooks and past incidents, names a root cause, or abstains, by rules that code applies to the model's answers, and plans a fix that a person must approve before anything changes.

It runs on a local model (`gemma4:12b` through Ollama), and every step it takes is saved in an append-only audit record.

```
Incident  →  logs, deployments, alerts, metrics, dependency map   (MCP tools)
          →  runbooks, API specs, past incidents                  (RAG over Qdrant)
          →  root cause: what failed, which change explains it    (Gemma answers, code decides)
          →  remediation plan, checked against an action catalogue
          →  pause for human approval  →  audit trail
```

## What it does well, and what it doesn't

FlowGuard with `gemma4:12b` on `data/benchmark-2031`: 300 test incidents from 30 scenario families that no model saw during development, run once from a tagged commit, with the terms fixed beforehand. Since 2026-11-11 FlowGuard diagnoses with the explain path; the rubric it replaced ran on the same incidents.

| | Explain path (default) | Rubric (before) |
|---|---|---|
| Diagnosed correctly, of 240 with a cause | **206, 86%** (81% to 90%; 70% to 94% counting each family as one scenario) | 139, 58% |
| … where a change came first (180) | 161 | 139 |
| … where nothing changed (60) | 45 | 0, by construction |
| Wrong diagnoses | 31 (30, and 1 of the 60 without a cause) | 23 |
| Right when it gave an answer | 87% (206 of 237) | 86% (139 of 162) |
| Abstained where there's no cause | 59 of 60 | 60 of 60 |
| Unsafe actions planned, approval bypasses | **0, 0** | 0, 0 |
| Abstained when its logs were withheld | 300 of 300 | 300 of 300 |
| Plan includes the reference fix steps | 67% | 54% |
| Median time per investigation | 48 s | 39 s |

The explain path asks Gemma two questions: what failed, from the symptoms alone, and which change, if any, explains it. Code decides from the answers. It stopped the rubric's main mistake, blaming the release that only triggered a different failure, and it diagnoses causes with nothing changed before them, which the rubric can't. 29 of its 31 wrong answers came from four families, where Gemma named the failure by its surface symptom: a truncated upload as a timeout (10 of 10), a poison message as a schema mismatch (10 of 10), a changed filename pattern as a schema or data problem (6), and a receiver that stopped polling as a queue problem (3). Its plans propose more fixes the reference doesn't have than the rubric's did (39 against 18), all held for approval. One of the five marks fixed before the run, precision, was worded ambiguously: read as the share of answers that were right, the explain path passes (87% against 86%); read literally, counting right abstentions too, it misses by 0.1 points. The switch was decided after seeing that ([brief](brief.md), section 14). The incidents are synthetic, and one person wrote both them and FlowGuard. [`docs/evaluation.md`](docs/evaluation.md#benchmark-2031) has the details.

### The earlier benchmark

Before that, with the rubric deciding, on a generated benchmark: 250 test incidents from 11 scenario families that were never used during development, run once, with nothing changed afterwards.

| | Test set (250) |
|---|---|
| Diagnosed correctly | **186 of 228, 82%** (95% interval 76% to 86%; 62% to 92% counting each family as one scenario) |
| Abstained where the evidence supports no cause | 22 of 22 |
| Abstained wrongly | 2% |
| Required evidence gathered | 100% |
| Unsafe actions planned | **0** |
| Approval bypasses | **0** |
| Abstained when its logs were withheld | 250 of 250 |
| Plan includes the reference fix steps | 80% |
| Confidence separates right answers from wrong | **No**: AUROC 0.34, where 0.5 is chance. A fix chosen afterwards scored 0.50 on fresh incidents |
| Median time per investigation | 46 s |

Seven of the eleven families were diagnosed 99% of the time. The misses came from four. In two, Gemma named the release that triggered the failure, not what broke: a dropped index or a cut replica count. Even then, its plan rolled back the right release in 21 of 22 cases. In encoding_change, Gemma mixed up a file's encoding with its schema. In provider_outage, Gemma sometimes abstained when the evidence did support the cause. On the 55 development incidents it scored 92%, so the test set found a real drop. The confidence score is also misleading: answers at 0.9 or above were right 13 of 27 times, and answers at 0.65 were right 52 of 52 times, because the rubric rewards citing a release. Reporting confidence as the lead over the best rival in another category looked better on a development set, then failed its one check on 110 fresh incidents (AUROC 0.50), so confidence still says nothing about whether an answer is right. The incidents are synthetic, and one person wrote both them and FlowGuard. Variants of one family behave alike, so the honest interval counts families, not incidents. Two later sets of 110 fresh incidents from the same families scored 80% and 89%. A decision rule that scores all the cited evidence together failed its one pre-registered check on the second (Gemma gained only 2 diagnoses, Sonnet made 2 more wrong ones), so the rubric stays. The benchmark also makes some things easy: every incident has an exact precedent in the knowledge base, and only incidents with a cause have a change before the failure, so a new benchmark of 40 families was built for the next number, above. [`docs/evaluation.md`](docs/evaluation.md#benchmark) has the details and the limits.

Before the benchmark, FlowGuard was tuned on five hand-written incidents, and three more were held out and evaluated once:

| | Tuning set (5) | Held out (3) |
|---|---|---|
| Diagnosed correctly | 5 of 5 (3 of 5 before tuning) | **3 of 3** |
| Plan includes the reference fix steps | 80% | **67%**: two plans had no fixing step |
| Required evidence gathered | 100% | 100% |
| Unsafe actions planned | 0 | 0 |
| Approval bypasses | 0 | 0 |
| Abstained when its logs were withheld | 5 of 5 | 3 of 3 |
| Median time per investigation | 46 s | 60 s |

Eight incidents is a small sample, which is why the benchmark was built. Every run is kept in [`reports/`](reports/).

FlowGuard **recommends**: an approved plan is recorded, not run. There is no authentication, so anyone who can reach the API can approve. See [the threat model](docs/threat-model.md) for what that means.

## Quick start

You need [Ollama](https://ollama.com) with the model pulled (8 GB):

```powershell
ollama pull gemma4:12b
```

### With Docker Compose

```powershell
docker compose up --build
```

This starts the API and a Qdrant server, and uses the Ollama already on your computer. `docker compose --profile ollama up --build` runs Ollama in a container instead. Check it's ready:

```powershell
Invoke-RestMethod http://localhost:8000/health/ready
```

### Without Docker

Python 3.11 or later:

```powershell
pip install -e ".[dev]"
uvicorn flowguard.api.app:app
```

The document index stays in memory and is rebuilt at each start. Settings are in [`.env.example`](.env.example); every one has a default.

## Demo

With the API running:

```powershell
python -m flowguard.demo                         # investigate INC-001, stop for approval
python -m flowguard.demo --approve               # ...and approve the plan
python -m flowguard.demo --incident INC-003 --reject "Wait for the carrier"
```

The demo checks readiness, starts an investigation, shows the plan with what needs approval, records the decision, and prints the readable report and the audit trail. [`examples/requests.http`](examples/requests.http) has a request for every route, to send from VS Code's REST Client.

## API

| Route | |
|---|---|
| `GET /health` | The process is running |
| `GET /health/ready` | The index, the model, and the audit store can all serve |
| `POST /investigations` | Investigate an incident. Answers 201 with the record, or 422 for an invalid request, which is still audited |
| `GET /investigations/{id}` | The latest record |
| `GET /investigations/{id}/report` | The latest record as a readable Markdown report |
| `GET /investigations/{id}/events` | Every saved version of the record |
| `POST /investigations/{id}/approve` | Approve a plan that's waiting |
| `POST /investigations/{id}/reject` | Decline it, with a reason |
| `POST /investigations/{id}/request-more-evidence` | Send it back once, with what to look for |

## How it stays safe

- **The model proposes, code decides.** Gemma says what failed and which change explains it, and suggests steps. Code decides by fixed rules whether to accept the diagnosis or abstain, attaches each step's risk, rollback, and approval requirement, and validates the plan.
- **Only catalogued actions.** A step must be one of 11 actions, target a service or deployment in the evidence, cite evidence, and come in a safe order. A replay can't run before a fix.
- **Every state change waits for a person.** The graph pauses, the pause survives restarts, and only an explicit, named decision resumes it. Nothing times out into approval.
- **Read-only, allowlisted tools.** The model never calls tools. Each of the 10 MCP tools has a call limit, and a write tool can't be declared without requiring approval.
- **Untrusted text stays data.** Evidence is fenced off in the prompt, and fence tags inside it are removed. Credentials are redacted wherever text enters.
- **Everything is audited.** Each stage saves a new version of the record. Versions can't be changed or saved twice, and the investigation fails if its record can't be saved.

The full list, with the test for each threat, is in [the threat model](docs/threat-model.md).

## Tests and evaluation

```powershell
ruff check . ; ruff format --check . ; mypy src
pytest                                          # about 550 tests, no model needed
pytest -m llm                                   # 2 tests against the real model
python -m flowguard.evaluation.investigations   # the five tuning incidents with Gemma, about 6 minutes
```

The benchmark's commands, which take hours, are in [`docs/evaluation.md`](docs/evaluation.md#reproducing).

CI runs the checks and builds the Docker image on every push. [`tests/unit/test_safety.py`](tests/unit/test_safety.py) covers each threat in the brief with a model that obeys injected instructions, to show the controls don't depend on the model behaving.

## Documentation

- [Architecture](docs/architecture.md): the components, the investigation graph, and the main design decisions.
- [Threat model](docs/threat-model.md): what could go wrong, what stops it, the test that proves it, and the risks that remain.
- [Evaluation](docs/evaluation.md): the method, the metrics, both sets of results, and their limits.
- [Connectors](docs/connectors.md): the contract a connector to a real system must meet, and the connectors wanted.
- [`brief.md`](brief.md): the original design brief, with dated notes where the build changed course.
- [`CHANGELOG.md`](CHANGELOG.md): what changed, step by step.

## Project layout

```
src/flowguard/
  api/          FastAPI app and routes
  graph/        LangGraph state, nodes, routing, checkpoints
  domain/       Models and rules: incidents, evidence, confidence, remediation, validation, redaction
  mcp/          MCP servers (observability, operations, knowledge), tool guard, client adapter
  rag/          Chunking, embedding, ingestion, retrieval
  llm/          Ollama client
  storage/      Append-only audit store
  evaluation/   Retrieval and investigation evaluations
  benchmark/    The benchmark's scenario families, generator, and checker
data/           Eight seeded incidents: logs, deployments, alerts, metrics, maps, documents, ground truth
data/benchmark/ The generated benchmark: 305 incidents
data/benchmark-2031/  The next benchmark: 50 development and 300 test incidents, no model run yet
reports/        Evaluation results; the benchmark's are in reports/benchmark/
```

## Contributing

FlowGuard reads synthetic incidents today. The most useful next step is connectors to real systems, such as Loki, Prometheus, and GitHub, so it can investigate real incidents. [docs/connectors.md](docs/connectors.md) describes what a connector must do, and [CONTRIBUTING.md](CONTRIBUTING.md) explains how to send one.

## Licence

[Apache License 2.0](LICENSE).
