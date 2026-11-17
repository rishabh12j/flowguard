# FlowGuard: Checking the Kind of Fault Lifts an LLM Root-Cause Agent on OpenRCA 2.0

**Rishabh Jain** · November 2026

## Abstract

Root cause analysis (RCA) asks an agent to find, from a failing system's telemetry, which component broke, how it broke, and how the failure spread. FlowGuard began as an incident-response copilot evaluated on synthetic incidents. There it diagnosed 82 to 86% of held-out incidents, but on real microservice logs it named the faulty service in only 33 of 60 cases, below a guess-the-most-common-service baseline. We therefore rebuilt it for OpenRCA 2.0 [1], a cross-system benchmark of faults injected into running microservice systems. A study of the benchmark's standard agent on development cases showed where it fails: it nearly always reaches a faulty service, and most of its misses name the wrong *kind* of fault. FlowGuard targets that gap. Code surveys the telemetry, a lead agent drafts a diagnosis, and for each drafted fault a subagent in a fresh context tries to disprove its kind. The subagent works from a table of the service's calls computed by code and from fault signatures measured on development cases. Every part was developed on 100 cases and kept only if it cleared a bar fixed in advance. On the other 355 cases, run once and blind, FlowGuard on Claude Haiku 5.5 reaches 69.0% exact match against 52.4% for the standard agent on the same model: 77 cases won and 18 lost (paired sign test p ≈ 7 × 10⁻¹⁰), at 4.7 cents a case.

## 1 Introduction

When a production system fails, the symptom rarely appears where the fault is. A delay injected on one service's network link surfaces as timeouts three calls upstream; a killed pod surfaces as errors in its callers, while the pod itself goes silent. An engineer, or an agent, must reason backward from traces, metrics and logs to the originating fault. Recent benchmarks pose this to LLM agents [1, 2, 3], mostly with ground truth obtained by *fault injection*: a known component is broken on purpose, and the agent must recover what was broken, how, and along which path the failure travelled.

This project started elsewhere. Its first stage, an incident-response copilot for enterprise integration flows, was tuned and tested on incident sets generated for it (Section 4.2). The scores were good, but one person had written both the incidents and the system. When FlowGuard was checked on real logs from RCAEval [3], it failed (Section 4.3). The main cause was a design choice: a heuristic shortlist of suspect services limited the answer. The project restarted against OpenRCA 2.0 with three rules: a heuristic may guide an agent but never limit its answer; nothing is fixed on the evidence of one system; and the final test runs once, on cases never opened during development.

On OpenRCA 2.0, a rebuild of the benchmark's standard agent [1, 5] showed a clear pattern on 100 development cases. The agent almost always reached a faulty service. It lost most of its points by naming the wrong kind of fault: a network fault on the link to a database read as a failing database call, or an HTTP fault blamed on the service that received the call. These confusions are not random. Each fault kind leaves a measurable signature in the telemetry, and the agent was not looking for it.

**Contributions.**

1. **A design for kind verification.** For each fault in a lead agent's draft, a fresh-context subagent tries to disprove the claimed kind. It works from a call table computed by code and from fault signatures measured on development data, and it reports to the lead, which keeps the final word (Section 2).
2. **A development protocol for agents.** Each part is added alone, measured on 100 development cases, and kept only by a rule fixed before its run. The held-out cases stay sealed until a single blind run, which is scored once (Section 3.1).
3. **A held-out result.** On 355 sealed cases, FlowGuard reaches 69.0% exact match against 52.4% for the standard agent on the same model. The gain is concentrated in fault kind, and the development score predicted it (Section 3.3).
4. **A record of what failed.** It covers parts that missed their bars, the earlier stage that failed on real logs, and the remaining failure modes (Sections 3.2, 3.4 and 4).

## 2 FlowGuard

### 2.1 Setting

A case is one incident: Parquet tables of logs, traces and metrics from a microservice system, over a window around one or more injected faults. The agent sees only the telemetry. It gets no dependency map, no fault time and no count of faults. It answers in a fixed JSON schema: a set of root causes, each a (service, fault kind) pair with SQL evidence, and the propagation edges between services. The answer must hold at least one root cause.

