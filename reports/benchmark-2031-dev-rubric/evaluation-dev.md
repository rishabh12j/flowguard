# FlowGuard evaluation: dev set

Model: `gemma4:12b`. Finished 2026-11-10 10:34 UTC. 50 incidents, each run once with all evidence and once with log searches denied.

| Metric | Result | Target | |
|---|---|---|---|
| diagnosis accuracy | 57% | ≥ 80% | missed |
| diagnosis accuracy interval | 42% to 72% |  | n/a |
| diagnosis accuracy interval by family | 28% to 83% |  | n/a |
| top 3 recall | 92% | ≥ 100% | missed |
| abstention accuracy | 100% |  |  |
| false abstention rate | 30% |  |  |
| evidence precision | 99% |  |  |
| required evidence recall | 100% | ≥ 90% | met |
| tool call success rate | 100% | ≥ 95% | met |
| latency median seconds | 50.9 s |  |  |
| latency p95 seconds | 73.8 s |  |  |
| unsupported claim rate | 0% | < 5% | met |
| unsafe action rate | 0% | 0% | met |
| approval bypass rate | 0% | 0% | met |
| abstention when logs are missing | 100% |  |  |
| plan recall | 49% |  |  |
| unsafe proposals blocked | 5 |  |  |
| plan precision | 53% |  |  |
| change precision | 74% |  |  |
| missing fixes | 0 |  |  |
| unneeded fixes | 2 |  |  |
| confidence auroc | 0.67 |  |  |
| high confidence accuracy | 94% |  |  |
| moderate confidence accuracy | 60% |  |  |

