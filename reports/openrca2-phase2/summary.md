## Services per case

| System | Cases | Services, median [min, max] |
|---|---|---|
| ts | 60 | 49 [48, 49] |
| hs | 33 | 20 [20, 21] |
| otel-demo | 7 | 20 [20, 21] |
| all | 100 | 48 [20, 49] |

## Top 1 and top 3: a required fault's service ranked first, or in the first three

| Signal | ts top 1 | ts top 3 | hs top 1 | hs top 3 | otel-demo top 1 | otel-demo top 3 | all top 1 | all top 3 | all: median rank |
|---|---|---|---|---|---|---|---|---|---|
| T1 error share | 43% | 47% | 6% | 6% | 0% | 0% | 28% | 30% | 9 |
| T2 latency | 52% | 60% | 27% | 30% | 14% | 29% | 41% | 48% | 4 |
| T3 own time | 55% | 72% | 27% | 36% | 14% | 29% | 43% | 57% | 3 |
| T4 trace silence | 2% | 5% | 45% | 79% | 0% | 0% | 16% | 29% | 8 |
| L1 error logs | 42% | 53% | 9% | 12% | 14% | 14% | 29% | 37% | 8 |
| L2 log silence | 0% | 2% | 67% | 79% | 43% | 43% | 25% | 30% | 11 |
| M1 loudest metric | 23% | 47% | 42% | 85% | 43% | 57% | 31% | 60% | 2 |
| B0 commonest root | 2% | 13% | 52% | 64% | 0% | 0% | 18% | 29% | 7 |

Some telemetry signal (T1 to M1) puts it in the first 1: ts 83%, hs 97%, otel-demo 57%, all 86%

Some telemetry signal (T1 to M1) puts it in the first 3: ts 100%, hs 100%, otel-demo 86%, all 99%

## By kind of fault: required faults whose service is in a signal's first three

| Kind | Faults | T1 | T2 | T3 | T4 | L1 | L2 | M1 | B0 | Visible on any |
|---|---|---|---|---|---|---|---|---|---|---|
| pod_unavailable | 29 | 0% | 0% | 3% | 79% | 10% | 86% | 97% | 38% | 100% |
| network_delay | 14 | 7% | 100% | 100% | 29% | 7% | 43% | 36% | 64% | 100% |
| network_partition | 10 | 70% | 80% | 80% | 20% | 80% | 10% | 50% | 20% | 100% |
| network_loss | 8 | 25% | 100% | 100% | 0% | 25% | 0% | 62% | 0% | 100% |
| pod_failure | 8 | 0% | 12% | 100% | 0% | 38% | 0% | 25% | 12% | 100% |
| http_response_body_corrupted | 6 | 100% | 0% | 0% | 0% | 100% | 0% | 67% | 33% | 100% |
| application_method_slow | 5 | 0% | 100% | 80% | 0% | 20% | 0% | 100% | 0% | 100% |
| network_corrupt | 5 | 20% | 100% | 100% | 20% | 0% | 0% | 0% | 20% | 100% |
| http_slow | 4 | 100% | 100% | 100% | 0% | 75% | 0% | 0% | 0% | 100% |
| container_cpu_saturated | 3 | 0% | 33% | 67% | 33% | 0% | 33% | 100% | 33% | 100% |
| http_aborted | 3 | 100% | 0% | 0% | 0% | 100% | 0% | 67% | 100% | 100% |
| http_wrong_status_code | 3 | 100% | 0% | 0% | 0% | 100% | 0% | 33% | 33% | 100% |
| jvm_heap_exhausted | 3 | 0% | 100% | 100% | 33% | 33% | 0% | 33% | 0% | 100% |
| application_exception | 2 | 100% | 0% | 0% | 0% | 100% | 0% | 50% | 0% | 100% |
| wrong_return_value | 1 | 100% | 0% | 0% | 0% | 100% | 0% | 100% | 0% | 100% |

## Visibility: share of faults past a signal's cut-off, by role

