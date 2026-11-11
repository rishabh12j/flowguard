# FlowGuard: project report

This report describes what FlowGuard is, how it decides the cause of an incident, how it was tested, what the results show, and how it can be extended.

## 1. Purpose

The project asks one question: can a small language model, deployed locally, find the cause of a production integration failure well enough to help an on-call engineer, and how does it compare with a hosted model? The model is Gemma 4 12B (`gemma4:12b`), run through Ollama on a single machine.

Running locally keeps incident evidence inside the environment. Logs contain stack traces, customer identifiers, partner endpoints and sometimes leaked secrets, and many organisations can't send them to an external API. It also means there is no cost per call. Hosted models are larger and were expected to read the evidence better. The project measured the difference on the same code and incidents.

The focus is diagnosis: naming what caused the failure. FlowGuard also proposes a remediation plan, but plans were treated as secondary and were not tuned.

## 2. How an investigation runs

An investigation is a LangGraph graph behind a FastAPI service:

```
incident report
   │
intake ─── validates the report, redacts credentials
   │
   ├── log analysis ──── searches logs in the incident window, finds the first failure
   └── retrieval ─────── runbooks, past incidents, API specs (vector search)
   │
dependency trace ──── changes in the 24 hours before the first failure,
   │                   at or upstream of the failing service
root cause ────────── the model reads the evidence, code decides (section 3)
   │
remediation ───────── the model proposes steps from a fixed catalogue
   │
validation ────────── code checks every step
   │
approval ──────────── the graph pauses until a person decides
   │
audit ─────────────── an append-only record of the investigation
```

Evidence is read only through three Model Context Protocol (MCP) servers. The observability server searches logs and alerts and reads metrics. The operations server lists deployments and past incidents. The knowledge server returns dependency maps, API specifications and runbooks. Every tool is read-only and has a call limit per investigation. A call that is denied, fails or is cut short is recorded and lowers what FlowGuard can conclude; it doesn't stop the investigation. Credentials found in evidence (private keys, bearer tokens, JSON Web Tokens, cloud access keys, passwords in URLs or `password=` values) are redacted as the evidence arrives, before the model sees it.

Runbooks and past incidents are split by section, embedded with sentence-transformers and stored in Qdrant. Retrieval is filtered to the current documents of the affected system.

The model is called through a one-method interface, `generate(system, prompt, schema)`, with an Ollama implementation and a Claude implementation used for comparison. Every answer must match a JSON schema, and every evidence ID it cites must be one it was shown. An answer that breaks either rule is treated as no answer.

Before any step that changes state, the graph pauses, with its state saved by a LangGraph checkpointer, and waits for a person to approve, reject or ask for more evidence. Every investigation, including rejected and abstained ones, ends with a record in an append-only SQLite store. The record holds the validated incident, every tool call, the evidence, the decision, the plan and the approval.

## 3. Deciding the root cause

A diagnosis names one of ten categories: authentication, authorisation, schema_contract_mismatch, networking, timeout, rate_limiting, data_quality, file_transfer, queue_or_event_processing or deployment_or_configuration. FlowGuard can also abstain, which records the category as `unknown`. Abstaining is the correct outcome when the evidence doesn't support a cause. A wrong diagnosis sends an engineer the wrong way; an abstention hands the incident over with the evidence already gathered.

The design rule throughout is that the model proposes and code decides. Two methods were built.

### 3.1 The confidence rubric

The first method asked the model for two or three hypotheses. Each hypothesis named a category and cited supporting and contradicting evidence. Code scored each hypothesis from the kinds of evidence it cited:

| Signal | Score |
|---|---|
| Direct error evidence (an error log) | +0.30 |
| Timeline: a cited change (deployment, alert, or metric over its threshold) within 24 hours before the first failure | +0.20 |
| Dependency path: that change at or upstream of the failing service | +0.15 |
| API or schema evidence | +0.15 |
| A cited deployment | +0.10 |
| A matching past incident | +0.10 |
| Each piece of contradicting evidence | −0.20 |
| Each evidence source that failed or was cut short | −0.15 |

The score is clamped between 0 and 1. The best hypothesis needs 0.65 or more, otherwise FlowGuard abstains. The advantage is that any score can be recomputed by hand from the citations.

Testing showed three problems with it:

- **It favours blaming the release.** It scores what kinds of evidence a hypothesis cites, not whether they fit the category. A hypothesis that blames the latest release always cites a deployment and a timeline, so it often outscores the real failure that the release only triggered. On the final test set, 19 of its 23 wrong answers were of this kind.
- **It can't diagnose a cause with no change before it.** Without a change to cite, the best possible score is 0.55, under the 0.65 threshold. An expired certificate or clock drift can never be diagnosed.
- **Its score doesn't predict correctness.** On the 250-incident test set, answers scored 0.9 or above were right 13 of 27 times, while answers at 0.65 were right 52 of 52 times.

It also penalised a candid model. Sonnet listed contradicting evidence for 90% of its hypotheses and lost 0.20 for each item, so on one development set Sonnet scored 76 of 100 against Gemma's 86. It had proposed the right category in all 24 of the incidents it missed.

### 3.2 Attempts to fix the rubric

Each fix was chosen on a development set, with pass marks written down before a single check on fresh incidents. None passed:

| Attempt | Check | Result |
|---|---|---|
| Report confidence as the lead over the best rival category | AUROC on 110 fresh incidents | Failed: 0.50, no better than chance |
| Four new decision rules; the best scored all the cited evidence together | At least 5 more right and at most 1 more wrong than the rubric, for both models, on 110 fresh incidents | Failed: Gemma gained 2; Sonnet gained 19 but made 2 more wrong |
| Ask for three hypotheses in three different categories | Marks on the development set | Failed: right fell from 85 to 77, because Gemma offered the release as an alternative more often |
| Ask only "what failed", showing the symptoms alone | 90 of 100 right and at least 9 of 10 no-cause incidents declined | Half passed: 90 right, but it declined none of the 10 |

The last attempt showed that symptoms alone can name what failed, but can't tell whether there is a cause to name. That led to the second method.

### 3.3 The explain path (current default)

The explain path asks two questions, in the order an engineer would reason:

1. **What failed?** The model sees only the symptoms: the incident report, logs, API specifications and dependency map, each under a neutral ID. Releases, alerts, metrics, runbooks and past incidents are withheld. It answers what failed, which evidence shows it, whether the failure is sustained or isolated, and its category.
2. **What explains it?** The model sees all the evidence. It answers with the change that explains the failure, or that no change was needed (for example, a certificate that expired on its own), or that nothing in the evidence explains it.

Code then applies these rules:

- The answer must cite an error log. With no logs at all, FlowGuard abstains without calling the model.
- An isolated failure, an unknown category or "nothing explains it" means abstaining.
- The second answer can change the category only by naming a change that explains the failure, and never to deployment_or_configuration. A broken release has to show in the symptoms, such as a service that won't start.

Withholding the changes in the first question stops the model being drawn to a release it hasn't seen. Allowing "no change was needed" makes change-free causes diagnosable. What it gives up is the rubric's arithmetic: the decision rests on the model's reading, which is recorded but can't be recomputed by hand. The explain path was developed on 10 scenario families. It became the default after the final test run (section 6).

## 4. Remediation

After a diagnosis, the model may propose up to five steps from a catalogue of eleven actions: `rollback_deployment`, `update_field_mapping`, `replay_failed_messages`, `redeliver_file`, `rerun_job`, `pause_job`, `enable_rate_limiting`, `rotate_credential`, `add_contract_test`, `add_monitoring` and `notify_service_owner`. Each step names a target and cites evidence.

Validation is deterministic. A step is rejected, with its reason recorded, if:

- it isn't in the catalogue;
- it cites evidence that doesn't exist or doesn't relate to it;
- it targets something that isn't in the evidence;
- it replays messages before a fix has been accepted.

Risk, rollback and verification come from the catalogue, not the model. Every step that changes state needs approval.

## 5. Test data

Each test incident reproduces the evidence an engineer would pull from production systems. FlowGuard reads it through the same read-only tools it would use against real platforms.

An incident consists of:

- an incident report: the service, the reported symptom and the time window, as a monitoring alert or ticket would raise it;
- timestamped application logs at mixed levels from the failing service and its neighbours, with unrelated warnings and background noise;
- alert records and metric series with thresholds, such as error rate, latency, queue depth and connection-pool use;
- deployment and configuration-change records for the service and its neighbours;
- a dependency map, versioned API specifications, runbooks and past incident write-ups.

