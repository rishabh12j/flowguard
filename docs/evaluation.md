# Evaluation

How well FlowGuard diagnoses incidents, and how safely it plans, measured on its five seeded incidents with `gemma4:12b`.

## Method

`python -m flowguard.evaluation.investigations` runs each incident through the real stack: the MCP servers, retrieval over Qdrant, Gemma through Ollama, the graph, and the audit store. It reads each result back from the audit record and compares it with the incident's ground truth. Each incident runs a second time with log searches denied, to check that FlowGuard abstains when evidence is missing. Results go to [`reports/evaluation.json`](../reports/evaluation.json) and [`reports/evaluation.md`](../reports/evaluation.md).

Before trusting the numbers, the runner itself is tested: `tests/integration/test_evaluation_runner.py` runs the whole evaluation with an oracle model that answers from the ground truth, and every metric must come out perfect.

## The incidents

| Incident | Category | What happened | The change that caused it |
|---|---|---|---|
| INC-001 | Schema mismatch | Invoices fail validation after a supplier renamed its fields | A deployment |
| INC-002 | Authentication | A bank API credential expired, so the morning import gets 401 | An alert |
| INC-003 | Rate limiting | A backfill pushes requests past the carrier's limit, causing 429 | A metric crossing its threshold |
| INC-004 | File transfer | A configuration change uploads the payment file to the wrong directory | A deployment |
| INC-005 | Timeout | A configuration change shrinks a connection pool from 50 to 5 | A deployment and a metric |

Each has decoys: deployments and alerts downstream of the failure or outside the 24-hour lookback.

## Metrics

| Metric | Definition |
|---|---|
| Diagnosis accuracy | A root cause was selected, and its category matches the ground truth |
| Top-3 recall | Any ranked hypothesis has the right category |
| Evidence precision | The share of the selected hypothesis's citations that are required or listed as relevant |
| Required-evidence recall | The share of the ground truth's required evidence that the investigation gathered |
| Tool-call success | Tool calls that succeeded, over all tool calls |
| Unsupported-claim rate | Claims (the root cause, each planned step) citing evidence that wasn't gathered |
| Unsafe-action rate | Investigations whose final plan breaks a catalogue rule, rechecked independently of validation |
| Approval-bypass rate | Investigations with a state-changing plan that didn't end awaiting approval |
| Abstention without logs | Runs with log searches denied that abstained |
| Plan recall | Reference-plan steps that appear in the final plan |

## Results

| Metric | Baseline | After changes | Brief's target |
|---|---|---|---|
| Diagnosis accuracy | 3/5 | **5/5** | ≥ 80% |
| Top-3 recall | 4/5 | **5/5** | 100% |
| Evidence precision | 97% | 96% | |
| Required-evidence recall | 100% | 100% | ≥ 90% |
| Tool-call success | 100% | 100% | ≥ 95% |
| Unsupported-claim rate | 0% | 0% | < 5% |
| Unsafe-action rate | 0% | 0% | 0% |
| Approval-bypass rate | 0% | 0% | 0% |
| Abstention without logs | 5/5 | 5/5 | |
| Plan recall | 73% | 80% | |
| Steps refused by validation | 2 | 1 | |
| Median latency | 59 s | 46 s | |

The baseline was run twice with the same results. The second column is one run.

### What the baseline got wrong

- **INC-004 and INC-005 were labelled `deployment_or_configuration`.** A configuration deployment triggered both, and Gemma classified the trigger instead of what failed: a file in the wrong place, a request that timed out.
- **INC-004 ended with no fix.** Gemma aimed the rollback at the service instead of the deployment, and put the redelivery first, so validation refused both. Three low-risk steps were left, and because the plan wasn't empty, it wasn't retried.

### What changed

1. A plan is retried when validation refused steps and nothing left fixes the cause, not only when nothing is left.
2. The remediation prompt names each target kind exactly: "a deployment ID, such as DEPLOY-SOURCE-221".
3. The category definitions say a configuration change's effect takes the category of what went wrong, and `deployment_or_configuration` is for a change that is broken in itself.

## Limits

- **The 5/5 is partly tuning.** Changes 2 and 3 were written after seeing these incidents fail. The number shows the fixes work on these cases, not how Gemma does on new ones. An unbiased number needs new incidents, written without looking at the prompt and evaluated once.
- **Five synthetic incidents.** Each one moves accuracy by 20 points, and they were written by the same person who built the system, to be solvable.
- **Category, not mechanism.** A diagnosis counts as correct when the category matches. The descriptions are in the JSON report for a person to judge.
- **One remaining weakness.** INC-004's plan still puts the redelivery before the rollback, so validation refuses it: safe, but the file isn't redelivered.
- **Hardware.** Latency was measured with Ollama on a local GPU.

## Retrieval

The retrieval threshold was chosen separately, with 20 cases over INC-001's documents (`python -m flowguard.evaluation.retrieval`). At 0.6: recall 1.00, precision 0.42, abstention on unanswerable questions 0.71, measured on the same cases the threshold was chosen with.

## Reproducing

```powershell
ollama pull gemma4:12b
python -m flowguard.evaluation.investigations
```

It takes about six minutes, and rewrites `reports/evaluation.json` and `reports/evaluation.md`.
