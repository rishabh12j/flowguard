# FlowGuard evaluation: dev set

Model: `gemma4:12b, diagnosis explain`. Finished 2026-11-10 11:26 UTC. 50 incidents, each run once with all evidence and once with log searches denied.

| Metric | Result | Target | |
|---|---|---|---|
| diagnosis accuracy | 100% | ≥ 80% | met |
| diagnosis accuracy interval | 91% to 100% |  | n/a |
| diagnosis accuracy interval by family | 68% to 100% |  | n/a |
| top 3 recall | 100% | ≥ 100% | met |
| abstention accuracy | 90% |  |  |
| false abstention rate | 0% |  |  |
| evidence precision | 98% |  |  |
| required evidence recall | 100% | ≥ 90% | met |
| tool call success rate | 100% | ≥ 95% | met |
| latency median seconds | 66.7 s |  |  |
| latency p95 seconds | 96.3 s |  |  |
| unsupported claim rate | 0% | < 5% | met |
| unsafe action rate | 0% | 0% | met |
| approval bypass rate | 0% | 0% | met |
| abstention when logs are missing | 100% |  |  |
| plan recall | 75% |  |  |
| unsafe proposals blocked | 11 |  |  |
| plan precision | 57% |  |  |
| change precision | 76% |  |  |
| missing fixes | 0 |  |  |
| unneeded fixes | 3 |  |  |
| confidence auroc | 0.97 |  |  |
| high confidence accuracy | 100% |  |  |
| moderate confidence accuracy | 88% |  |  |

