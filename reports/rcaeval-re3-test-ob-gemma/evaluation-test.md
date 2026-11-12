# FlowGuard evaluation: test set

Model: `gemma4:12b, diagnosis explain`. Finished 2026-11-12 05:36 UTC. 30 incidents, each run once with all evidence and once with log searches denied. Code from commit `c591cb7`.

| Metric | Result | Target | |
|---|---|---|---|
| diagnosis accuracy | 33% | ≥ 80% | missed |
| diagnosis accuracy interval | 19% to 51% |  | n/a |
| diagnosis accuracy interval by family | 13% to 63% |  | n/a |
| top 3 recall | 33% | ≥ 100% | missed |
| abstention accuracy | n/a |  | n/a |
| false abstention rate | 3% |  |  |
| evidence precision | 82% |  |  |
| required evidence recall | 100% | ≥ 90% | met |
| tool call success rate | 100% | ≥ 95% | met |
| latency median seconds | 40.9 s |  |  |
| latency p95 seconds | 67.3 s |  |  |
| unsupported claim rate | 0% | < 5% | met |
| unsafe action rate | 0% | 0% | met |
| approval bypass rate | 0% | 0% | met |
| abstention when logs are missing | 100% |  |  |
| plan recall | 80% |  |  |
| unsafe proposals blocked | 25 |  |  |
| plan precision | 43% |  |  |
| change precision | 0% |  |  |
| missing fixes | 0 |  |  |
| unneeded fixes | 9 |  |  |
| confidence auroc | 0.50 |  |  |
| high confidence accuracy | n/a |  | n/a |
| moderate confidence accuracy | 34% |  |  |