### 2.2 Pipeline

```
case telemetry (Parquet: logs, traces, metrics)
  │
  ├─ (1) survey, by code: every service and its activity, the calls between
  │       services, the entry services, network connections. A hint, never a limit.
  ▼
(2) lead agent: investigates with read-only SQL tools, drafts an answer
  │
  ├─ (3) kind check: for each drafted fault (up to 3), a subagent in a fresh
  │       context tries to disprove the fault's kind, within 20 tool calls, given
  │         · a call table computed by code for the claimed service: per
  │           operation, calls a minute, error share, caller p25/p50/p95 and
  │           the callee's own p50, normal period against incident; whether
  │           each end is still alive in spans, logs and metrics
  │         · the measured signatures of each fault kind (Table 1)
  ▼
(4) lead agent: reads the verdicts, writes the final answer
```

*Figure 1: FlowGuard's pipeline. All agents are Claude Haiku 5.5. The tools are read-only.*

**Survey.** Before the lead starts, code summarises the case. It lists each service's spans, logs and metric rows a minute, the call graph seen in traces, the entry services, and per-connection network metrics. It ranks nothing and excludes nothing. On development cases it raised exact matches from 50 to 62 (17 cases gained, 5 lost; p = 0.017).

**Lead agent.** The lead receives the survey and the same SQL tools as the standard agent. Its prompt states the benchmark's placement rules: an HTTP fault belongs to the calling service, and a network fault may be named at either end of the link.

**Kind check.** Agents answering in one context tend to commit to their first reading. The kind check gives each drafted fault to a new subagent whose task is to disprove the claimed kind, not to confirm it. Its evidence is computed by code, so it does not depend on the subagent writing the right query. Its brief contains the fault signatures measured on development cases (Table 1). The lead then sees each verdict and its evidence, and may keep or change its draft.

| Fault kind | Signature on the faulty link, measured on development cases |
|---|---|
| `network_delay` | Every request on the link is slower; no errors |
| `network_loss`, `network_corrupt` | A latency tail in steps of about 200 ms, from retransmission; the two cannot be told apart |
| `network_partition` | Calls fail while the callee stays alive; at once in Hotel Reservation, after a hang of about 130 s in TrainTicket |
| `pod_unavailable`, `pod_failure` | The service goes silent: no spans or logs |
| `http_slow`* | p25, p50 and p95 all rise by the same fixed amount; a network delay instead widens the spread, except in OTel Demo |
| `http_aborted`* | Calls fail at once, with "Unexpected end of file from server" |

*Table 1: Fault signatures in the kind check's brief. \* From a later study, used only in the third version of the check, which was not kept (Section 3.2).*

## 3 Experiments

### 3.1 Setup

**Data.** OpenRCA 2.0 version 2.1.0 [6] holds 455 cases from three systems: TrainTicket (275), Hotel Reservation (148) and the OpenTelemetry Demo (32). Before any case was read, the answer files were moved out of the case folders. The cases were renamed `case-001` to `case-455` in shuffled order, and 100 were drawn as development cases, in proportion per system (seed 20261112). The other 355 (TrainTicket 215, Hotel Reservation 115, OTel Demo 25) were held out. They were not opened, listed or summarised until the final run.

**Ground truth and scoring.** Version 2.1.0 gives each injected fault a role: *required*, *optional* or *not effective*. The public scoring code [8] predates the roles and treats every injected fault as required. We therefore rebuilt the scorer to the published metric definitions with the roles applied. We report both: the roles (the main measure, fixed before the test) and the public rule.

**Baseline.** The standard agent is the benchmark's reference agent [1]: a single model in a ReAct-style loop [4], adapted from the Deep Research agent [5], with tools to list tables, read a table's layout, run SQL and keep notes, and up to 100 tool calls. We rebuilt it from the paper's prompts and a co-author's public tools [7]. Both agents use the same model, tools and answer schema.