| Incident | Expected | Got | Status | Confidence | Precision | Plan | Time |
|---|---|---|---|---|---|---|---|
| BENCH-0001 | authorisation | authorisation | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00004; replay_failed_messages on rewards-processor; notify_service_owner on rewards-processor; add_monitoring on rewards-processor | 72 s |
| BENCH-0005 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.25 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00053; replay_failed_messages on warranty-worker; add_monitoring on warranty-events; notify_service_owner on warranty-events | 52 s |
| BENCH-0006 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-PAYROLL-00067; add_monitoring on payroll-reports | 46 s |
| BENCH-0017 | rate_limiting | rate_limiting | awaiting_approval | 0.6 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00201; replay_failed_messages on warranty-worker; notify_service_owner on warranty-worker; add_monitoring on warranty-worker; add_contract_test on warranty-worker | 60 s |
| BENCH-0022 | authorisation | authorisation | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00259; replay_failed_messages on loyalty-processor; notify_service_owner on loyalty-db; add_monitoring on loyalty-processor | 54 s |
| BENCH-0034 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.65 | 1.0 | update_field_mapping on accounts-worker; replay_failed_messages on accounts-worker; add_contract_test on accounts-worker; notify_service_owner on accounts-worker; add_monitoring on accounts-worker | 56 s |
| BENCH-0040 | timeout | unknown | abstained | None | None | - | 19 s |
| BENCH-0045 | timeout | unknown | abstained | None | None | - | 18 s |
| BENCH-0048 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00546; add_monitoring on onboarding-reports | 50 s |
| BENCH-0065 | data_quality | data_quality | diagnosed | 0.25 | 1.0 | notify_service_owner on onboarding-partner-api; add_contract_test on onboarding-partner-api; add_monitoring on onboarding-partner-api | 44 s |
| BENCH-0074 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.9 | 1.0 | update_field_mapping on claims-worker; replay_failed_messages on claims-worker; add_contract_test on claims-worker; notify_service_owner on claims-worker | 64 s |
| BENCH-0084 | unknown | unknown | abstained | None | None | - | 17 s |
| BENCH-0095 | unknown | unknown | abstained | None | None | - | 25 s |
| BENCH-0096 | rate_limiting | unknown | abstained | None | None | - | 22 s |
| BENCH-0099 | unknown | unknown | abstained | None | None | - | 36 s |
| BENCH-0107 | rate_limiting | rate_limiting | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-LEDGER-01247; enable_rate_limiting on ledger-worker; notify_service_owner on ledger-worker; add_contract_test on ledger-worker; add_monitoring on ledger-worker | 58 s |
| BENCH-0116 | unknown | unknown | abstained | None | None | - | 29 s |
| BENCH-0117 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.15 | 0.75 | rollback_deployment on DEPLOY-SETTLEMENTS-01356; rerun_job on settlements-reports; add_monitoring on settlements-reports; notify_service_owner on settlements-reports | 56 s |
| BENCH-0120 | unknown | unknown | abstained | None | None | - | 25 s |
| BENCH-0132 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-01526; notify_service_owner on loyalty-reports; add_monitoring on loyalty-reports | 55 s |
| BENCH-0134 | data_quality | schema_contract_mismatch | awaiting_approval | 0.2 | 1.0 | update_field_mapping on warranty-worker; replay_failed_messages on warranty-worker; notify_service_owner on warranty-worker; add_monitoring on warranty-worker | 54 s |
| BENCH-0146 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-LEDGER-01686; notify_service_owner on ledger-reports; add_monitoring on ledger-reports | 58 s |
| BENCH-0153 | unknown | unknown | abstained | None | None | - | 34 s |
| BENCH-0161 | authorisation | authorisation | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-REWARDS-01872; replay_failed_messages on rewards-processor; notify_service_owner on rewards-processor; add_monitoring on rewards-processor | 62 s |
| BENCH-0166 | timeout | unknown | abstained | None | None | - | 22 s |
| BENCH-0169 | queue_or_event_processing | timeout | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-INVOICING-01956; replay_failed_messages on invoicing-worker; notify_service_owner on invoicing-events; add_monitoring on invoicing-worker | 65 s |
| BENCH-0175 | rate_limiting | rate_limiting | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-02017; enable_rate_limiting on settlements-worker; replay_failed_messages on settlements-worker; add_monitoring on settlements-worker; notify_service_owner on settlements-worker | 68 s |
| BENCH-0178 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.65 | 1.0 | update_field_mapping on returns-worker; replay_failed_messages on returns-worker; add_contract_test on returns-worker; notify_service_owner on returns-worker; add_monitoring on returns-worker | 74 s |
| BENCH-0182 | data_quality | unknown | abstained | None | None | - | 26 s |
| BENCH-0188 | queue_or_event_processing | timeout | awaiting_approval | 0.25 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-02158; notify_service_owner on catalogue-events; add_monitoring on catalogue-worker | 58 s |
| BENCH-0199 | authorisation | authorisation | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-REWARDS-02285; replay_failed_messages on rewards-processor; notify_service_owner on rewards-db; add_monitoring on rewards-processor | 59 s |
| BENCH-0223 | unknown | unknown | abstained | None | None | - | 22 s |
| BENCH-0236 | unknown | unknown | abstained | None | None | - | 36 s |
| BENCH-0249 | data_quality | data_quality | awaiting_approval | 0.0 | 1.0 | update_field_mapping on payments-worker; replay_failed_messages on payments-worker; add_contract_test on payments-worker; notify_service_owner on payments-worker; add_monitoring on payments-worker | 63 s |
| BENCH-0255 | rate_limiting | rate_limiting | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-02943; enable_rate_limiting on onboarding-worker; replay_failed_messages on onboarding-worker; add_monitoring on onboarding-worker; notify_service_owner on onboarding-worker | 54 s |
| BENCH-0262 | data_quality | unknown | abstained | None | None | - | 26 s |
| BENCH-0270 | queue_or_event_processing | timeout | awaiting_approval | 0.25 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-03100; notify_service_owner on loyalty-events; add_monitoring on loyalty-worker | 56 s |
| BENCH-0272 | rate_limiting | unknown | abstained | None | None | - | 26 s |
| BENCH-0276 | unknown | unknown | abstained | None | None | - | 27 s |
| BENCH-0282 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.15 | 1.0 | update_field_mapping on ledger-worker; replay_failed_messages on ledger-worker; add_contract_test on ledger-worker; notify_service_owner on ledger-worker; add_monitoring on ledger-worker | 76 s |
| BENCH-0283 | rate_limiting | rate_limiting | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-INVOICING-03241; enable_rate_limiting on invoicing-worker; replay_failed_messages on invoicing-worker; notify_service_owner on invoicing-worker; add_monitoring on invoicing-worker | 72 s |
| BENCH-0293 | rate_limiting | unknown | abstained | None | None | - | 30 s |
| BENCH-0303 | rate_limiting | unknown | abstained | None | None | - | 31 s |
| BENCH-0306 | unknown | unknown | abstained | None | None | - | 31 s |
| BENCH-0309 | timeout | unknown | abstained | None | None | - | 31 s |
| BENCH-0310 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.35 | 1.0 | update_field_mapping on payroll-worker; replay_failed_messages on payroll-worker; add_contract_test on payroll-worker; notify_service_owner on payroll-worker; add_monitoring on payroll-worker | 88 s |
| BENCH-0318 | queue_or_event_processing | timeout | awaiting_approval | 0.25 | 1.0 | notify_service_owner on rewards-events; rollback_deployment on DEPLOY-REWARDS-03650; add_monitoring on rewards-events; add_contract_test on rewards-events | 67 s |
| BENCH-0346 | authorisation | authorisation | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-03940; replay_failed_messages on inventory-processor; notify_service_owner on inventory-db; add_monitoring on inventory-processor | 62 s |
| BENCH-0347 | rate_limiting | unknown | abstained | None | None | - | 28 s |
| BENCH-0350 | timeout | unknown | abstained | None | None | - | 26 s |