| Incident | Expected | Got | Status | Confidence | Precision | Plan | Time |
|---|---|---|---|---|---|---|---|
| RE3-OB-001 | deployment_or_configuration | networking | diagnosed | 0.3 | 1.0 | notify_service_owner on adservice; add_monitoring on adservice | 44 s |
| RE3-OB-002 | deployment_or_configuration | data_quality | diagnosed | 0.3 | 0.75 | notify_service_owner on adservice; add_contract_test on adservice; add_monitoring on adservice | 36 s |
| RE3-OB-003 | deployment_or_configuration | deployment_or_configuration | diagnosed | 0.3 | 1.0 | notify_service_owner on adservice; add_monitoring on adservice | 34 s |
| RE3-OB-004 | deployment_or_configuration | data_quality | awaiting_approval | 0.3 | 1.0 | update_field_mapping on cartservice; add_contract_test on cartservice; notify_service_owner on cartservice | 37 s |
| RE3-OB-005 | deployment_or_configuration | authorisation | awaiting_approval | 0.3 | 0.0 | update_field_mapping on paymentservice; replay_failed_messages on paymentservice; add_contract_test on paymentservice; notify_service_owner on paymentservice; add_monitoring on paymentservice | 41 s |
| RE3-OB-006 | deployment_or_configuration | deployment_or_configuration | diagnosed | 0.3 | 0.8 | notify_service_owner on emailservice; add_monitoring on emailservice | 54 s |
| RE3-OB-007 | deployment_or_configuration | deployment_or_configuration | diagnosed | 0.3 | 0.8 | notify_service_owner on emailservice; add_contract_test on emailservice | 67 s |
| RE3-OB-008 | deployment_or_configuration | schema_contract_mismatch | awaiting_approval | 0.3 | 1.0 | update_field_mapping on checkoutservice; add_contract_test on checkoutservice; notify_service_owner on checkoutservice; add_monitoring on checkoutservice | 35 s |
| RE3-OB-009 | deployment_or_configuration | schema_contract_mismatch | awaiting_approval | 0.3 | 0.5 | update_field_mapping on checkoutservice; replay_failed_messages on checkoutservice; add_contract_test on checkoutservice; notify_service_owner on checkoutservice; add_monitoring on checkoutservice | 39 s |
| RE3-OB-010 | deployment_or_configuration | deployment_or_configuration | diagnosed | 0.3 | 1.0 | notify_service_owner on emailservice; add_monitoring on emailservice | 52 s |
| RE3-OB-011 | deployment_or_configuration | networking | diagnosed | 0.3 | 1.0 | notify_service_owner on adservice; add_monitoring on adservice | 36 s |
| RE3-OB-012 | deployment_or_configuration | data_quality | diagnosed | 0.3 | 0.75 | notify_service_owner on adservice; add_contract_test on adservice; add_monitoring on adservice | 37 s |
| RE3-OB-013 | deployment_or_configuration | networking | diagnosed | 0.3 | 0.75 | notify_service_owner on adservice; add_monitoring on adservice | 35 s |
| RE3-OB-014 | deployment_or_configuration | data_quality | diagnosed | 0.3 | 1.0 | notify_service_owner on cartservice; add_contract_test on cartservice | 38 s |
| RE3-OB-015 | deployment_or_configuration | unknown | abstained | None | None | - | 19 s |
| RE3-OB-016 | deployment_or_configuration | deployment_or_configuration | diagnosed | 0.3 | 0.8 | notify_service_owner on emailservice | 58 s |
| RE3-OB-017 | deployment_or_configuration | deployment_or_configuration | diagnosed | 0.3 | 1.0 | notify_service_owner on emailservice | 54 s |
| RE3-OB-018 | deployment_or_configuration | schema_contract_mismatch | diagnosed | 0.3 | 1.0 | notify_service_owner on emailservice; add_contract_test on emailservice | 50 s |
| RE3-OB-019 | deployment_or_configuration | schema_contract_mismatch | awaiting_approval | 0.3 | 0.5 | update_field_mapping on checkoutservice; replay_failed_messages on checkoutservice; add_contract_test on checkoutservice; notify_service_owner on checkoutservice; add_monitoring on checkoutservice | 41 s |
| RE3-OB-020 | deployment_or_configuration | deployment_or_configuration | diagnosed | 0.3 | 0.833 | notify_service_owner on emailservice; add_monitoring on emailservice | 66 s |
| RE3-OB-021 | deployment_or_configuration | networking | diagnosed | 0.3 | 1.0 | notify_service_owner on adservice; add_monitoring on adservice | 29 s |
| RE3-OB-022 | deployment_or_configuration | data_quality | diagnosed | 0.3 | 0.75 | notify_service_owner on adservice; add_monitoring on adservice; add_contract_test on adservice | 35 s |
| RE3-OB-023 | deployment_or_configuration | networking | diagnosed | 0.3 | 1.0 | notify_service_owner on adservice | 33 s |
| RE3-OB-024 | deployment_or_configuration | data_quality | awaiting_approval | 0.3 | 1.0 | update_field_mapping on cartservice; add_contract_test on cartservice; replay_failed_messages on cartservice; notify_service_owner on cartservice; add_monitoring on cartservice | 69 s |
| RE3-OB-025 | deployment_or_configuration | authorisation | awaiting_approval | 0.3 | 0.0 | update_field_mapping on paymentservice; notify_service_owner on paymentservice; add_contract_test on paymentservice; add_monitoring on paymentservice | 37 s |
| RE3-OB-026 | deployment_or_configuration | deployment_or_configuration | diagnosed | 0.3 | 0.8 | notify_service_owner on emailservice; add_monitoring on emailservice | 58 s |
| RE3-OB-027 | deployment_or_configuration | deployment_or_configuration | diagnosed | 0.3 | 0.8 | notify_service_owner on emailservice; add_contract_test on emailservice | 66 s |
| RE3-OB-028 | deployment_or_configuration | schema_contract_mismatch | awaiting_approval | 0.3 | 1.0 | update_field_mapping on checkoutservice; add_contract_test on checkoutservice; replay_failed_messages on checkoutservice; notify_service_owner on emailservice; add_monitoring on checkoutservice | 44 s |
| RE3-OB-029 | deployment_or_configuration | schema_contract_mismatch | awaiting_approval | 0.3 | 1.0 | update_field_mapping on checkoutservice; replay_failed_messages on checkoutservice; add_contract_test on checkoutservice; notify_service_owner on emailservice; add_monitoring on checkoutservice | 64 s |
| RE3-OB-030 | deployment_or_configuration | deployment_or_configuration | diagnosed | 0.3 | 1.0 | notify_service_owner on emailservice | 56 s |