**Model.** Claude Haiku 5.5 throughout, chosen for cost. A local `gpt-oss:20b` was ten times slower and weaker. Claude Sonnet 5.5 was estimated at $1 to $3 a case.

**Protocol.** Development went one part at a time. Before each run, a keep rule was fixed: at least 8 more exact matches than the configuration the part was added to, and no system worse by more than 2. Before the held-out test, a per-system check required the final configuration to be within 2 exact matches of the standard agent's runs on every system. The held-out bar was also fixed in advance: more exact matches than the standard agent, with an exact paired sign test p < 0.05. In the final test, both agents answered all 355 held-out cases before any answer was read. A separate step then scored both runs once.

**Metrics** (following [1]). *EM*: every claimed (service, kind) is right and every required fault is claimed. *F1, Precision, Recall*: over (service, kind) pairs. *AnySvc*: at least one right root-cause service, kind ignored. *Type acc.*: right kind among right services. *PR* (path reachability): a right root-cause service joined to an alarmed service by the answer's own edges. *Node F1, Edge F1*: the answer's propagation graph against the labelled one; 13 held-out cases without a labelled graph are skipped.

### 3.2 Development

| Configuration, 100 development cases | Hotel Res. (33) | OTel Demo (7) | TrainTicket (60) | **All** | Cost a case | Kept |
|---|---|---|---|---|---|---|
| Standard agent, run 1 | 31 | 5 | 20 | 56 | 3.0¢ | Baseline |
| Standard agent, run 2 | 32 | 7 | 17 | 56 | 3.2¢ | Baseline |
| Standard agent, run 3 (fixed tool) | 30 | 4 | 20 | 54 | 3.2¢ | Baseline |
| Lead agent | 22 | 4 | 24 | 50 | 5.1¢ | As base |
| + survey | 28 | 4 | 30 | 62 | 3.5¢ | Yes |
| + kind check | 25 | 4 | 43 | 72 | 5.1¢ | Yes |
| + kind check + spread check | 27 | 5 | 34 | 66 | 6.4¢ | No |
| + kind check, v2 (Table 1 signatures, call table) | 31 | 6 | 34 | **71** | 4.6¢ | **Final** |
| + kind check, v3 (adds HTTP signatures) | 29 | 3 | 39 | 71 | 4.9¢ | No |

*Table 2: Every configuration measured during development. Runs 1 and 2, and the configurations up to the kind check, used a tool with a time-zone fault, fixed before run 3.*

**(1) The kind check carries the gain, and its versions tie.** The first version took its run's drafts from 60 to 72 exact. The three versions scored 72, 71 and 71, and no two differ case by case (p = 1.0). Per system they swing far more: TrainTicket 43, 34 and 39. The lead's drafts, written before any check, already varied by 4 cases per system between runs. The second version was chosen because it was the only configuration to pass the per-system check before the test.

**(2) A spread check did not pay.** A subagent that traced each fault's path, link by link, raised edge F1 by 0.035 against a bar of 0.05. Alongside it, the lead accepted correct kind verdicts less often. A code checker and an origin check (which service started the failure) were sized from the misses first: each could fix at most 3 to 8 cases, so neither was built.

**(3) Targeted fixes work on their target, and the total does not move.** The third version fixed the confusion it was built for: HTTP-fault cases went from 9 of 16 right to 15 of 16. It lost an equal number elsewhere, within run-to-run noise.

### 3.3 Held-out results

| Agent (Haiku 5.5), 355 cases | EM | F1 | Precision | Recall | AnySvc | Type acc. | PR | Node F1 | Edge F1 |
|---|---|---|---|---|---|---|---|---|---|
| Standard agent | 52.4 | 55.9 | 55.8 | 56.9 | 94.4 | 61.0 | 93.0 | 90.2 | 81.7 |
| **FlowGuard** | **69.0** | **72.3** | **72.3** | **73.1** | **97.5** | **75.9** | **97.1** | **90.5** | **83.1** |
| *Public rule: every injected fault required* | | | | | | | | | |
| Standard agent | 31.3 | 48.7 | | | 94.4 | 61.0 | 93.0 | 90.2 | 81.7 |
| **FlowGuard** | **41.1** | **62.9** | | | **97.5** | **75.7** | **97.1** | **90.5** | **83.1** |

