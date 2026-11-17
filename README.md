# FlowGuard

FlowGuard finds what caused a production incident. It reads the incident's telemetry (logs, traces and metrics), names the faulty service and the kind of fault, and traces how the failure spread.

It began as an incident-response copilot tested on synthetic incidents. When it was checked on real logs, it failed, so the project changed course and rebuilt it as a team of agents for [OpenRCA 2.0](https://huggingface.co/datasets/anon-ops/ops-lite), a public benchmark of faults injected into running microservice systems. The agents were developed on 100 of the benchmark's cases, then tested once, blind, on the other 355:

| On 355 held-out cases, Claude Haiku 5.5 | Exact root cause | Cost a case | Time a case |
|---|---|---|---|
| The benchmark's standard agent | 186 (52.4%) | 3.0 cents | 1.3 min |
| **FlowGuard** | **245 (69.0%)** | 4.7 cents | 2.2 min |

On the same model, cases, tools and scorer, FlowGuard was right in 77 cases where the standard agent was wrong, and wrong in 18 where it was right (paired sign test p ≈ 7 × 10⁻¹⁰). The full result, with its limits, is in [`docs/openrca2-results.md`](docs/openrca2-results.md).

## The story

### Stage 1: a copilot on synthetic incidents

The first FlowGuard handled failures in enterprise integration flows. Given an incident, it gathered logs, deployments, alerts and metrics through MCP tools, retrieved runbooks and past incidents, named a root cause or abstained, and planned a fix that a person had to approve. It ran on a local model (`gemma4:12b`), and code, not the model, made the final decision from the model's answers.

It was measured on generated benchmarks, each test set run once with the pass marks fixed beforehand. It diagnosed 82% of the incidents with a cause in one test set and 86% in a second, larger one, planned no unsafe action and never bypassed approval. It also showed its limits. Its confidence score did not separate right answers from wrong ones, and both a fix to that score and a new decision rule failed their one check on fresh incidents. And one person had written both the incidents and the system. Stage 1 is described in [`docs/flowguard-copilot.md`](docs/flowguard-copilot.md) and [`docs/project-report.md`](docs/project-report.md).

### The turning point: real logs

On 2026-11-12, FlowGuard was checked on logs it had not been written for: [RCAEval](https://doi.org/10.5281/zenodo.14590730) RE3, real microservice logs with injected code faults. Its rules were tuned on one system (Sock Shop) and tested on two others. It named the faulty service in 33 of 60 cases, below the 50% of always guessing the most common faulty service. The cause was a design choice: a heuristic shortlist of suspect services was a hard limit on the answer, and the real faulty service was on it in only 33 cases.

The project's objective was a tool that finds what caused a real incident, and the synthetic scores had hidden how far it was from that. So the project started again, with three lessons: a heuristic may guide the model but never limit its answer, nothing is fixed on one system's evidence, and the test must be on data the project did not write.

### Stage 2: agents for OpenRCA 2.0

OpenRCA 2.0 (version 2.1.0) holds 455 incidents from three systems: TrainTicket (275), Hotel Reservation (148) and the OpenTelemetry Demo (32). Each is one or more faults injected into a running system, such as network delay, packet loss, a killed pod or a slow HTTP endpoint, with its logs, traces and metrics as Parquet tables. The answer gives each fault's service and kind, and the path the failure took.

The work went in fixed phases, each reviewed before the next:

1. **Set the rules.** Before any case was read, the cases were renamed and shuffled, and 100 were drawn as development cases. The other 355 were held out: not opened, listed or summarised until the final test.
2. **Read the task and study the data.** The public scoring code does not know the labels' new fault roles, so a scorer was written to the published definitions. A study of the development cases found that agents almost always find the faulty service but name the wrong kind of fault.
3. **Measure the baseline.** The benchmark's standard agent, a single model in a loop with SQL tools, was rebuilt and run twice on the development cases: 56 exact each time on Claude Haiku 5.5.
4. **Design, then build one part at a time.** Each part was kept only if it beat the configuration before it by a margin fixed in advance.
5. **Test once.** The chosen configuration and the standard agent each answered all 355 held-out cases before any answer was read. Then both were scored once.

| Part, on 100 development cases | Exact | Kept |
|---|---|---|
| Standard agent (three runs) | 56, 56, 54 | The baseline |
| Lead agent | 50 | As the base for the rest |
| + code survey | 62 | Yes |
| + kind check | 72 | Yes |
| + spread check (traces the failure's path) | 66 | No: missed its bar |
| Kind check, second version (measured fault signatures) | 71 | **Final**: the only version to pass the per-system check before the test |
| Kind check, third version (HTTP against network faults) | 71 | No |

A checker and an origin check were sized from the misses and not built, because they could fix too few cases.

## How it works

```
case telemetry (Parquet: logs, traces, metrics)
   │
   ├─ survey (code): every service, the calls between them, entry services,
   │                 network connections; a hint, never a limit
   ▼
lead agent: investigates with read-only SQL and drafts an answer
   │
   ├─ kind check, one subagent per drafted fault, each in a fresh context:
   │     tries to disprove the fault's kind, given a call table computed by code
   │     (latency percentiles, errors, the called service's own time, whether
   │     each end is still alive) and the measured signatures of each fault kind
   ▼
lead agent: weighs the verdicts and writes the final answer
   (faulty services, fault kinds, propagation path; schema-checked JSON)
```

All agents run on Claude Haiku 5.5. The tools are read-only.

Most of the gain comes from the kind check. On the held-out cases, the lead's drafts were right in 198. The check fixed 60 of the rest and broke 13, ending at 245. Both agents nearly always named a right service (94% and 98% of cases). Where the service was right, the standard agent named the right kind of fault 61% of the time and FlowGuard 76%.

## Results

| System | Cases | Standard agent | FlowGuard | FlowGuard won | FlowGuard lost |
|---|---|---|---|---|---|
| TrainTicket | 215 | 73 (34.0%) | **122 (56.7%)** | 58 | 9 |
| OpenTelemetry Demo | 25 | 12 (48.0%) | **20 (80.0%)** | 9 | 1 |
| Hotel Reservation | 115 | 101 (87.8%) | 103 (89.6%) | 10 | 8 |
| **All** | **355** | **186 (52.4%)** | **245 (69.0%)** | **77** | **18** |

- **The gain** is 16.6 points, with a 95% interval of 11.5 to 21.7.
- **The development cases predicted it:** 71% on development, 69.0% held out, so the choices made on the 100 development cases did not overfit them.
- **Under the public scorer's stricter rule**, where every injected fault must be named, including those the labels mark optional, FlowGuard scores 41.1% against 31.3%.

**What it does not show**

- **It is not a leaderboard result.** The published rows were measured on an older, 500-case version of the data with other labels and larger models. The best row is 46.4%, with Claude Opus 5. A claim there needs a submission under the leaderboard's rules, and there is no public route for one.
- **One run of each agent, on one model.**
- **Hotel Reservation shows no gain**, at 1.6 times the cost.
- **TrainTicket is still at 57%.** Network faults to the database read as database faults, and HTTP faults read as network faults.
- **Every case is an injected fault in a test system.** Finding the cause of real production incidents, the project's objective, is not yet demonstrated.

## Running it

You need Python 3.11 or later. The agents need an Anthropic API key in `ANTHROPIC_API_KEY`.

```bash
pip install -e ".[openrca2,claude,dev]" huggingface_hub

# The dataset at the commit used here (2.9 GB), checked file by file
hf download anon-ops/ops-lite --repo-type dataset \
    --revision 581eba39d0bfd2d397eded6cd7cbe3303255521a \
    --local-dir data/external/openrca2/raw
python -m flowguard.openrca2.download --raw data/external/openrca2/raw

# Separate the answers from the telemetry, rename the cases, draw the split (seed 20261112)
python -m flowguard.openrca2.prepare --root data/external/openrca2

# FlowGuard on the 100 development cases, stopping at $6
python -m flowguard.openrca2.baseline --root data/external/openrca2 \
    --provider claude --model claude-haiku-5-5 --agent lead+survey+kind2 \
    --sample 100 --max-usd 6 --out reports/my-dev-run
```

`--agent standard` runs the benchmark's standard agent instead. The held-out test answers every held-out case without reading any answer (`--held-out`, split across terminals with `--shard k/n`), then scores both runs once:

```bash
python -m flowguard.openrca2.final --root data/external/openrca2 \
    --standard <standard run> --design <FlowGuard run> --out compared.md
```

The tests need no data or model: `pytest`.

## Documentation

| | |
|---|---|
| [`docs/openrca2-results.md`](docs/openrca2-results.md) | The held-out result and its limits |
| [`docs/openrca2-design.md`](docs/openrca2-design.md) | The design, every measurement and decision in order, and the budget |
| [`docs/openrca2-task.md`](docs/openrca2-task.md) | The task, the scoring and the leaderboard |
| [`docs/openrca2-data.md`](docs/openrca2-data.md) | The study of the development cases |
| [`docs/openrca2-baseline.md`](docs/openrca2-baseline.md) | The standard agent, rebuilt, and how it differs from the published runs |
| [`docs/flowguard-copilot.md`](docs/flowguard-copilot.md), [`docs/project-report.md`](docs/project-report.md) | Stage 1: the copilot and its synthetic benchmarks |
| [`brief.md`](brief.md), [`CHANGELOG.md`](CHANGELOG.md) | The full working record |

## Project layout

```
src/flowguard/openrca2/   stage 2: the agents, tools, survey, scorer, runners
  design.py, subagents.py   the lead agent and the kind check
  survey.py                 the code survey and the call table
  baseline.py, final.py     development runs, the held-out test and its scoring
  score.py, failures.py     the scorer and the comparison of runs
src/flowguard/            stage 1: the copilot (graph, MCP tools, retrieval, API)
tests/                    unit tests for both stages
reports/                  every run, case by case
```

## Licence

[Apache 2.0](LICENSE).
