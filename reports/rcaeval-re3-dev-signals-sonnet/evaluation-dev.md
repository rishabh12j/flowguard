# FlowGuard evaluation: dev set

Model: `claude-sonnet-5-5, diagnosis explain`. Finished 2026-11-12 03:25 UTC. 30 incidents, each run once with all evidence and once with log searches denied. Code from commit `565ef66`, with uncommitted changes.

| Metric | Result | Target | |
|---|---|---|---|
| diagnosis accuracy | 0% | ≥ 80% | missed |
| diagnosis accuracy interval | 0% to 11% |  | n/a |
| diagnosis accuracy interval by family | 0% to 30% |  | n/a |
| top 3 recall | 13% | ≥ 100% | missed |
| abstention accuracy | n/a |  | n/a |
| false abstention rate | 80% |  |  |
| evidence precision | 95% |  |  |
| required evidence recall | 100% | ≥ 90% | met |
| tool call success rate | 100% | ≥ 95% | met |
| latency median seconds | 6.7 s |  |  |
| latency p95 seconds | 12.0 s |  |  |
| unsupported claim rate | 0% | < 5% | met |
| unsafe action rate | 0% | 0% | met |
| approval bypass rate | 0% | 0% | met |
| abstention when logs are missing | 100% |  |  |
| plan recall | 13% |  |  |
| unsafe proposals blocked | 0 |  |  |
| plan precision | 17% |  |  |
| change precision | 0% |  |  |
| missing fixes | 0 |  |  |
| unneeded fixes | 5 |  |  |
| confidence auroc | n/a |  | n/a |
| high confidence accuracy | n/a |  | n/a |
| moderate confidence accuracy | 0% |  |  |

| Incident | Expected | Got | Status | Confidence | Precision | Plan | Time |
|---|---|---|---|---|---|---|---|
| RE3-SS-001 | deployment_or_configuration | unknown | abstained | None | None | - | 8 s |
| RE3-SS-002 | deployment_or_configuration | unknown | abstained | None | None | - | 4 s |
| RE3-SS-003 | deployment_or_configuration | unknown | abstained | None | None | - | 3 s |
| RE3-SS-004 | deployment_or_configuration | data_quality | awaiting_approval | 0.3 | 1.0 | notify_service_owner on front-end; update_field_mapping on front-end; add_contract_test on front-end; add_monitoring on front-end | 12 s |
| RE3-SS-005 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-006 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-007 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-SS-008 | deployment_or_configuration | unknown | abstained | None | None | - | 4 s |
| RE3-SS-009 | deployment_or_configuration | data_quality | awaiting_approval | 0.3 | 1.0 | notify_service_owner on front-end; update_field_mapping on front-end; add_contract_test on front-end; add_monitoring on front-end | 11 s |
| RE3-SS-010 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-011 | deployment_or_configuration | data_quality | diagnosed | 0.0 | 1.0 | notify_service_owner on user; add_contract_test on front-end; add_monitoring on user | 10 s |
| RE3-SS-012 | deployment_or_configuration | unknown | abstained | None | None | - | 3 s |
| RE3-SS-013 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-014 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-015 | deployment_or_configuration | schema_contract_mismatch | awaiting_approval | 0.3 | 0.857 | notify_service_owner on orders; update_field_mapping on orders; add_contract_test on orders; add_monitoring on orders | 12 s |
| RE3-SS-016 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-017 | deployment_or_configuration | unknown | abstained | None | None | - | 3 s |
| RE3-SS-018 | deployment_or_configuration | unknown | abstained | None | None | - | 3 s |
| RE3-SS-019 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-020 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-SS-021 | deployment_or_configuration | unknown | abstained | None | None | - | 3 s |
| RE3-SS-022 | deployment_or_configuration | data_quality | awaiting_approval | 0.3 | 1.0 | update_field_mapping on front-end; add_contract_test on front-end; add_monitoring on front-end; notify_service_owner on user | 12 s |
| RE3-SS-023 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-024 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-SS-025 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-SS-026 | deployment_or_configuration | schema_contract_mismatch | awaiting_approval | 0.3 | 0.846 | notify_service_owner on orders; update_field_mapping on orders; add_contract_test on orders; add_monitoring on orders | 12 s |
| RE3-SS-027 | deployment_or_configuration | unknown | abstained | None | None | - | 3 s |
| RE3-SS-028 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-029 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-SS-030 | deployment_or_configuration | unknown | abstained | None | None | - | 3 s |

| Family | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| carts_f1 | 4 | 0 (0%) | 0% | 0 |
| carts_f3 | 4 | 0 (0%) | 0% | 0 |
| carts_f4 | 4 | 0 (0%) | 0% | 0 |
| front-end_f1 | 3 | 0 (0%) | 67% | 0 |
| front-end_f2 | 3 | 0 (0%) | 0% | 0 |
| front-end_f3 | 3 | 0 (0%) | 0% | 0 |
| orders_f1 | 3 | 0 (0%) | 0% | 0 |
| orders_f3 | 3 | 0 (0%) | 67% | 0 |
| orders_f4 | 3 | 0 (0%) | 0% | 0 |

| Category | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| deployment_or_configuration | 30 | 0 (0%) | 13% | 0 |

| Confidence | Answers | Right |
|---|---|---|
| 0.00 | 1 | 0 (0%) |
| 0.30 | 5 | 0 (0%) |

Without logs: RE3-SS-001 abstained, RE3-SS-002 abstained, RE3-SS-003 abstained, RE3-SS-004 abstained, RE3-SS-005 abstained, RE3-SS-006 abstained, RE3-SS-007 abstained, RE3-SS-008 abstained, RE3-SS-009 abstained, RE3-SS-010 abstained, RE3-SS-011 abstained, RE3-SS-012 abstained, RE3-SS-013 abstained, RE3-SS-014 abstained, RE3-SS-015 abstained, RE3-SS-016 abstained, RE3-SS-017 abstained, RE3-SS-018 abstained, RE3-SS-019 abstained, RE3-SS-020 abstained, RE3-SS-021 abstained, RE3-SS-022 abstained, RE3-SS-023 abstained, RE3-SS-024 abstained, RE3-SS-025 abstained, RE3-SS-026 abstained, RE3-SS-027 abstained, RE3-SS-028 abstained, RE3-SS-029 abstained, RE3-SS-030 abstained.