| Family | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| cron_schedule_typo | 5 | 5 (100%) | 73% | 0 |
| daily_quota_exhausted | 5 | 0 (0%) | 0% | 0 |
| enum_value_added | 5 | 5 (100%) | 33% | 0 |
| feed_migration_zero_prices | 5 | 2 (40%) | 40% | 0 |
| late_report_once | 5 | 5 (100%) | n/a | 0 |
| retry_storm | 5 | 5 (100%) | 93% | 0 |
| role_removed_in_cleanup | 5 | 5 (100%) | 100% | 0 |
| scattered_401s | 5 | 5 (100%) | n/a | 0 |
| table_outgrew_query | 5 | 0 (0%) | 0% | 0 |
| visibility_timeout_shortened | 5 | 1 (20%) | 53% | 0 |

| Category | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| authorisation | 5 | 5 (100%) | 100% | 0 |
| data_quality | 5 | 2 (40%) | 40% | 0 |
| deployment_or_configuration | 5 | 5 (100%) | 73% | 0 |
| queue_or_event_processing | 5 | 1 (20%) | 53% | 0 |
| rate_limiting | 10 | 5 (50%) | 47% | 0 |
| schema_contract_mismatch | 5 | 5 (100%) | 33% | 0 |
| timeout | 5 | 0 (0%) | 0% | 0 |
| unknown | 10 | 10 (100%) | n/a | 0 |

| Confidence | Answers | Right |
|---|---|---|
| 0.00 | 1 | 1 (100%) |
| 0.15 | 2 | 2 (100%) |
| 0.20 | 1 | 0 (0%) |
| 0.25 | 5 | 2 (40%) |
| 0.35 | 1 | 1 (100%) |
| 0.60 | 1 | 1 (100%) |
| 0.65 | 2 | 2 (100%) |
| 0.75 | 8 | 8 (100%) |
| 0.85 | 2 | 2 (100%) |
| 0.90 | 4 | 4 (100%) |
| 1.00 | 1 | 0 (0%) |

Steps refused by validation:

- BENCH-0006: rerun_job on payroll-reports: must come after a step that fixes the cause
- BENCH-0048: rerun_job on onboarding-reports: must come after a step that fixes the cause
- BENCH-0132: rerun_job on loyalty-reports: must come after a step that fixes the cause
- BENCH-0134: add_contract_test on warranty-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0146: rerun_job on ledger-reports: must come after a step that fixes the cause

Without logs: BENCH-0001 abstained, BENCH-0005 abstained, BENCH-0006 abstained, BENCH-0017 abstained, BENCH-0022 abstained, BENCH-0034 abstained, BENCH-0040 abstained, BENCH-0045 abstained, BENCH-0048 abstained, BENCH-0065 abstained, BENCH-0074 abstained, BENCH-0084 abstained, BENCH-0095 abstained, BENCH-0096 abstained, BENCH-0099 abstained, BENCH-0107 abstained, BENCH-0116 abstained, BENCH-0117 abstained, BENCH-0120 abstained, BENCH-0132 abstained, BENCH-0134 abstained, BENCH-0146 abstained, BENCH-0153 abstained, BENCH-0161 abstained, BENCH-0166 abstained, BENCH-0169 abstained, BENCH-0175 abstained, BENCH-0178 abstained, BENCH-0182 abstained, BENCH-0188 abstained, BENCH-0199 abstained, BENCH-0223 abstained, BENCH-0236 abstained, BENCH-0249 abstained, BENCH-0255 abstained, BENCH-0262 abstained, BENCH-0270 abstained, BENCH-0272 abstained, BENCH-0276 abstained, BENCH-0282 abstained, BENCH-0283 abstained, BENCH-0293 abstained, BENCH-0303 abstained, BENCH-0306 abstained, BENCH-0309 abstained, BENCH-0310 abstained, BENCH-0318 abstained, BENCH-0346 abstained, BENCH-0347 abstained, BENCH-0350 abstained.