| Incident | Expected | Got | Status | Confidence | Precision | Plan | Time |
|---|---|---|---|---|---|---|---|
| BENCH-0001 | authorisation | authorisation | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00004; replay_failed_messages on rewards-processor; notify_service_owner on rewards-db; add_monitoring on rewards-processor | 59 s |
| BENCH-0005 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00053; replay_failed_messages on warranty-worker; notify_service_owner on warranty-events; add_monitoring on warranty-worker; add_contract_test on warranty-events | 73 s |
| BENCH-0006 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 1.0 | 0.857 | rollback_deployment on DEPLOY-PAYROLL-00067; rerun_job on payroll-reports; notify_service_owner on payroll-reports; add_monitoring on payroll-reports; add_contract_test on payroll-reports | 69 s |
| BENCH-0017 | rate_limiting | rate_limiting | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00201; enable_rate_limiting on warranty-worker; replay_failed_messages on warranty-worker; add_monitoring on warranty-worker; notify_service_owner on warranty-worker | 62 s |
| BENCH-0022 | authorisation | authorisation | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00259; replay_failed_messages on loyalty-processor; notify_service_owner on loyalty-db; add_monitoring on loyalty-processor | 76 s |
| BENCH-0034 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.9 | 1.0 | update_field_mapping on accounts-worker; replay_failed_messages on accounts-worker; add_contract_test on accounts-worker; notify_service_owner on accounts-worker | 55 s |
| BENCH-0040 | timeout | timeout | diagnosed | 0.45 | 1.0 | notify_service_owner on shipping-reports | 40 s |
| BENCH-0045 | timeout | timeout | diagnosed | 0.45 | 1.0 | notify_service_owner on payroll-reports; add_monitoring on payroll-reports | 68 s |
| BENCH-0048 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00546; add_monitoring on onboarding-reports; notify_service_owner on onboarding-reports | 77 s |
| BENCH-0065 | data_quality | data_quality | diagnosed | 0.65 | 1.0 | notify_service_owner on onboarding-partner-api; add_contract_test on onboarding-partner-api | 96 s |
| BENCH-0074 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.9 | 1.0 | update_field_mapping on claims-worker; replay_failed_messages on claims-worker; add_contract_test on claims-worker; notify_service_owner on claims-worker | 83 s |
| BENCH-0084 | unknown | unknown | abstained | None | None | - | 10 s |
| BENCH-0095 | unknown | unknown | abstained | None | None | - | 15 s |
| BENCH-0096 | rate_limiting | rate_limiting | awaiting_approval | 0.4 | 1.0 | enable_rate_limiting on onboarding-worker; replay_failed_messages on onboarding-worker; add_monitoring on onboarding-worker; notify_service_owner on onboarding-worker | 64 s |
| BENCH-0099 | unknown | unknown | abstained | None | None | - | 11 s |
| BENCH-0107 | rate_limiting | rate_limiting | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-LEDGER-01247; enable_rate_limiting on ledger-worker; replay_failed_messages on ledger-worker; add_contract_test on ledger-worker; notify_service_owner on ledger-worker | 72 s |
| BENCH-0116 | unknown | unknown | abstained | None | None | - | 10 s |
| BENCH-0117 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 1.0 | 0.8 | rollback_deployment on DEPLOY-SETTLEMENTS-01356; rerun_job on settlements-reports; add_monitoring on settlements-reports | 64 s |
| BENCH-0120 | unknown | unknown | abstained | None | None | - | 12 s |
| BENCH-0132 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-01526; rerun_job on loyalty-reports; notify_service_owner on loyalty-reports; add_monitoring on loyalty-reports; add_contract_test on loyalty-reports | 68 s |
| BENCH-0134 | data_quality | data_quality | awaiting_approval | 0.8 | 1.0 | update_field_mapping on warranty-worker; replay_failed_messages on warranty-worker; add_contract_test on warranty-worker; notify_service_owner on warranty-worker; add_monitoring on warranty-worker | 117 s |
| BENCH-0146 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-LEDGER-01686; add_monitoring on ledger-reports; notify_service_owner on ledger-reports | 74 s |
| BENCH-0153 | unknown | unknown | abstained | None | None | - | 14 s |
| BENCH-0161 | authorisation | authorisation | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-REWARDS-01872; replay_failed_messages on rewards-processor; notify_service_owner on rewards-db; add_monitoring on rewards-processor | 75 s |
| BENCH-0166 | timeout | timeout | diagnosed | 0.45 | 1.0 | notify_service_owner on returns-reports; add_monitoring on returns-reports | 91 s |
| BENCH-0169 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-INVOICING-01956; replay_failed_messages on invoicing-worker; notify_service_owner on invoicing-worker; add_monitoring on invoicing-worker | 66 s |
| BENCH-0175 | rate_limiting | rate_limiting | awaiting_approval | 0.55 | 0.667 | enable_rate_limiting on settlements-worker; replay_failed_messages on settlements-worker; notify_service_owner on settlements-worker; add_monitoring on settlements-worker | 71 s |
| BENCH-0178 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.9 | 1.0 | update_field_mapping on returns-worker; replay_failed_messages on returns-worker; add_contract_test on returns-worker; notify_service_owner on returns-worker; add_monitoring on returns-worker | 70 s |
| BENCH-0182 | data_quality | data_quality | diagnosed | 0.8 | 1.0 | notify_service_owner on returns-partner-sftp; add_contract_test on returns-worker | 95 s |
| BENCH-0188 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-02158; notify_service_owner on catalogue-events; add_monitoring on catalogue-worker; add_contract_test on catalogue-events | 73 s |
| BENCH-0199 | authorisation | authorisation | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-REWARDS-02285; replay_failed_messages on rewards-processor; notify_service_owner on rewards-db; add_monitoring on rewards-processor | 62 s |
| BENCH-0223 | unknown | unknown | abstained | None | None | - | 10 s |
| BENCH-0236 | unknown | authentication | diagnosed | 0.4 | 1.0 | notify_service_owner on accounts-worker | 47 s |
| BENCH-0249 | data_quality | data_quality | diagnosed | 0.8 | 1.0 | notify_service_owner on payments-worker; add_contract_test on payments-worker; add_monitoring on payments-worker | 48 s |
| BENCH-0255 | rate_limiting | rate_limiting | awaiting_approval | 0.9 | 0.75 | enable_rate_limiting on onboarding-worker; rollback_deployment on DEPLOY-ONBOARDING-02943; replay_failed_messages on onboarding-worker; notify_service_owner on onboarding-worker; add_monitoring on onboarding-worker | 62 s |
| BENCH-0262 | data_quality | data_quality | awaiting_approval | 0.8 | 1.0 | update_field_mapping on returns-worker; replay_failed_messages on returns-worker; add_contract_test on returns-worker; notify_service_owner on returns-worker | 108 s |
| BENCH-0270 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-03100; notify_service_owner on loyalty-events; add_monitoring on loyalty-worker | 63 s |
| BENCH-0272 | rate_limiting | rate_limiting | awaiting_approval | 0.55 | 1.0 | enable_rate_limiting on returns-worker; notify_service_owner on returns-worker; add_monitoring on returns-worker | 56 s |
| BENCH-0276 | unknown | unknown | abstained | None | None | - | 10 s |
| BENCH-0282 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-LEDGER-03230; replay_failed_messages on ledger-worker; add_contract_test on ledger-worker; notify_service_owner on ledger-processor; add_monitoring on ledger-worker | 72 s |
| BENCH-0283 | rate_limiting | rate_limiting | awaiting_approval | 0.9 | 1.0 | enable_rate_limiting on invoicing-worker; rollback_deployment on DEPLOY-INVOICING-03241; replay_failed_messages on invoicing-worker; notify_service_owner on invoicing-worker; add_monitoring on invoicing-worker | 81 s |
| BENCH-0293 | rate_limiting | rate_limiting | awaiting_approval | 0.55 | 1.0 | enable_rate_limiting on claims-worker; replay_failed_messages on claims-worker; notify_service_owner on claims-worker; add_monitoring on claims-worker | 66 s |
| BENCH-0303 | rate_limiting | rate_limiting | awaiting_approval | 0.4 | 1.0 | enable_rate_limiting on settlements-worker; replay_failed_messages on settlements-worker; add_monitoring on settlements-worker; notify_service_owner on settlements-worker | 68 s |
| BENCH-0306 | unknown | unknown | abstained | None | None | - | 19 s |
| BENCH-0309 | timeout | timeout | diagnosed | 0.45 | 1.0 | notify_service_owner on invoicing-reports | 40 s |
| BENCH-0310 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.9 | 1.0 | update_field_mapping on payroll-worker; replay_failed_messages on payroll-worker; add_contract_test on payroll-worker; notify_service_owner on payroll-worker | 77 s |
| BENCH-0318 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 1.0 | 1.0 | notify_service_owner on rewards-events; rollback_deployment on DEPLOY-REWARDS-03650; add_monitoring on rewards-events | 67 s |
| BENCH-0346 | authorisation | authorisation | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-03940; replay_failed_messages on inventory-processor; notify_service_owner on inventory-db; add_monitoring on inventory-processor | 73 s |
| BENCH-0347 | rate_limiting | rate_limiting | awaiting_approval | 0.55 | 1.0 | enable_rate_limiting on procurement-worker; notify_service_owner on procurement-worker; add_monitoring on procurement-worker | 57 s |
| BENCH-0350 | timeout | timeout | awaiting_approval | 0.45 | 1.0 | update_field_mapping on payments-reports; replay_failed_messages on payments-reports; add_monitoring on payments-reports; notify_service_owner on payments-reports | 89 s |

