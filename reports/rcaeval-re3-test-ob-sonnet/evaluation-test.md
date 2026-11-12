# FlowGuard evaluation: test set

Model: `claude-sonnet-5-5, diagnosis explain`. Finished 2026-11-12 06:23 UTC. 30 incidents, each run once with all evidence and once with log searches denied. Code from commit `c591cb7`.

| Metric | Result | Target | |
|---|---|---|---|
| diagnosis accuracy | 0% | ≥ 80% | missed |
| diagnosis accuracy interval | 0% to 11% |  | n/a |
| diagnosis accuracy interval by family | 0% to 28% |  | n/a |
| top 3 recall | 50% | ≥ 100% | missed |
| abstention accuracy | n/a |  | n/a |
| false abstention rate | 90% |  |  |
| evidence precision | 89% |  |  |
| required evidence recall | 100% | ≥ 90% | met |
| tool call success rate | 100% | ≥ 95% | met |
| latency median seconds | 6.7 s |  |  |
| latency p95 seconds | 11.9 s |  |  |
| unsupported claim rate | 0% | < 5% | met |
| unsafe action rate | 0% | 0% | met |
| approval bypass rate | 0% | 0% | met |
| abstention when logs are missing | 100% |  |  |
| plan recall | 3% |  |  |
| unsafe proposals blocked | 0 |  |  |
| plan precision | 8% |  |  |
| change precision | 0% |  |  |
| missing fixes | 0 |  |  |
| unneeded fixes | 1 |  |  |
| confidence auroc | n/a |  | n/a |
| high confidence accuracy | n/a |  | n/a |
| moderate confidence accuracy | 0% |  |  |

| Incident | Expected | Got | Status | Confidence | Precision | Plan | Time |
|---|---|---|---|---|---|---|---|
| RE3-OB-001 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-OB-002 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-OB-003 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-OB-004 | deployment_or_configuration | data_quality | diagnosed | 0.3 | 0.667 | notify_service_owner on cartservice; add_contract_test on cartservice; add_monitoring on cartservice; notify_service_owner on frontend | 12 s |
| RE3-OB-005 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-OB-006 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-OB-007 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-OB-008 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-OB-009 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-OB-010 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-OB-011 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-OB-012 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-OB-013 | deployment_or_configuration | unknown | abstained | None | None | - | 5 s |
| RE3-OB-014 | deployment_or_configuration | data_quality | awaiting_approval | 0.3 | 1.0 | update_field_mapping on frontend; add_contract_test on frontend; add_monitoring on cartservice; notify_service_owner on frontend | 13 s |
| RE3-OB-015 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-OB-016 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-OB-017 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-OB-018 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-OB-019 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-OB-020 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-OB-021 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-OB-022 | deployment_or_configuration | unknown | abstained | None | None | - | 5 s |
| RE3-OB-023 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-OB-024 | deployment_or_configuration | data_quality | diagnosed | 0.3 | 1.0 | add_contract_test on cartservice; notify_service_owner on frontend; add_monitoring on cartservice | 11 s |
| RE3-OB-025 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-OB-026 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |
| RE3-OB-027 | deployment_or_configuration | unknown | abstained | None | None | - | 8 s |
| RE3-OB-028 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-OB-029 | deployment_or_configuration | unknown | abstained | None | None | - | 7 s |
| RE3-OB-030 | deployment_or_configuration | unknown | abstained | None | None | - | 6 s |

| Family | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| adservice_f3 | 3 | 0 (0%) | 0% | 0 |
| adservice_f4 | 3 | 0 (0%) | 0% | 0 |
| adservice_f5 | 3 | 0 (0%) | 0% | 0 |
| cartservice_f1 | 3 | 0 (0%) | 33% | 0 |
| currencyservice_f1 | 3 | 0 (0%) | 0% | 0 |
| emailservice_f1 | 3 | 0 (0%) | 0% | 0 |
| emailservice_f2 | 3 | 0 (0%) | 0% | 0 |
| emailservice_f3 | 3 | 0 (0%) | 0% | 0 |
| emailservice_f4 | 3 | 0 (0%) | 0% | 0 |
| emailservice_f5 | 3 | 0 (0%) | 0% | 0 |

| Category | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| deployment_or_configuration | 30 | 0 (0%) | 3% | 0 |

| Confidence | Answers | Right |
|---|---|---|
| 0.30 | 3 | 0 (0%) |

Without logs: RE3-OB-001 abstained, RE3-OB-002 abstained, RE3-OB-003 abstained, RE3-OB-004 abstained, RE3-OB-005 abstained, RE3-OB-006 abstained, RE3-OB-007 abstained, RE3-OB-008 abstained, RE3-OB-009 abstained, RE3-OB-010 abstained, RE3-OB-011 abstained, RE3-OB-012 abstained, RE3-OB-013 abstained, RE3-OB-014 abstained, RE3-OB-015 abstained, RE3-OB-016 abstained, RE3-OB-017 abstained, RE3-OB-018 abstained, RE3-OB-019 abstained, RE3-OB-020 abstained, RE3-OB-021 abstained, RE3-OB-022 abstained, RE3-OB-023 abstained, RE3-OB-024 abstained, RE3-OB-025 abstained, RE3-OB-026 abstained, RE3-OB-027 abstained, RE3-OB-028 abstained, RE3-OB-029 abstained, RE3-OB-030 abstained.