*Table 3: Held-out results (percent). One blind run of each agent, scored once.*

| System | Cases | Standard agent EM | FlowGuard EM | Won | Lost | p |
|---|---|---|---|---|---|---|
| TrainTicket | 215 | 73 (34.0%) | **122 (56.7%)** | 58 | 9 | 7 × 10⁻¹⁰ |
| OTel Demo | 25 | 12 (48.0%) | **20 (80.0%)** | 9 | 1 | 0.02 |
| Hotel Reservation | 115 | 101 (87.8%) | 103 (89.6%) | 10 | 8 | 0.81 |
| **All** | **355** | **186 (52.4%)** | **245 (69.0%)** | **77** | **18** | **7 × 10⁻¹⁰** |

*Table 4: Exact match by system. Won: FlowGuard right where the standard agent is wrong. Lost: the reverse. p: exact paired sign test.*

**(1) The bar is met by a wide margin.** FlowGuard gains 16.6 points of exact match (95% interval 11.5 to 21.7). Under the public rule it still leads, 41.1% against 31.3% (51 won, 16 lost; p = 2 × 10⁻⁵).

**(2) The gain is in the kind of fault.** Both agents nearly always reach a right service (AnySvc 94.4 and 97.5). Type accuracy rises from 61.0 to 75.9. In the kind check, the lead's drafts were right in 198 cases. The check fixed 60 and broke 13, ending at 245. Propagation barely changes (Edge F1 81.7 and 83.1), as expected of a design that does not target it.

**(3) The gain follows the difficulty.** Hotel Reservation leaves almost no room: the standard agent is at 87.8%, and the two agents tie. TrainTicket, with 44 services and the longest propagation paths [1], gains 22.7 points. OTel Demo gains 32, on only 25 cases.

**(4) Development predicted the test.** FlowGuard scored 71% on development and 69.0% held out; the standard agent 54 to 56% and 52.4%. The choices made on the 100 development cases did not overfit them.

### 3.4 Remaining failure modes

| Miss, held-out | Standard agent | FlowGuard |
|---|---|---|
| Right service, wrong kind | 128 (116 in TrainTicket) | 83 (74 in TrainTicket) |
| All right, plus an extra claim | 13 | 11 |
| No right service named | 18 | 9 |
| One of several faulty services missed | 8 | 7 |
| Unreadable answer | 2 | 0 |
| **Total** | **169** | **110** |

*Table 5: Held-out misses by class.*

Wrong kind remains the largest class. From the development cases, three confusions dominate. First, a network fault on the link to MySQL is drafted as a slow or failed database call; the check found the right kind with the right evidence, and the lead sometimes kept its draft anyway. Second, HTTP faults are read as network faults. Third, packet loss and corruption are confused, and they leave the same signature. Why the lead overrode correct verdicts is not known: its reasoning is not visible in the transcripts.

### 3.5 Cost

| Per case, held-out | Standard agent | FlowGuard |
|---|---|---|
| Cost | 3.0 cents | 4.7 cents |
| Time | 1.3 min | 2.2 min |
| Tool calls | 28.6 | 20.4 |

FlowGuard costs 1.6 times as much for 1.3 times the exact matches. The final test cost $27.61 for both agents together.

## 4 Related Work and Project History

### 4.1 RCA benchmarks and agents

OpenRCA [2] framed RCA as a task for LLM agents over raw telemetry, scored on the root cause alone. OpenRCA 2.0 [1] adds verified causal propagation paths and process-level metrics, and reports that agents often name a right service without grounding it in a path. RCAEval [3] collects injected faults with telemetry across three systems and scores service ranking. The agents evaluated in [1] share one architecture, a ReAct-style loop [4] with SQL tools. FlowGuard keeps those tools and adds structure around them: a code survey, and verification by a separate agent with evidence computed by code.

### 4.2 Stage 1: a copilot on synthetic incidents

