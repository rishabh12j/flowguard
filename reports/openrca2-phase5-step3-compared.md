# Runs compared on 100 development cases

| Run | Exact match | hs | otel-demo | ts | Edge-F1 | Cost | Seconds a case |
|---|---|---|---|---|---|---|---|
| openrca2-baseline-haiku-run3 | 54 | 30 of 33 | 4 of 7 | 20 of 60 | 0.836 | $3.18 | 79 |
| openrca2-lead-survey-kind | 72 | 25 of 33 | 4 of 7 | 43 of 60 | 0.858 | $5.10 | 147 |
| openrca2-lead-survey-kind-spread | 66 | 27 of 33 | 5 of 7 | 34 of 60 | 0.905 | $6.36 | 188 |

openrca2-baseline-haiku-run3 against openrca2-lead-survey-kind: both right in 46, both wrong in 20, only openrca2-baseline-haiku-run3 right in 8, only openrca2-lead-survey-kind right in 26; exact paired test p = 0.003.

openrca2-baseline-haiku-run3 against openrca2-lead-survey-kind-spread: both right in 47, both wrong in 27, only openrca2-baseline-haiku-run3 right in 7, only openrca2-lead-survey-kind-spread right in 19; exact paired test p = 0.029.

openrca2-lead-survey-kind against openrca2-lead-survey-kind-spread: both right in 57, both wrong in 19, only openrca2-lead-survey-kind right in 15, only openrca2-lead-survey-kind-spread right in 9; exact paired test p = 0.307.

## openrca2-baseline-haiku-run3: 46 cases without an exact match

A case can show more than one problem.

| Problem | Cases |
|---|---|
| wrong kind | 35 |
| named instead: another service | 8 |
| missed a required fault | 6 |
| named instead: an entry service | 2 |
| invalid answer | 1 |
| named instead: a service on the true graph | 1 |

| Wrong kind: true -> claimed | Times |
|---|---|
| network_loss -> database_call_slow | 6 |
| network_partition -> database_call_failed | 4 |
| network_corrupt -> database_call_slow | 3 |
| http_slow -> network_delay | 3 |
| jvm_heap_exhausted -> pod_failure | 2 |
| network_delay -> database_call_slow | 2 |
| pod_failure -> process_cpu_saturated | 2 |
| network_loss -> application_method_slow | 1 |
| http_aborted -> network_loss | 1 |
| wrong_return_value -> application_exception | 1 |
| http_wrong_status_code -> application_exception | 1 |
| network_delay -> application_method_slow | 1 |
| network_loss -> network_delay | 1 |
| network_corrupt -> network_delay | 1 |
| jvm_heap_exhausted -> container_memory_saturated | 1 |
| network_corrupt -> http_slow | 1 |
| network_partition -> application_method_slow | 1 |
| http_response_body_corrupted -> application_exception | 1 |
| pod_failure -> application_method_slow | 1 |
| pod_failure -> container_cpu_saturated | 1 |

## openrca2-lead-survey-kind: 28 cases without an exact match

A case can show more than one problem.

| Problem | Cases |
|---|---|
| wrong kind | 22 |
| missed a required fault | 4 |
| named instead: another service | 4 |
| named instead: an entry service | 2 |
| named instead: a service on the true graph | 1 |

| Wrong kind: true -> claimed | Times |
|---|---|
| network_corrupt -> network_loss | 5 |
| jvm_heap_exhausted -> pod_failure | 3 |
| network_delay -> http_slow | 2 |
| network_partition -> dns_lookup_failed | 2 |
| network_delay -> network_loss | 2 |
| container_cpu_saturated -> process_cpu_saturated | 1 |
| pod_unavailable -> network_partition | 1 |
| wrong_return_value -> application_exception | 1 |
| network_delay -> network_partition | 1 |
| network_loss -> database_call_slow | 1 |
| network_delay -> database_call_slow | 1 |
| http_slow -> network_delay | 1 |
| pod_failure -> container_cpu_saturated | 1 |

### openrca2-lead-survey-kind: the checks, on 100 cases with a valid draft

Exact matches: 60 for the drafts, 72 for the final answers. Edge-F1: 0.855 for the drafts, 0.858 for the final answers. The checks cost $1.62.

| After the checks | Draft | Final answer | Cases |
|---|---|---|---|
| the draft stood | wrong | wrong | 12 |
| the draft stood | right | right | 52 |
| the lead answered again | wrong | wrong | 12 |
| the lead answered again | wrong | right | 16 |
| the lead answered again | right | wrong | 4 |
| the lead answered again | right | right | 4 |

## openrca2-lead-survey-kind-spread: 34 cases without an exact match

A case can show more than one problem.

| Problem | Cases |
|---|---|
| wrong kind | 29 |
| named instead: another service | 4 |
| missed a required fault | 2 |
| named instead: an entry service | 1 |

| Wrong kind: true -> claimed | Times |
|---|---|
| network_corrupt -> network_loss | 5 |
| network_partition -> database_call_failed | 3 |
| network_loss -> database_call_slow | 3 |
| network_delay -> network_loss | 3 |
| network_delay -> http_slow | 2 |
| http_slow -> network_delay | 2 |
| jvm_heap_exhausted -> process_cpu_saturated | 2 |
| network_delay -> database_call_slow | 2 |
| network_loss -> application_method_slow | 1 |
| wrong_return_value -> application_exception | 1 |
| http_response_body_corrupted -> network_corrupt | 1 |
| jvm_heap_exhausted -> container_memory_saturated | 1 |
| network_partition -> dns_lookup_failed | 1 |
| network_partition -> pod_unavailable | 1 |
| pod_failure -> container_cpu_saturated | 1 |

### openrca2-lead-survey-kind-spread: the checks, on 100 cases with a valid draft

Exact matches: 62 for the drafts, 66 for the final answers. Edge-F1: 0.871 for the drafts, 0.905 for the final answers. The checks cost $2.51.

| After the checks | Draft | Final answer | Cases |
|---|---|---|---|
| the draft stood | wrong | wrong | 6 |
| the draft stood | right | right | 38 |
| the lead answered again | wrong | wrong | 24 |
| the lead answered again | wrong | right | 8 |
| the lead answered again | right | wrong | 4 |
| the lead answered again | right | right | 20 |