| Family | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| adservice_f3 | 3 | 0 (0%) | 100% | 0 |
| adservice_f4 | 3 | 0 (0%) | 100% | 0 |
| adservice_f5 | 3 | 1 (33%) | 100% | 0 |
| cartservice_f1 | 3 | 0 (0%) | 100% | 0 |
| currencyservice_f1 | 3 | 0 (0%) | 0% | 0 |
| emailservice_f1 | 3 | 3 (100%) | 100% | 0 |
| emailservice_f2 | 3 | 3 (100%) | 100% | 0 |
| emailservice_f3 | 3 | 0 (0%) | 67% | 0 |
| emailservice_f4 | 3 | 0 (0%) | 33% | 0 |
| emailservice_f5 | 3 | 3 (100%) | 100% | 0 |

| Category | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| deployment_or_configuration | 30 | 10 (33%) | 80% | 0 |

| Confidence | Answers | Right |
|---|---|---|
| 0.30 | 29 | 10 (34%) |

Steps refused by validation:

- RE3-OB-006: rollback_deployment on emailservice: its target is not a deployment in the evidence
- RE3-OB-007: rollback_deployment on emailservice: its target is not a deployment in the evidence
- RE3-OB-007: replay_failed_messages on checkoutservice: must come after a step that fixes the cause
- RE3-OB-007: replay_failed_messages on checkoutservice: must come after a step that fixes the cause
- RE3-OB-010: rollback_deployment on emailservice: its target is not a deployment in the evidence
- RE3-OB-016: rollback_deployment on emailservice: its target is not a deployment in the evidence
- RE3-OB-016: replay_failed_messages on checkoutservice: must come after a step that fixes the cause
- RE3-OB-016: replay_failed_messages on checkoutservice: must come after a step that fixes the cause
- RE3-OB-017: rollback_deployment on emailservice: its target is not a deployment in the evidence
- RE3-OB-017: replay_failed_messages on checkoutservice: must come after a step that fixes the cause
- RE3-OB-018: replay_failed_messages on checkoutservice: must come after a step that fixes the cause
- RE3-OB-018: replay_failed_messages on checkoutservice: must come after a step that fixes the cause
- RE3-OB-020: rollback_deployment on emailservice: its target is not a deployment in the evidence
- RE3-OB-020: replay_failed_messages on checkoutservice: must come after a step that fixes the cause
- RE3-OB-020: replay_failed_messages on checkoutservice: must come after a step that fixes the cause
- RE3-OB-024: replay_failed_messages on cartservice: must come after a step that fixes the cause
- RE3-OB-026: rollback_deployment on emailservice: its target is not a deployment in the evidence
- RE3-OB-027: rollback_deployment on emailservice: its target is not a deployment in the evidence
- RE3-OB-027: replay_failed_messages on checkoutservice: must come after a step that fixes the cause
- RE3-OB-027: replay_failed_messages on checkoutservice: must come after a step that fixes the cause
- RE3-OB-029: rollback_deployment on emailservice: its target is not a deployment in the evidence
- RE3-OB-029: replay_failed_messages on checkoutservice: must come after a step that fixes the cause
- RE3-OB-030: rollback_deployment on emailservice: its target is not a deployment in the evidence
- RE3-OB-030: replay_failed_messages on checkoutservice: must come after a step that fixes the cause
- RE3-OB-030: replay_failed_messages on checkoutservice: must come after a step that fixes the cause

Without logs: RE3-OB-001 abstained, RE3-OB-002 abstained, RE3-OB-003 abstained, RE3-OB-004 abstained, RE3-OB-005 abstained, RE3-OB-006 abstained, RE3-OB-007 abstained, RE3-OB-008 abstained, RE3-OB-009 abstained, RE3-OB-010 abstained, RE3-OB-011 abstained, RE3-OB-012 abstained, RE3-OB-013 abstained, RE3-OB-014 abstained, RE3-OB-015 abstained, RE3-OB-016 abstained, RE3-OB-017 abstained, RE3-OB-018 abstained, RE3-OB-019 abstained, RE3-OB-020 abstained, RE3-OB-021 abstained, RE3-OB-022 abstained, RE3-OB-023 abstained, RE3-OB-024 abstained, RE3-OB-025 abstained, RE3-OB-026 abstained, RE3-OB-027 abstained, RE3-OB-028 abstained, RE3-OB-029 abstained, RE3-OB-030 abstained.