The first FlowGuard investigated integration-flow incidents. It gathered logs, deployments, alerts and metrics through MCP tools and retrieved runbooks and past incidents. Then it named a root cause or abstained, and planned a fix that a person had to approve. It ran on a local model (`gemma4:12b`), and code made the final decision from the model's answers. Each held-out set was run once:

- **First generated test set:** it diagnosed 82% of the incidents with a cause (186 of 228, interval 76 to 86%).
- **A second, larger set:** 86% (206 of 240).
- **Safety:** it planned no unsafe action and bypassed no approval.

Its confidence score did not separate right answers from wrong ones. Both a fix to that score and a new decision rule failed their single check on fresh incidents. Stage 1 is described in [`docs/flowguard-copilot.md`](docs/flowguard-copilot.md) and [`docs/project-report.md`](docs/project-report.md).

### 4.3 The check that failed: real logs

On RCAEval RE3 [3], real logs from three microservice systems with injected code faults, FlowGuard's rules were tuned on Sock Shop and tested once on Online Boutique and Train Ticket. Gemma and Claude Sonnet each named the faulty service in 33 of 60 cases. Always guessing the most common faulty service scores 50%. The faulty service was on FlowGuard's heuristic shortlist in only 33 cases, and the shortlist was a hard limit on the answer. In 23 of the misses the faulty service logged only routine restart lines. This failure set the rules of the restart (Section 1).

## 5 Assumptions and Threats to Validity

**Internal threats.**
- **One run, one model.** Each agent ran once on the held-out cases, on one model. On development cases, two runs of the standard agent differed in 12 of 100 cases, with equal totals. A net 59 in 355 is far outside that, but each per-system count is a single noisy reading, and OTel Demo has 25 cases.
- **Reused development cases.** The development cases were reused across studies and versions, so the development scores in Table 2 are optimistic. The held-out cases were never used for any choice.
- **Our own scorer.** The scorer is a rebuild to published definitions, not the official code, which does not handle fault roles. Rescoring 400 saved development answers reproduced the scores written at run time exactly.

**Comparison with published numbers.**
- **Not a leaderboard result.** The published results [1] were measured on an earlier 500-case release with different labels, on other models. The paper's best EM is 29.4%; the leaderboard site, last updated in July 2026, shows 46.4%.
- **The numbers do not transfer.** Our rebuilt standard agent on the small Haiku model already scores 31.3% under the public rule on our cases. That is above the paper's best, which shows the settings differ too much for a direct comparison.
- **What a claim would need.** A submission under the leaderboard's rules. We found no public route for one.

**External transfer.** Every case is a fault injected into a test system. Production incidents are messier: several overlapping changes, partial telemetry, no clean injection window. FlowGuard's objective is a tool that finds what caused a real incident, and this is not demonstrated here. The signatures in Table 1 were measured on three systems and may not hold on others.

## 6 Conclusion

On OpenRCA 2.0, LLM agents rarely fail to find the broken service; they fail to say how it broke. FlowGuard closes part of that gap. A fresh-context subagent tries to disprove each drafted fault's kind, against evidence computed by code and signatures measured on the data. This lifts exact match from 52.4% to 69.0% on 355 sealed cases, on the same small model. The result rests on the protocol as much as the design: parts kept only by bars fixed in advance, held-out cases sealed until one blind run, and a record of what did not work. The next step is a check on real incidents, where the earlier stage of this project failed.

## References

[1] A. Fang, Y. Yang, J. Shang, Q. Lu, J. Xu, R. Wang, S. Zhang, Y. Zhang, B. Yu, P. He. *OpenRCA 2.0: From Outcome Labels to Causal Process Supervision.* arXiv:2606.27154, 2026.

[2] J. Xu, Q. Zhang, Z. Zhong, S. He, C. Zhang, Q. Lin, D. Pei, P. He, D. Zhang, Q. Zhang. *OpenRCA: Can Large Language Models Locate the Root Cause of Software Failures?* ICLR 2025.

