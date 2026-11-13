# Runs compared on 100 development cases

| Run | Exact match | hs | otel-demo | ts | Cost | Seconds a case |
|---|---|---|---|---|---|---|
| openrca2-baseline-haiku | 56 | 31 of 33 | 5 of 7 | 20 of 60 | $2.97 | 82 |
| openrca2-baseline-haiku-run2 | 56 | 32 of 33 | 7 of 7 | 17 of 60 | $3.23 | 80 |
| openrca2-lead | 50 | 22 of 33 | 4 of 7 | 24 of 60 | $5.06 | 85 |
| openrca2-lead-survey | 62 | 28 of 33 | 4 of 7 | 30 of 60 | $3.46 | 80 |

openrca2-baseline-haiku against openrca2-baseline-haiku-run2: both right in 50, both wrong in 38, only openrca2-baseline-haiku right in 6, only openrca2-baseline-haiku-run2 right in 6; exact paired test p = 1.000.

openrca2-baseline-haiku against openrca2-lead: both right in 37, both wrong in 31, only openrca2-baseline-haiku right in 19, only openrca2-lead right in 13; exact paired test p = 0.377.

openrca2-baseline-haiku against openrca2-lead-survey: both right in 46, both wrong in 28, only openrca2-baseline-haiku right in 10, only openrca2-lead-survey right in 16; exact paired test p = 0.327.

openrca2-baseline-haiku-run2 against openrca2-lead: both right in 38, both wrong in 32, only openrca2-baseline-haiku-run2 right in 18, only openrca2-lead right in 12; exact paired test p = 0.362.

openrca2-baseline-haiku-run2 against openrca2-lead-survey: both right in 47, both wrong in 29, only openrca2-baseline-haiku-run2 right in 9, only openrca2-lead-survey right in 15; exact paired test p = 0.307.

openrca2-lead against openrca2-lead-survey: both right in 45, both wrong in 33, only openrca2-lead right in 5, only openrca2-lead-survey right in 17; exact paired test p = 0.017.

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

## openrca2-lead: 50 cases without an exact match

A case can show more than one problem.

| Problem | Cases |
|---|---|
| wrong kind | 35 |
| named instead: another service | 10 |
| missed a required fault | 8 |
| named instead: a service on the true graph | 1 |
| named instead: an entry service | 1 |

| Wrong kind: true -> claimed | Times |
|---|---|
| network_delay -> http_slow | 8 |
| network_loss -> database_call_slow | 5 |
| network_corrupt -> database_call_slow | 3 |
| network_partition -> database_call_failed | 2 |
| network_partition -> database_call_slow | 2 |
| network_partition -> dns_lookup_failed | 2 |
| jvm_heap_exhausted -> container_cpu_saturated | 2 |
| network_delay -> database_call_slow | 2 |
| network_loss -> application_method_slow | 1 |
| pod_unavailable -> network_delay | 1 |
| network_partition -> http_slow | 1 |
| wrong_return_value -> application_exception | 1 |
| network_loss -> http_slow | 1 |
| network_corrupt -> application_method_slow | 1 |
| jvm_heap_exhausted -> pod_failure | 1 |
| network_corrupt -> network_loss | 1 |
| pod_failure -> process_cpu_saturated | 1 |

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