Each incident is sized to fit the model's 8,192-token context. Evidence fetched from production would need the same filtering to the incident window.

The data is structured so that surface patterns don't give the answer away:

- Documents carry numbered IDs, so no name reveals the failure type.
- Only half the scenario families have a matching runbook and past incident, so retrieval alone can't answer the rest.
- Many incidents follow a release that only triggered a different failure, such as a new consumer sharing an API key and surfacing as rate limiting.
- Some causes have no change before them: an expired certificate, clock drift, a lapsed subscription, a partner that started requiring a new field.
- Half the incidents with no diagnosable cause include an unrelated upstream change, so a change alone is never enough.
- Each family has several variants with different services, timings and noise.

The final benchmark has 40 scenario families. Development and test families are different failures, not variants of the same ones.

| Split | Families | Incidents | Correct outcome |
|---|---|---|---|
| Development | 10 | 50 | Used to build the explain path; never scored |
| Test: a change came before the cause | 18 | 180 | The category of the real failure, not the release |
| Test: a cause with nothing changed | 6 | 60 | The category, with no change needed |
| Test: no diagnosable cause | 6 | 60 | Abstain |

## 6. Testing

### 6.1 Procedure

1. The test run comes from a tagged commit. The evaluation runner refuses to run a test split with uncommitted code or data, and each report records its commit.
2. The pass marks, and how they would be computed, were committed to the project brief before the run.
3. Each incident runs twice: once with all evidence, and once with log searches denied, where the only correct outcome is to abstain.
4. A test set runs once and is then retired, never used for tuning. Five test sets were retired this way over the project.

### 6.2 Metrics

- **Diagnosis accuracy:** right answers out of incidents with a cause. It is reported with a 95% Wilson interval, and with a stricter interval that counts each family as one sample, because variants of a family behave alike.
- **Precision of answers given:** right ÷ (right + wrong), the share of diagnoses that can be acted on.
- **Abstentions:** on incidents with no cause, and on every incident when logs are withheld.
- **Evidence precision and recall:** whether the cited evidence is relevant, and whether the evidence that proves the cause was cited.
- **Safety:** unsafe actions in a plan and approval bypasses; both must be zero.
- **Plans** (secondary): whether a plan contains the reference fix steps.
- **Latency:** median and 95th percentile.

### 6.3 Results over the project

| Test set | Method | Accuracy |
|---|---|---|
| 3 held-out incidents | Rubric | 3 of 3 |
| 250 incidents, 11 families | Rubric | 82% (76% to 86%) |
| Two later sets of 110 incidents from the same families | Rubric | 80% and 89% |
| 300 incidents, 30 new families (final) | Rubric | 58% |
| The same 300 | Explain path | 86% |

The earlier benchmark was easier than its numbers suggested. Every incident had an exact precedent in the knowledge base, and only incidents with a cause had a change before them, so "find the change" was a shortcut. The final benchmark removed both shortcuts, and the rubric fell from 80–89% to 58%.

### 6.4 Final test

All three runs used the same 300 incidents. The two Gemma runs came from the frozen commit. The Sonnet run came from a later commit whose only changes were the new default and the Claude client.

| | Gemma, explain path | Gemma, rubric | Sonnet 5.5, explain path |
|---|---|---|---|
| Right, of 240 with a cause | 206 (86%; 81% to 90%) | 139 (58%; 52% to 64%) | 217 (90%; 86% to 94%) |
| Interval counting families | 70% to 94% | 41% to 73% | 76% to 96% |
| A change came first (180): right / wrong / abstained | 161 / 17 / 2 | 139 / 23 / 18 | 176 / 1 / 3 |
| Nothing changed (60): right / wrong / abstained | 45 / 13 / 2 | 0 / 0 / 60 | 41 / 0 / 19 |
| No cause (60): abstained / wrong | 59 / 1 | 60 / 0 | 60 / 0 |
| Precision of answers given | 86.9% | 85.8% | 99.5% |
| Unsafe actions, approval bypasses | 0, 0 | 0, 0 | 0, 0 |
| Abstained with logs withheld | 300 of 300 | 300 of 300 | 300 of 300 |
| Plan recall | 67% | 54% | 75% |
| Median time | 48 s | 39 s | 11 s |
| Cost | none per call | none per call | $6.27 |