| Family | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| cron_schedule_typo | 5 | 5 (100%) | 87% | 0 |
| daily_quota_exhausted | 5 | 5 (100%) | 87% | 0 |
| enum_value_added | 5 | 5 (100%) | 40% | 0 |
| feed_migration_zero_prices | 5 | 5 (100%) | 50% | 0 |
| late_report_once | 5 | 5 (100%) | n/a | 0 |
| retry_storm | 5 | 5 (100%) | 87% | 0 |
| role_removed_in_cleanup | 5 | 5 (100%) | 100% | 0 |
| scattered_401s | 5 | 4 (80%) | n/a | 0 |
| table_outgrew_query | 5 | 5 (100%) | 80% | 0 |
| visibility_timeout_shortened | 5 | 5 (100%) | 67% | 0 |

| Category | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| authorisation | 5 | 5 (100%) | 100% | 0 |
| data_quality | 5 | 5 (100%) | 50% | 0 |
| deployment_or_configuration | 5 | 5 (100%) | 87% | 0 |
| queue_or_event_processing | 5 | 5 (100%) | 67% | 0 |
| rate_limiting | 10 | 10 (100%) | 87% | 0 |
| schema_contract_mismatch | 5 | 5 (100%) | 40% | 0 |
| timeout | 5 | 5 (100%) | 80% | 0 |
| unknown | 10 | 9 (90%) | n/a | 0 |

