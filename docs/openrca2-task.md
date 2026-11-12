# OpenRCA 2.0: the task and how it is scored

Phase 1 of the plan in `brief.md`, section 33. Written on 2026-11-12 from the paper (arXiv 2606.27154v2), the dataset's README, the leaderboard site and the official scoring code. No case was opened for it.

## What an agent is given

- One case: ten parquet tables. Traces, logs and three kinds of metrics (`metrics`, `metrics_sum`, `metrics_histogram`), each for a normal period before the fault and for the abnormal period.
- A fixed text, the same for every case: a user reports that requests are slow or failing, and the agent is told where the tables are.
- Nothing else. It gets no dependency map, no time of the fault, no alarmed endpoint, and no count of faults. A case holds one or more faults; 176 of the 455 have more than one.

## What it must return

One JSON object with two lists.

```json
{
  "root_causes": [
    {"service": "...", "fault_kind": "...", "evidence": [{"kind": "metric|trace|log", "sql": "...", "claim": "..."}]}
  ],
  "propagation": [
    {"from": "...", "to": "...", "evidence": [{"kind": "trace", "sql": "...", "claim": "..."}]}
  ]
}
```

- `service` is a service name as it appears in the data. One entry for each separate fault.
- `fault_kind` is one of 25 fixed values, named for what is seen in the telemetry and not for how the fault was injected: 2 for pods, 6 for the network, 4 for HTTP, 5 for resources, 5 for application code and database calls, 2 for DNS, and clock skew. The paper lists older names for 15 of them; the scoring code accepts both. (The code's own notes say 26, which counts `unknown`, a value an agent must not give.)
- A `propagation` edge runs the way the fault spread, from the failing service towards the service the user reaches. It is not the direction of the call, which is usually the opposite.
- Every root cause and every edge needs at least one piece of evidence: a DuckDB `SELECT` over the case's tables and a claim of at most 20 words.
- Load generators are not services and must not be named.

## How one case is scored

The scoring code is public: `rcabench_platform/v3/sdk/evaluation` in `github.com/OperationsPAI/aegis` (commit `979ae70`, 2026-08-11).

**Matching a claim to a fault.** Names are compared in lower case with hyphens and underscores removed. Each claim is paired with at most one true fault, and each fault with at most one claim.

| Result | Meaning |
|---|---|
| Hit | The service is right and the kind is right |
| Wrong kind | The service is right and the kind is wrong |
| Miss | The service is wrong |

- For a network fault, either end of the affected link counts as the right service. For every other kind, only the service the fault was injected on counts. For an HTTP fault that is the calling service.
- Two pairs of kinds count as the same answer: `pod_failure` with `pod_unavailable`, and `network_loss` with `network_partition`.

**The leaderboard's columns.** The site does not define them. This table matches them to the scoring code by name; the two marked rows are not confirmed.

| Column | Field in the code | What it is for one case |
|---|---|---|
| f1 | `f1` | Harmonic mean of hits / claims and hits / true faults |
| acc | `exact_match` | 1 when every claim is a hit and every true fault is hit; an extra claim or a wrong kind makes it 0 |
| any-hit (not confirmed) | `any_service_hit` | 1 when at least one true fault's service is named, kind ignored |
| all-hit | `all_service_hit` | 1 when every true fault's service is named, kind ignored |
| type-acc | `fault_kind_accuracy` | Hits / (hits + wrong kinds); a case with neither is left out of the mean |
| node-F1 | `node_f1` | F1 of the services in the answer against the services in the true graph |
| edge-F1 | `edge_f1` | F1 of the answer's edges against the true edges, direction counted |
| path-acc (not confirmed) | `path_reachability` | 1 when a hit root cause is joined to an alarmed service through the answer's own edges, in either direction |

- Every column is a mean over all cases. An answer that is not valid JSON scores 0 on all of them.
- The code anchors path-acc on a hit; the paper's main table anchors it on a right service of any kind. Which one the site shows is not stated.
- Two more scores exist and are not on the leaderboard: the share of evidence queries that run and return a row, and a model's judgement of whether each query supports its claim.

## The numbers to beat, and why they are not on our cases

Top rows on 2026-11-12, all with the standard agent:

| Model | f1 | acc | any-hit | all-hit | type-acc | node-F1 | edge-F1 | path-acc |
|---|---|---|---|---|---|---|---|---|
| Claude Opus 5 | 61.37 | 46.40 | 88.80 | 64.00 | 77.36 | 80.15 | 66.99 | 68.80 |
| GPT-5.6 Sol | 54.43 | 38.00 | 84.20 | 54.00 | 74.47 | 76.05 | 61.29 | 59.60 |
| Claude Fable 5 | 53.36 | 35.20 | 85.20 | 51.20 | 73.59 | 78.80 | 66.07 | 62.00 |
| Claude Sonnet 5 | 43.20 | 27.20 | 85.20 | 51.40 | 60.09 | 78.79 | 64.10 | 50.00 |

Across the 28 rows, a right service is named in 67% to 89% of cases, while acc runs from 14% to 46%. The points are lost on the kind of fault, on the second fault, and on extra claims.

**These rows were measured on an older version of the dataset.** The site was last updated on 2026-07-25. The dataset was replaced on 2026-09-26, first by a 457-case release and then by version 2.1.0, whose commit message reads "fault-role labeling fix + round-6 propagation admission (455 instances)". That is the commit we downloaded. The leaderboard's percentages are whole counts out of 500 (46.40% is 232 of 500; it is no whole number of 455), and the paper also reports 500 cases. So the published rows are on 500 cases with the old labels, and our held-out set is 355 of the 455 cases with the new labels. A score on our cases cannot be set directly against a published row.

**No public scorer knows the new labels.** The public code takes every injected fault from `injection.json` as a true fault. Version 2.1.0 makes `label.json` the authority and gives each fault a role:

| Role | Effect on scoring, from the README |
|---|---|
| `required` | Part of the answer an agent must recover |
| `optional` | Naming it is neither required nor penalised |
| `not_effective` | Not part of the answer; naming it counts as a wrong root cause |

Three faults also carry `also_accept`, a list of other services that count as naming them. The label's `service_edges` is the graph that node-F1, edge-F1 and path-acc are computed on, and cases with `process_applicable` false are skipped by those three (18 of 455). The scorer for this project therefore has to be written here: the public code's matching, with the README's roles. Its numbers follow the published definitions and are not official.

## The standard agent

- One model in a loop with four tools: list the tables, read a table's columns, run a SQL query, and write a note to itself. When it stops calling tools, a second call turns the transcript into the JSON answer.
- About 50 tool calls a case are advised and 100 is the cap. Temperature is 0.7.
- The second call is given the answer format and the list of kinds. In the August code this text also carries a short definition of each kind and rules for telling similar kinds apart (`fault_kind_disambiguation.md`); the version printed in the paper in June has only the list. Whether the leaderboard's runs had the longer text is not known. It ships with the scoring code for agents to use, so using it is within the task.
- A co-author's adaptation of the agent is public (`github.com/QishengLu/rca_study_thinkdepthai`, commit `26b5166`, 2026-11-03), and the prompts are printed in the paper's appendix F.4. The leaderboard marks the scaffold as not open, and the harness that drives it is not in that repository. In that code a query returns 10 rows by default, and a result over about 5,000 tokens is refused with a suggested `LIMIT`.

## Other published results, for scale

- Across the paper's 11 models: exact match 20.7%, F1 34.1%, a right service 76.0%, a path to the alarm 61.5%.
- Twelve algorithms that use no language model were run on the 500-case version and scored on ranking the services (`github.com/OperationsPAI/rcabench-leaderboard`). The best put a true root service first in 35% of cases, in the top three in 59% and in the top five in 70%. A one-rule baseline reached 33%, 53% and 65%.

## What is still open

1. **What "beat the leaderboard" can mean.** Either the published rows are treated as a rough guide only, or the standard agent is run on our held-out cases with our scorer to get a like-for-like baseline. The second is the only fair comparison and it costs model calls on 355 cases. Decided in phase 4, with the cost known from phase 3.
2. **The scorer's open points.** Drafted in phase 2 in `src/flowguard/openrca2/score.py`, waiting for review. A left-over claim naming an optional fault is set aside (it counts in neither precision's numerator nor its denominator, and does not break an exact match). A claim naming a not-effective fault is wrong. The true graph is the label's `service_edges`. Path reachability's targets are the services of `causal_graph.json`'s alarm nodes. The other end of a network link comes from `injection.json`.
3. **Authors' guidance outside the agent's prompt.** The scoring code's design note (`openrca-2-lite.md`, section 3) gives further rules for telling kinds apart, some with thresholds measured on labelled cases of the whole set, which includes our held-out cases. It was read during this phase. Proposed rule: the scoring rules are part of the task and are used; the thresholds are not used unless the final report says so.
4. **Column mapping.** any-hit and path-acc are matched by name only.
