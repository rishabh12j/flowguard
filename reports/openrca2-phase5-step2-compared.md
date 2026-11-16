# Runs compared on 100 development cases

| Run | Exact match | hs | otel-demo | ts | Edge-F1 | Cost | Seconds a case |
|---|---|---|---|---|---|---|---|
| openrca2-baseline-haiku | 56 | 31 of 33 | 5 of 7 | 20 of 60 | 0.827 | $2.97 | 82 |
| openrca2-baseline-haiku-run2 | 56 | 32 of 33 | 7 of 7 | 17 of 60 | 0.801 | $3.23 | 80 |
| openrca2-lead-survey | 62 | 28 of 33 | 4 of 7 | 30 of 60 | 0.891 | $3.46 | 80 |
| openrca2-lead-survey-kind | 72 | 25 of 33 | 4 of 7 | 43 of 60 | 0.858 | $5.10 | 147 |

openrca2-baseline-haiku against openrca2-baseline-haiku-run2: both right in 50, both wrong in 38, only openrca2-baseline-haiku right in 6, only openrca2-baseline-haiku-run2 right in 6; exact paired test p = 1.000.

openrca2-baseline-haiku against openrca2-lead-survey: both right in 46, both wrong in 28, only openrca2-baseline-haiku right in 10, only openrca2-lead-survey right in 16; exact paired test p = 0.327.

openrca2-baseline-haiku against openrca2-lead-survey-kind: both right in 44, both wrong in 16, only openrca2-baseline-haiku right in 12, only openrca2-lead-survey-kind right in 28; exact paired test p = 0.017.

openrca2-baseline-haiku-run2 against openrca2-lead-survey: both right in 47, both wrong in 29, only openrca2-baseline-haiku-run2 right in 9, only openrca2-lead-survey right in 15; exact paired test p = 0.307.

openrca2-baseline-haiku-run2 against openrca2-lead-survey-kind: both right in 45, both wrong in 17, only openrca2-baseline-haiku-run2 right in 11, only openrca2-lead-survey-kind right in 27; exact paired test p = 0.014.

openrca2-lead-survey against openrca2-lead-survey-kind: both right in 53, both wrong in 19, only openrca2-lead-survey right in 9, only openrca2-lead-survey-kind right in 19; exact paired test p = 0.087.

## openrca2-baseline-haiku: 44 cases without an exact match

A case can show more than one problem.

| Problem | Cases |
|---|---|
| wrong kind | 32 |
| named instead: another service | 10 |
| missed a required fault | 9 |
| named instead: an entry service | 2 |
| invalid answer | 1 |
| named instead: a service on the true graph | 1 |

| Wrong kind: true -> claimed | Times |
|---|---|
| network_loss -> database_call_slow | 6 |
| network_corrupt -> database_call_slow | 3 |
| network_partition -> database_call_failed | 3 |
| jvm_heap_exhausted -> pod_failure | 3 |
| pod_failure -> process_cpu_saturated | 2 |
| http_slow -> network_delay | 2 |
| network_delay -> database_call_slow | 2 |
| network_loss -> application_method_slow | 1 |
| wrong_return_value -> application_exception | 1 |
| network_partition -> database_call_slow | 1 |
| http_wrong_status_code -> application_exception | 1 |
| network_loss -> network_delay | 1 |
| network_corrupt -> network_delay | 1 |
| network_delay -> http_slow | 1 |
| network_corrupt -> http_slow | 1 |
| http_response_body_corrupted -> application_exception | 1 |
| pod_failure -> container_cpu_saturated | 1 |
| http_slow -> application_method_slow | 1 |

## openrca2-baseline-haiku-run2: 44 cases without an exact match

A case can show more than one problem.

| Problem | Cases |
|---|---|
| wrong kind | 31 |
| named instead: another service | 12 |
| missed a required fault | 10 |
| named instead: a service on the true graph | 1 |

| Wrong kind: true -> claimed | Times |
|---|---|
| network_loss -> database_call_slow | 5 |
| network_partition -> database_call_failed | 4 |
| pod_failure -> container_cpu_saturated | 3 |
| network_corrupt -> database_call_slow | 3 |
| network_loss -> application_method_slow | 2 |
| http_slow -> network_delay | 2 |
| network_corrupt -> network_delay | 2 |
| jvm_heap_exhausted -> pod_failure | 2 |
| network_delay -> database_call_slow | 2 |
| http_aborted -> network_partition | 1 |
| wrong_return_value -> application_exception | 1 |
| network_loss -> database_call_failed | 1 |
| http_wrong_status_code -> application_exception | 1 |
| jvm_heap_exhausted -> jvm_gc_thrashing | 1 |
| pod_failure -> application_method_slow | 1 |

## openrca2-lead-survey: 38 cases without an exact match

A case can show more than one problem.

| Problem | Cases |
|---|---|
| wrong kind | 31 |
| named instead: another service | 5 |
| named instead: an entry service | 3 |
| missed a required fault | 2 |
| named instead: a service on the true graph | 1 |

| Wrong kind: true -> claimed | Times |
|---|---|
| network_loss -> database_call_slow | 6 |
| network_partition -> database_call_failed | 4 |
| network_corrupt -> database_call_slow | 3 |
| network_delay -> http_slow | 3 |
| jvm_heap_exhausted -> pod_failure | 3 |
| network_partition -> dns_lookup_failed | 2 |
| network_delay -> database_call_slow | 2 |
| network_loss -> application_method_slow | 1 |
| wrong_return_value -> application_exception | 1 |
| network_partition -> http_aborted | 1 |
| http_slow -> application_method_slow | 1 |
| network_corrupt -> http_slow | 1 |
| network_corrupt -> network_loss | 1 |
| http_slow -> network_delay | 1 |
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