| Confidence | Answers | Right |
|---|---|---|
| 0.40 | 3 | 2 (67%) |
| 0.45 | 5 | 5 (100%) |
| 0.55 | 4 | 4 (100%) |
| 0.65 | 1 | 1 (100%) |
| 0.75 | 1 | 1 (100%) |
| 0.80 | 4 | 4 (100%) |
| 0.85 | 3 | 3 (100%) |
| 0.90 | 12 | 12 (100%) |
| 1.00 | 8 | 8 (100%) |

Steps refused by validation:

- BENCH-0045: rerun_job on payroll-reports: must come after a step that fixes the cause
- BENCH-0048: rerun_job on onboarding-reports: must come after a step that fixes the cause
- BENCH-0065: replay_failed_messages on onboarding-worker: must come after a step that fixes the cause
- BENCH-0065: replay_failed_messages on onboarding-worker: must come after a step that fixes the cause
- BENCH-0134: replay_failed_messages on warranty-worker: must come after a step that fixes the cause
- BENCH-0146: rerun_job on ledger-reports: must come after a step that fixes the cause
- BENCH-0166: replay_failed_messages on returns-reports: must come after a step that fixes the cause
- BENCH-0182: replay_failed_messages on returns-worker: must come after a step that fixes the cause
- BENCH-0182: replay_failed_messages on returns-worker: must come after a step that fixes the cause
- BENCH-0262: replay_failed_messages on returns-worker: must come after a step that fixes the cause
- BENCH-0350: rerun_job on payments-reports: must come after a step that fixes the cause

Without logs: BENCH-0001 abstained, BENCH-0005 abstained, BENCH-0006 abstained, BENCH-0017 abstained, BENCH-0022 abstained, BENCH-0034 abstained, BENCH-0040 abstained, BENCH-0045 abstained, BENCH-0048 abstained, BENCH-0065 abstained, BENCH-0074 abstained, BENCH-0084 abstained, BENCH-0095 abstained, BENCH-0096 abstained, BENCH-0099 abstained, BENCH-0107 abstained, BENCH-0116 abstained, BENCH-0117 abstained, BENCH-0120 abstained, BENCH-0132 abstained, BENCH-0134 abstained, BENCH-0146 abstained, BENCH-0153 abstained, BENCH-0161 abstained, BENCH-0166 abstained, BENCH-0169 abstained, BENCH-0175 abstained, BENCH-0178 abstained, BENCH-0182 abstained, BENCH-0188 abstained, BENCH-0199 abstained, BENCH-0223 abstained, BENCH-0236 abstained, BENCH-0249 abstained, BENCH-0255 abstained, BENCH-0262 abstained, BENCH-0270 abstained, BENCH-0272 abstained, BENCH-0276 abstained, BENCH-0282 abstained, BENCH-0283 abstained, BENCH-0293 abstained, BENCH-0303 abstained, BENCH-0306 abstained, BENCH-0309 abstained, BENCH-0310 abstained, BENCH-0318 abstained, BENCH-0346 abstained, BENCH-0347 abstained, BENCH-0350 abstained.