| System | Role | Faults | T1 | T2 | T3 | T4 | L1 | L2 | M1 | Any |
|---|---|---|---|---|---|---|---|---|---|---|
| ts | required | 61 | 39% | 61% | 61% | 52% | 48% | 54% | 98% | 100% |
| ts | not_effective | 13 | 15% | 69% | 38% | 69% | 0% | 85% | 100% | 100% |
| hs | required | 36 | 6% | 25% | 25% | 94% | 3% | 72% | 100% | 100% |
| hs | optional | 15 | 7% | 7% | 7% | 53% | 7% | 53% | 100% | 100% |
| otel-demo | required | 7 | 0% | 29% | 29% | 71% | 0% | 57% | 86% | 100% |
| otel-demo | optional | 4 | 0% | 25% | 50% | 0% | 0% | 50% | 100% | 100% |
| otel-demo | not_effective | 1 | 100% | 0% | 0% | 100% | 0% | 0% | 100% | 100% |
| all | required | 104 | 25% | 46% | 46% | 68% | 29% | 61% | 98% | 100% |
| all | optional | 19 | 5% | 11% | 16% | 42% | 5% | 53% | 100% | 100% |
| all | not_effective | 14 | 21% | 64% | 36% | 71% | 0% | 79% | 100% | 100% |

Cases with every required fault visible on some signal: 100 of 100.

## Some telemetry signal ranks the fault's service first, or in its first three, by role (added after the first run)

| System | Role | Faults | First | First 3 |
|---|---|---|---|---|
| ts | required | 61 | 84% | 100% |
| ts | not_effective | 13 | 77% | 77% |
| hs | required | 36 | 92% | 100% |
| hs | optional | 15 | 100% | 100% |
| otel-demo | required | 7 | 57% | 86% |
| otel-demo | optional | 4 | 100% | 100% |
| otel-demo | not_effective | 1 | 100% | 100% |
| all | required | 104 | 85% | 99% |
| all | optional | 19 | 100% | 100% |
| all | not_effective | 14 | 79% | 79% |

## Where each signal's first service sits (added after the first run)

| System | Signal | Cases | required fault | other fault | entry service | on the true path | elsewhere |
|---|---|---|---|---|---|---|---|
| ts | T1 | 60 | 30 | 0 | 4 | 14 | 12 |
| ts | T2 | 60 | 31 | 3 | 13 | 9 | 4 |
| ts | T3 | 60 | 33 | 0 | 15 | 6 | 6 |
| ts | T4 | 60 | 1 | 0 | 0 | 0 | 59 |
| ts | L1 | 60 | 27 | 0 | 4 | 10 | 19 |
| ts | L2 | 60 | 0 | 0 | 0 | 0 | 60 |
| ts | M1 | 60 | 14 | 10 | 2 | 5 | 29 |
| hs | T1 | 33 | 2 | 1 | 16 | 3 | 11 |
| hs | T2 | 33 | 9 | 2 | 0 | 0 | 22 |
| hs | T3 | 33 | 9 | 2 | 3 | 0 | 19 |
| hs | T4 | 33 | 17 | 1 | 0 | 0 | 15 |
| hs | L1 | 31 | 2 | 0 | 17 | 2 | 10 |
| hs | L2 | 25 | 16 | 0 | 0 | 0 | 9 |
| hs | M1 | 33 | 15 | 15 | 1 | 0 | 2 |
| otel-demo | T1 | 7 | 0 | 1 | 2 | 4 | 0 |
| otel-demo | T2 | 7 | 1 | 0 | 0 | 0 | 6 |
| otel-demo | T3 | 7 | 1 | 1 | 0 | 0 | 5 |
| otel-demo | T4 | 7 | 2 | 0 | 0 | 0 | 5 |
| otel-demo | L1 | 6 | 0 | 1 | 0 | 0 | 5 |
| otel-demo | L2 | 4 | 0 | 0 | 0 | 0 | 4 |
| otel-demo | M1 | 7 | 3 | 2 | 0 | 0 | 2 |

## Against services with no fault (added after the first run)

The same cut-offs and ranks for the services that no fault of the case names, averaged over services and then over cases.

| System | T1 | T2 | T3 | T4 | L1 | L2 | M1 | Any | Some signal's first | Some signal's first 3 |
|---|---|---|---|---|---|---|---|---|---|---|
| ts | 2% | 12% | 7% | 43% | 3% | 44% | 73% | 85% | 4% | 17% |
| hs | 4% | 2% | 2% | 17% | 3% | 15% | 81% | 83% | 33% | 49% |
| otel-demo | 11% | 4% | 2% | 27% | 0% | 33% | 72% | 79% | 52% | 64% |
| all | 3% | 8% | 5% | 33% | 3% | 34% | 76% | 84% | 17% | 31% |

## Cases with more than one required fault (4)

- case-255 (ts, 48 services): application_method_slow: best rank 1; network_corrupt: best rank 1
- case-352 (hs, 20 services): pod_unavailable: best rank 2; pod_unavailable: best rank 1
- case-359 (hs, 21 services): pod_unavailable: best rank 2; container_cpu_saturated: best rank 1
- case-389 (hs, 20 services): network_partition: best rank 1; pod_unavailable: best rank 1