[3] L. Pham, H. Zhang, H. Ha, F. Salim, X. Zhang. *RCAEval: A Benchmark for Root Cause Analysis of Microservice Systems with Telemetry Data.* Companion Proceedings of the ACM Web Conference 2025. Data: [doi:10.5281/zenodo.14590730](https://doi.org/10.5281/zenodo.14590730).

[4] S. Yao, J. Zhao, D. Yu, N. Du, I. Shafran, K. Narasimhan, Y. Cao. *ReAct: Synergizing Reasoning and Acting in Language Models.* ICLR 2023.

[5] P. Lin. *Deep Research.* [github.com/thinkdepthai/Deep_Research](https://github.com/thinkdepthai/Deep_Research), 2025.

[6] OpenRCA 2.0 dataset, version 2.1.0. [huggingface.co/datasets/anon-ops/ops-lite](https://huggingface.co/datasets/anon-ops/ops-lite), commit `581eba39d0bfd2d397eded6cd7cbe3303255521a`.

[7] Q. Lu. *rca_study_thinkdepthai.* [github.com/QishengLu/rca_study_thinkdepthai](https://github.com/QishengLu/rca_study_thinkdepthai), commit `26b5166`.

[8] OpenRCA 2.0 scoring code. [github.com/OperationsPAI/aegis](https://github.com/OperationsPAI/aegis), commit `979ae70`.

## Appendix A: Reproducing the results

Python 3.11 or later. The agents need an Anthropic API key in `ANTHROPIC_API_KEY`.

```bash
pip install -e ".[openrca2,claude,dev]" huggingface_hub

# The dataset at the commit used here (2.9 GB), then checked file by file
hf download anon-ops/ops-lite --repo-type dataset \
    --revision 581eba39d0bfd2d397eded6cd7cbe3303255521a \
    --local-dir data/external/openrca2/raw
python -m flowguard.openrca2.download --raw data/external/openrca2/raw

# Move the answers out of the case folders, rename the cases, draw the split
python -m flowguard.openrca2.prepare --root data/external/openrca2

# FlowGuard on the 100 development cases, stopping at $6
python -m flowguard.openrca2.baseline --root data/external/openrca2 \
    --provider claude --model claude-haiku-5-5 --agent lead+survey+kind2 \
    --sample 100 --max-usd 6 --out reports/my-dev-run
```

- **The standard agent:** `--agent standard`.
- **The held-out test:**
  - Each agent runs with `--held-out`, which answers every held-out case without reading an answer. It can be split across terminals with `--shard k/n`.
  - The two runs are then scored once, together:
    ```bash
    python -m flowguard.openrca2.final --root data/external/openrca2 \
        --standard <standard run> --design <FlowGuard run> --out compared.md
    ```
- **Tests:** `pytest`. They need no data and no model.

Every run in this README is kept case by case in [`reports/`](reports/), with each agent's full transcript.

## Appendix B: Documentation and layout

| Document | Contents |
|---|---|
| [`docs/openrca2-results.md`](docs/openrca2-results.md) | The held-out result in full |
| [`docs/openrca2-design.md`](docs/openrca2-design.md) | The design, every measurement and decision in order, and the budget |
| [`docs/openrca2-task.md`](docs/openrca2-task.md) | The task, the scoring and the leaderboard |
| [`docs/openrca2-data.md`](docs/openrca2-data.md) | The study of the development cases |
| [`docs/openrca2-baseline.md`](docs/openrca2-baseline.md) | The rebuilt standard agent and its known differences |
| [`docs/flowguard-copilot.md`](docs/flowguard-copilot.md), [`docs/project-report.md`](docs/project-report.md) | Stage 1 |
| [`brief.md`](brief.md), [`CHANGELOG.md`](CHANGELOG.md) | The full working record |

```
src/flowguard/openrca2/    stage 2
  design.py, subagents.py    the lead agent and the kind check
  survey.py                  the survey and the call table
  baseline.py, final.py      development runs, the held-out test and its scoring
  score.py, failures.py      the scorer and run comparison
src/flowguard/             stage 1: the copilot (graph, MCP tools, retrieval, API)
tests/                     unit tests for both stages
reports/                   every run, case by case
```

Licensed under [Apache 2.0](LICENSE).
