# OpenRCA 2.0: what the development cases show

Phase 2 of the plan in `brief.md`, section 33. It covers the 100 development cases only. The signals, measures and cut-offs were written in the brief before anything was measured against an answer. Three measures were added after the first run, and each is marked where it appears. Regenerate the tables with:

```
python -m flowguard.openrca2.study --root data/external/openrca2 --out reports/openrca2-phase2
```

`reports/openrca2-phase2/summary.md` holds every table; `cases.json` holds each case's ranks and values.

## The data

| | TrainTicket | Hotel Reservation | OTel Demo |
|---|---|---|---|
| Development cases | 60 | 33 | 7 |
| Services in a case | 48 to 49 | 20 to 21 | 20 to 21 |
| Size of a case | 3 to 18 MB, median 10 | under 3 MB | under 1 MB |
| Window, each period | 4 to 5 minutes | 5 minutes | 5 minutes |

- Each table has the same columns in every case. Logs carry a template column in 128 of the 200 log tables.
- OTel Demo logs have no error level at all (INFO, INFORMATION, or empty). TrainTicket also logs SEVERE.
- Every fault's service appears in at least one table, but not always in traces: for 3 required faults the named service has no spans, 2 of them appearing in logs and metrics only and 1 in metrics only.

**The answers.** The 100 cases hold 137 injected faults: 104 required, 19 optional and 14 not effective.

- **Required faults:** 96 cases have one and 4 have two. 37 cases had more than one fault injected, but in most of them the second fault is optional or not effective.
- **Optional faults:** in Hotel Reservation all 15 are CPU or memory stress; OTel Demo has 4.
- **Not effective:** TrainTicket has 13 (10 of them `JVMRuntimeMutator`); OTel Demo has 1.
- **No graph:** 5 cases have none (`process_applicable` false).
- **Hotel Reservation:** pod failure is 22 of its 36 required faults, and one service, `search`, is a root in about half its cases.

## Leaks

None found. No text column in any table holds a word from the fault-injection tooling. The only matches were metric names with "page_faults" and the word "default". The parquet files carry only their schema as metadata. Pods named after an injected service do get new names when the pod is restarted, but that is the system's own behaviour.

One weak possibility: each case runs in a numbered namespace. Most namespaces mix kinds of fault. TrainTicket's `ts6` to `ts11` each appear in one development case, all network faults, which is too few to judge. Namespaces should be hidden from agents to be safe.

## How far each signal points at the faulty service

Each signal ranks a case's services; ties count against the fault. "First 3" means a required fault's service is in the first three.

| Signal | TrainTicket first / first 3 | Hotel Res. first / first 3 | OTel Demo first / first 3 | All, first / first 3 |
|---|---|---|---|---|
| T1 error share | 43% / 47% | 6% / 6% | 0% / 0% | 28% / 30% |
| T2 latency | 52% / 60% | 27% / 30% | 14% / 29% | 41% / 48% |
| T3 own time | 55% / 72% | 27% / 36% | 14% / 29% | 43% / 57% |
| T4 trace silence | 2% / 5% | 45% / 79% | 0% / 0% | 16% / 29% |
| L1 error logs | 42% / 53% | 9% / 12% | 14% / 14% | 29% / 37% |
| L2 log silence | 0% / 2% | 67% / 79% | 43% / 43% | 25% / 30% |
| M1 loudest metric | 23% / 47% | 42% / 85% | 43% / 57% | 31% / 60% |
| B0 commonest root | 2% / 13% | 52% / 64% | 0% / 0% | 18% / 29% |
| Some signal, T1 to M1 | 83% / 100% | 97% / 100% | 57% / 86% | 86% / 99% |

Compared with services that no fault names (added after the first run), some signal ranks such a service first in 17% of cases and in its first three in 31%. For TrainTicket the figures are 4% and 17%, for Hotel Reservation 33% and 49%, and for OTel Demo 52% and 64%. OTel Demo's 57% is therefore no better than chance on 7 cases.

**By kind of fault**, the share of required faults in a signal's first three:

| Kind | Faults | Signals that show it |
|---|---|---|
| pod_unavailable | 29 | loudest metric 97%, log silence 86%, trace silence 79% |
| network_delay | 14 | latency and own time 100% |
| network_partition | 10 | latency, own time, error logs 80%; error share 70% |
| network_loss | 8 | latency and own time 100% |
| pod_failure (brief kill) | 8 | own time 100%; nothing else above 38% |
| http_response_body_corrupted, http_aborted, http_wrong_status_code, application_exception, wrong_return_value | 15 | error share and error logs 100% |
| application_method_slow | 5 | latency and loudest metric 100% |
| network_corrupt | 5 | latency and own time 100% |
| http_slow | 4 | error share, latency, own time 100% |
| container_cpu_saturated | 3 | loudest metric 100% |
| jvm_heap_exhausted | 3 | latency and own time 100% |

## Findings

1. **The service is nearly always findable, but no one signal finds it.** Some signal puts a required fault's service in its first three in 99 of 100 cases. The best single signal does so in 60% overall (the loudest metric) and in 72% of TrainTicket cases (own time). Which signal to trust depends on the kind of fault, and the kind is unknown at the start. The gain lies in choosing the right evidence per case, which is a job for judgement rather than a fixed ranking.

2. **What counts differs by system.** Silence is the strongest signal in Hotel Reservation and useless in TrainTicket, where the silence signals' first service is unrelated to the fault in 59 or 60 of 60 cases. Error share works in TrainTicket and not in Hotel Reservation. A rule fitted to one system would fail on another, which is the RE3 mistake again.

3. **Optional and not-effective faults look as faulty as required ones.** Some signal ranks every optional fault first, and 79% of the not-effective ones. In Hotel Reservation, when the loudest metric's first service is wrong, it is an optional stress fault 15 times out of 18. An anomaly at a service is no reason to name it. By the label's definition a fault is required when its effect spread beyond its own service, so whether to name a fault turns on evidence of spread, not on how loud it is. This is where exact match is won or lost.

4. **The loudest wrong answer is often downstream.** In TrainTicket, latency and own time put the entry service (`ts-ui-dashboard`) first in 13 and 15 cases. Error share and error logs in Hotel Reservation put the frontend first in 16 and 17. This is the failure the paper names: the loudest signal is often an effect.

5. **The visibility cut-offs set in the plan don't separate.** They pass 84% of services with no fault, against 100% of faulty ones; the loudest-metric cut-off alone passes 76%. So "every required fault is visible", which these cut-offs give, says nothing. The cut-offs stay as written and are reported as too loose.

6. **The second fault is not where the difficulty lies, in development.** Only 4 cases have two required faults. In all four, both services are within the first two of some signal.

7. **A dataset prior exists, and using it would be fitting the data.** Naming Hotel Reservation's commonest root (`search`) is right in 52% of its cases with no telemetry at all. It is reported as a baseline and not used.

## Limits

- OTel Demo has 7 development cases, and nothing about it is settled here.
- The signals are deliberately simple. The metric signal takes the largest shift over all of a service's metrics, which favours services with many metrics.
- The kind of fault was not studied beyond which signal shows it, so how often similar kinds can be told apart is not measured. Kind decides f1 and exact match as much as the service does.
- The time each anomaly began was not measured. It is the obvious next signal for telling cause from effect.
