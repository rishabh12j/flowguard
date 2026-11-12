# FlowGuard evaluation: dev set

Model: `claude-sonnet-5-5, diagnosis explain`. Finished 2026-11-11 13:08 UTC. 30 incidents, each run once with all evidence and once with log searches denied. Code from commit `565ef66`.

| Metric | Result | Target | |
|---|---|---|---|
| diagnosis accuracy | 10% | ≥ 80% | missed |
| diagnosis accuracy interval | 4% to 26% |  | n/a |
| diagnosis accuracy interval by family | 2% to 42% |  | n/a |
| top 3 recall | 17% | ≥ 100% | missed |
| abstention accuracy | n/a |  | n/a |
| false abstention rate | 73% |  |  |
| evidence precision | 62% |  |  |
| required evidence recall | 100% | ≥ 90% | met |
| tool call success rate | 99% | ≥ 95% | met |
| latency median seconds | 7.2 s |  |  |
| latency p95 seconds | 15.9 s |  |  |
| unsupported claim rate | 0% | < 5% | met |
| unsafe action rate | 0% | 0% | met |
| approval bypass rate | 0% | 0% | met |
| abstention when logs are missing | 100% |  |  |
| plan recall | 17% |  |  |
| unsafe proposals blocked | 6 |  |  |
| plan precision | 21% |  |  |
| change precision | 0% |  |  |
| missing fixes | 0 |  |  |
| unneeded fixes | 1 |  |  |
| confidence auroc | 0.50 |  |  |
| high confidence accuracy | n/a |  | n/a |
| moderate confidence accuracy | 38% |  |  |

| Incident | Expected | Got | Status | Confidence | Precision | Plan | Time |
|---|---|---|---|---|---|---|---|
| RE3-SS-001 | deployment_or_configuration | unknown | abstained | None | None | - | 9 s |
| RE3-SS-002 | deployment_or_configuration | unknown | abstained | None | None | - | 4 s |
| RE3-SS-003 | deployment_or_configuration | networking | diagnosed | 0.3 | 1.0 | notify_service_owner on carts-db; add_monitoring on carts-db; add_monitoring on orders | 12 s |
| RE3-SS-004 | deployment_or_configuration | data_quality | awaiting_approval | 0.3 | 1.0 | notify_service_owner on front-end; update_field_mapping on front-end; add_contract_test on front-end; add_monitoring on front-end | 12 s |
| RE3-SS-005 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-006 | deployment_or_configuration | unknown | abstained | None | None | - | 3 s |
| RE3-SS-007 | deployment_or_configuration | networking | diagnosed | 0.3 | 1.0 | notify_service_owner on carts; add_monitoring on carts | 12 s |
| RE3-SS-008 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-009 | deployment_or_configuration | unknown | abstained | None | None | - | 3 s |
| RE3-SS-010 | deployment_or_configuration | unknown | abstained | None | None | - | 4 s |
| RE3-SS-011 | deployment_or_configuration | deployment_or_configuration | diagnosed | 0.3 | 0.0 | notify_service_owner on queue-master; add_monitoring on queue-master; notify_service_owner on front-end; add_monitoring on front-end | 14 s |
| RE3-SS-012 | deployment_or_configuration | deployment_or_configuration | diagnosed | 0.3 | 0.0 | notify_service_owner on queue-master; add_monitoring on queue-master | 16 s |
| RE3-SS-013 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-014 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-015 | deployment_or_configuration | unknown | abstained | None | None | - | 8 s |
| RE3-SS-016 | deployment_or_configuration | unknown | abstained | None | None | - | 8 s |
| RE3-SS-017 | deployment_or_configuration | unknown | abstained | None | None | - | 3 s |
| RE3-SS-018 | deployment_or_configuration | unknown | abstained | None | None | - | 4 s |
| RE3-SS-019 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-SS-020 | deployment_or_configuration | networking | diagnosed | 0.3 | 1.0 | notify_service_owner on carts; add_monitoring on carts; add_monitoring on orders | 12 s |
| RE3-SS-021 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-SS-022 | deployment_or_configuration | unknown | abstained | None | None | - | 4 s |
| RE3-SS-023 | deployment_or_configuration | unknown | abstained | None | None | - | 3 s |
| RE3-SS-024 | deployment_or_configuration | deployment_or_configuration | diagnosed | 0.3 | 0.0 | notify_service_owner on queue-master; add_monitoring on queue-master | 10 s |
| RE3-SS-025 | deployment_or_configuration | unknown | abstained | None | None | - | 8 s |
| RE3-SS-026 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-027 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-028 | deployment_or_configuration | unknown | abstained | None | None | - | 9 s |
| RE3-SS-029 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-030 | deployment_or_configuration | networking | diagnosed | 0.3 | 1.0 | notify_service_owner on carts-db; notify_service_owner on carts; add_monitoring on carts-db | 18 s |

| Family | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| carts_f1 | 4 | 0 (0%) | 0% | 0 |
| carts_f3 | 4 | 0 (0%) | 50% | 0 |
| carts_f4 | 4 | 0 (0%) | 25% | 0 |
| front-end_f1 | 3 | 0 (0%) | 33% | 0 |
| front-end_f2 | 3 | 0 (0%) | 0% | 0 |
| front-end_f3 | 3 | 3 (100%) | 33% | 0 |
| orders_f1 | 3 | 0 (0%) | 0% | 0 |
| orders_f3 | 3 | 0 (0%) | 0% | 0 |
| orders_f4 | 3 | 0 (0%) | 0% | 0 |

| Category | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| deployment_or_configuration | 30 | 3 (10%) | 17% | 0 |

| Confidence | Answers | Right |
|---|---|---|
| 0.30 | 8 | 3 (38%) |

Steps refused by validation:

- RE3-SS-012: replay_failed_messages on queue-master: must come after a step that fixes the cause
- RE3-SS-012: replay_failed_messages on queue-master: must come after a step that fixes the cause
- RE3-SS-030: replay_failed_messages on carts: must come after a step that fixes the cause
- RE3-SS-030: replay_failed_messages on orders: must come after a step that fixes the cause
- RE3-SS-030: replay_failed_messages on carts: must come after a step that fixes the cause
- RE3-SS-030: replay_failed_messages on orders: must come after a step that fixes the cause

Without logs: RE3-SS-001 abstained, RE3-SS-002 abstained, RE3-SS-003 abstained, RE3-SS-004 abstained, RE3-SS-005 abstained, RE3-SS-006 abstained, RE3-SS-007 abstained, RE3-SS-008 abstained, RE3-SS-009 abstained, RE3-SS-010 abstained, RE3-SS-011 abstained, RE3-SS-012 abstained, RE3-SS-013 abstained, RE3-SS-014 abstained, RE3-SS-015 abstained, RE3-SS-016 abstained, RE3-SS-017 abstained, RE3-SS-018 abstained, RE3-SS-019 abstained, RE3-SS-020 abstained, RE3-SS-021 abstained, RE3-SS-022 abstained, RE3-SS-023 abstained, RE3-SS-024 abstained, RE3-SS-025 abstained, RE3-SS-026 abstained, RE3-SS-027 abstained, RE3-SS-028 abstained, RE3-SS-029 abstained, RE3-SS-030 abstained.