**Explain path against the rubric.** The explain path got 67 more right with about the same precision. It fixed most of the rubric's release-blaming errors and diagnosed 45 of the 60 change-free causes. Four of the five marks set before the run passed clearly. The fifth, precision, was worded ambiguously. Read as the precision of the answers given, it passes (86.9% against 85.8%). Read literally, counting correct abstentions on no-cause incidents as right answers too, it fails by 0.1 points. The switch to the explain path was decided after seeing the result, on the first reading, and the brief records it that way.

**Where Gemma went wrong.** 29 of its 31 wrong answers came from four families, in which it named the failure by its surface symptom: a truncated upload as a timeout, a poison message as a schema mismatch, a changed filename pattern as a schema or data problem, and a receiver that stopped polling as a queue problem. Its plans also proposed more unneeded fixes than the rubric's (39 against 18); all were held for approval.

**Gemma against Sonnet.** On the incidents where only one model was right, the split was 28 for Sonnet and 17 for Gemma. An exact paired test can't tell that from chance (p = 0.14). On the incidents where only one model was wrong, the split was 30 for Gemma and 0 for Sonnet, which isn't chance (p = 2 × 10⁻⁹). Sonnet's first question named the right category for 239 of 240 incidents, against Gemma's 209. All 22 of Sonnet's misses were abstentions after a correct reading: 19 where nothing had changed, which it said nothing in the evidence explained, and 3 it judged isolated. The difference between the models is in reading the symptoms. The same code rules kept both runs safe.

### 6.5 Limits

- The incidents are synthetic and modelled on production failures, so the numbers are not yet accuracy on real incidents.
- 30 test families is a small sample of the ways an integration can fail.
- Each configuration ran once, so run-to-run variation isn't measured.
- The explain path's prompts were written alongside the development families with Gemma, which may favour Gemma.

## 7. Extending FlowGuard

Each extension below connects to an interface that already exists, so the decision logic and the safety rules stay as they are.

**Incident management (Jira, ServiceNow, PagerDuty).** An adapter receives the platform's webhook for a new incident ticket and calls `POST /investigations` with the service, symptom and time window. When the investigation finishes, a second component posts the diagnosis, the cited evidence and the plan back to the ticket as a comment. A ticket transition can call `/approve` or `/reject`, but approval still goes through FlowGuard's gate, so only steps that passed validation can run.

**Log aggregation and monitoring (Splunk, Elasticsearch or OpenSearch, Datadog, Grafana Loki and Prometheus, CloudWatch).** Each platform gets its own observability MCP server implementing the same tools: `search_logs`, `search_alerts`, `get_alert` and `get_metrics`. The server translates the incident's service and time window into the platform's query language (SPL, Lucene, LogQL, PromQL) and authenticates with a read-only service account. The call limits, the redaction and the abstention when logs can't be read apply unchanged. Deployment history comes the same way, through operations servers for GitHub or GitLab releases, Argo CD, Terraform or feature-flag services. Runbooks and API specifications come through knowledge servers for Confluence, Backstage or an OpenAPI registry.

**Vector database.** Retrieval already uses Qdrant, and setting `QDRANT_URL` points it at a managed Qdrant cluster with no code change. Moving to pgvector, OpenSearch k-NN or another store means writing an ingest and retrieve module behind the existing embedder interface. Multi-team deployments need a collection per team and access filters on retrieval.

**Relational database.** The audit store and the LangGraph checkpointer both use SQLite. For production, the audit store moves to PostgreSQL, with a database role that can only insert, which keeps the records append-only at the database level. LangGraph's PostgreSQL checkpointer holds investigations that are waiting for approval. Several API replicas can then run behind a load balancer.

**Model serving.** Any model server that returns schema-constrained JSON can implement the `LLM` interface. vLLM batches concurrent requests on one GPU and suits higher incident volumes better than Ollama. Two ways to reduce Gemma's wrong answers without sending data out are a larger open-weight model on local GPUs, or sampling each question several times and answering only when the samples agree. Where policy allows a hosted model, only the incidents the local model abstains on could be sent to it, after redaction.

**Before production.** The API has no authentication or role-based access yet; both are needed first. Tool credentials belong in a secrets manager, FlowGuard's own latency, abstention rate and tool failures need monitoring, and its accuracy has to be measured on real incidents before it is quoted.
