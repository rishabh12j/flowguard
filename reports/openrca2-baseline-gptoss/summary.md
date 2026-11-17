# Baseline run: ollama:gpt-oss:20b, 10 development cases

| Score | Mean |
|---|---|
| f1 | 0.367 |
| precision | 0.400 |
| recall | 0.350 |
| acc | 0.300 |
| any_hit | 0.600 |
| all_hit | 0.500 |
| type_acc | 0.667 |
| node_f1 | 0.676 |
| edge_f1 | 0.515 |
| path_acc | 0.333 |
| path_acc_service | 0.444 |

| Case | System | Calls | Turns | Prompt tokens | Output tokens | USD | Seconds | acc | f1 | any-hit | Stopped | Notes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| case-036 | hs | 44 | 46 | 497,768 | 6,457 | 0.000 | 945 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-073 | ts | 24 | 26 | 250,776 | 4,830 | 0.000 | 360 | 0 | 0.00 | 1 | the model stopped calling tools |  |
| case-095 | ts | 26 | 28 | 282,750 | 4,595 | 0.000 | 350 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-117 | ts | 42 | 44 | 675,980 | 8,295 | 0.000 | 657 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-155 | otel-demo | 44 | 46 | 627,950 | 8,786 | 0.000 | 672 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-164 | hs | 33 | 35 | 407,910 | 5,818 | 0.000 | 389 | 1 | 1.00 | 1 | the model stopped calling tools | Ollama failed and the request was retried: error parsing tool call: raw='{"reflection":"After analyzing traces, we see that only the frontend service has errors (status 500) and increased latency. The span names indicate calls to search.Search/Nearby, but no child spans for the search service are present. Metrics for the search service show deployment unavailable, container not ready, and restarts, indicating that the search pod is crashing due to a missing executable. This explains the 500 errors and latency in frontend. No other servic |
| case-216 | ts | 42 | 44 | 418,188 | 9,109 | 0.000 | 502 | 0 | 0.00 | 0 | the model stopped calling tools |  |
| case-237 | ts | 37 | 39 | 436,176 | 5,850 | 0.000 | 350 | 1 | 1.00 | 1 | the model stopped calling tools |  |
| case-274 | ts | 53 | 55 | 765,202 | 8,827 | 0.000 | 587 | 0 | 0.00 | 1 | the model stopped calling tools | Ollama failed and the request was retried: error parsing tool call: raw='{"reflection":"We have identified that abnormal metrics show significant increases in request duration across many services, with maximum durations around 60s. Traces reveal that services like ts-travel-plan-service, ts-travel2-service, ts-route-plan-service, ts-seat-service, ts-order-other-service, and ts-security-service all experience 60s latency. Logs for ts-order-other-service and ts-security-service contain HikariPool warnings about failed connection validatio |
| case-352 | hs | 35 | 37 | 249,850 | 6,343 | 0.000 | 400 | 0 | 0.67 | 1 | the model stopped calling tools |  |

Total: $0.00, 4,612,550 prompt tokens, 68,910 output tokens.
