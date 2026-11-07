# FlowGuard evaluation: dev set

Model: `gemma4:12b`. Finished 2026-11-07 10:52 UTC. 110 incidents, each run once with all evidence and once with log searches denied.

| Metric | Result | Target | |
|---|---|---|---|
| diagnosis accuracy | 80% | ≥ 80% | met |
| diagnosis accuracy interval | 71% to 87% |  | n/a |
| top 3 recall | 98% | ≥ 100% | missed |
| abstention accuracy | 100% |  |  |
| false abstention rate | 7% |  |  |
| evidence precision | 100% |  |  |
| required evidence recall | 100% | ≥ 90% | met |
| tool call success rate | 100% | ≥ 95% | met |
| latency median seconds | 47.9 s |  |  |
| latency p95 seconds | 65.5 s |  |  |
| unsupported claim rate | 0% | < 5% | met |
| unsafe action rate | 0% | 0% | met |
| approval bypass rate | 0% | 0% | met |
| abstention when logs are missing | 100% |  |  |
| plan recall | 81% |  |  |
| unsafe proposals blocked | 28 |  |  |
| plan precision | 62% |  |  |
| missing fixes | 0 |  |  |
| unneeded fixes | 0 |  |  |
| confidence auroc | 0.50 |  |  |
| high confidence accuracy | 83% |  |  |
| moderate confidence accuracy | 93% |  |  |

| Incident | Expected | Got | Status | Confidence | Precision | Plan | Time |
|---|---|---|---|---|---|---|---|
| BENCH-0001 | data_quality | data_quality | diagnosed | 0.3 | 1.0 | notify_service_owner on pricing-processor; add_monitoring on pricing-processor | 73 s |
| BENCH-0002 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-ACCOUNTS-00010; replay_failed_messages on accounts-processor; add_contract_test on accounts-gateway; notify_service_owner on accounts-gateway | 43 s |
| BENCH-0003 | timeout | deployment_or_configuration | awaiting_approval | 0.7 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00017; replay_failed_messages on warranty-processor; add_monitoring on warranty-processor; notify_service_owner on warranty-db | 55 s |
| BENCH-0004 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-BILLING-00024; replay_failed_messages on billing-processor; add_contract_test on billing-gateway; notify_service_owner on billing-gateway; add_monitoring on billing-processor | 49 s |
| BENCH-0005 | timeout | deployment_or_configuration | awaiting_approval | 0.05 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00030; add_monitoring on bookings-processor; notify_service_owner on bookings-processor | 49 s |
| BENCH-0006 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-INVOICING-00040; add_monitoring on invoicing-processor; notify_service_owner on invoicing-processor | 43 s |
| BENCH-0007 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00048; replay_failed_messages on payments-gateway; add_contract_test on payments-gateway; notify_service_owner on payments-gateway; add_monitoring on payments-processor | 44 s |
| BENCH-0008 | authorisation | authorisation | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PROCUREMENT-00056; replay_failed_messages on procurement-worker; add_contract_test on procurement-worker; notify_service_owner on procurement-worker | 49 s |
| BENCH-0009 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-PROCUREMENT-00064; replay_failed_messages on procurement-worker; add_monitoring on procurement-worker | 43 s |
| BENCH-0010 | data_quality | schema_contract_mismatch | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00074; replay_failed_messages on returns-processor; add_contract_test on returns-gateway; notify_service_owner on returns-gateway | 57 s |
| BENCH-0011 | authentication | authentication | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-BILLING-00083; replay_failed_messages on billing-worker; notify_service_owner on billing-worker; add_monitoring on billing-worker | 41 s |
| BENCH-0012 | unknown | unknown | abstained | None | None | - | 17 s |
| BENCH-0013 | unknown | unknown | abstained | None | None | - | 19 s |
| BENCH-0014 | timeout | timeout | awaiting_approval | 0.05 | 1.0 | pause_job on claims-processor; notify_service_owner on claims-processor; add_monitoring on claims-processor | 45 s |
| BENCH-0015 | unknown | unknown | abstained | None | None | - | 19 s |
| BENCH-0016 | timeout | unknown | abstained | None | None | - | 26 s |
| BENCH-0017 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00120; replay_failed_messages on warranty-worker; add_monitoring on warranty-worker; notify_service_owner on warranty-worker | 46 s |
| BENCH-0018 | authentication | authentication | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PAYROLL-00128; replay_failed_messages on payroll-worker; notify_service_owner on payroll-worker; add_monitoring on payroll-worker | 45 s |
| BENCH-0019 | rate_limiting | rate_limiting | awaiting_approval | 0.65 | 1.0 | enable_rate_limiting on returns-worker; replay_failed_messages on returns-worker; notify_service_owner on returns-worker; add_monitoring on returns-worker | 40 s |
| BENCH-0020 | authorisation | authorisation | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-ACCOUNTS-00140; replay_failed_messages on accounts-worker; add_contract_test on accounts-worker; notify_service_owner on accounts-worker | 54 s |
| BENCH-0021 | networking | networking | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00149; replay_failed_messages on warranty-processor; add_monitoring on warranty-processor; notify_service_owner on warranty-processor | 43 s |
| BENCH-0022 | rate_limiting | rate_limiting | awaiting_approval | 0.0 | 1.0 | pause_job on settlements-backfill; enable_rate_limiting on settlements-worker; replay_failed_messages on settlements-worker; add_monitoring on settlements-worker | 48 s |
| BENCH-0023 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00165; notify_service_owner on bookings-processor; add_monitoring on bookings-processor | 39 s |
| BENCH-0024 | file_transfer | file_transfer | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00173; notify_service_owner on bookings-exporter; add_monitoring on bookings-exporter | 44 s |
| BENCH-0025 | rate_limiting | rate_limiting | awaiting_approval | 0.9 | 1.0 | pause_job on shipping-backfill; enable_rate_limiting on shipping-worker; replay_failed_messages on shipping-worker; notify_service_owner on shipping-worker; add_monitoring on shipping-worker | 48 s |
| BENCH-0026 | authorisation | authorisation | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00191; replay_failed_messages on loyalty-worker; add_contract_test on loyalty-worker; notify_service_owner on loyalty-worker | 52 s |
| BENCH-0027 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on onboarding-worker; replay_failed_messages on onboarding-worker; add_monitoring on onboarding-worker | 40 s |
| BENCH-0028 | file_transfer | data_quality | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00205; redeliver_file on returns-exporter; add_contract_test on returns-exporter; add_monitoring on returns-exporter; notify_service_owner on returns-exporter | 53 s |
| BENCH-0029 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00214; notify_service_owner on payments-processor; add_contract_test on payments-processor | 37 s |
| BENCH-0030 | queue_or_event_processing | unknown | abstained | None | None | - | 20 s |
| BENCH-0031 | file_transfer | file_transfer | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-PAYROLL-00227; redeliver_file on payroll-exporter; add_contract_test on payroll-exporter; notify_service_owner on payroll-exporter | 45 s |
| BENCH-0032 | timeout | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00236 | 35 s |
| BENCH-0033 | queue_or_event_processing | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00246; replay_failed_messages on returns-worker; add_monitoring on returns-worker | 42 s |
| BENCH-0034 | rate_limiting | rate_limiting | awaiting_approval | 0.65 | 1.0 | pause_job on ledger-backfill; enable_rate_limiting on ledger-worker; replay_failed_messages on ledger-worker; notify_service_owner on ledger-backfill; add_monitoring on ledger-worker | 51 s |
| BENCH-0035 | rate_limiting | rate_limiting | awaiting_approval | 0.8 | 1.0 | enable_rate_limiting on accounts-worker; replay_failed_messages on accounts-worker; add_monitoring on accounts-worker | 36 s |
| BENCH-0036 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on procurement-worker; replay_failed_messages on procurement-worker; add_monitoring on procurement-worker | 36 s |
| BENCH-0037 | rate_limiting | rate_limiting | awaiting_approval | 0.75 | 1.0 | enable_rate_limiting on claims-worker; replay_failed_messages on claims-worker | 34 s |
| BENCH-0038 | timeout | schema_contract_mismatch | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00287; replay_failed_messages on onboarding-processor; notify_service_owner on onboarding-db; add_monitoring on onboarding-processor | 50 s |
| BENCH-0039 | authentication | authentication | awaiting_approval | 0.3 | 1.0 | rotate_credential on settlements-worker; replay_failed_messages on settlements-worker; add_monitoring on settlements-worker | 43 s |
| BENCH-0040 | authorisation | deployment_or_configuration | diagnosed | 0.55 | 1.0 | notify_service_owner on catalogue-worker | 75 s |
| BENCH-0041 | networking | networking | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-INVOICING-00314; replay_failed_messages on invoicing-processor; add_monitoring on invoicing-processor | 48 s |
| BENCH-0042 | data_quality | data_quality | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00321; replay_failed_messages on catalogue-processor; add_contract_test on catalogue-gateway; notify_service_owner on catalogue-gateway; add_monitoring on catalogue-processor | 55 s |
| BENCH-0043 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.35 | 1.0 | update_field_mapping on accounts-gateway; replay_failed_messages on accounts-processor; add_contract_test on accounts-gateway; notify_service_owner on accounts-gateway; add_monitoring on accounts-processor | 58 s |
| BENCH-0044 | unknown | unknown | abstained | None | None | - | 23 s |
| BENCH-0045 | authentication | authentication | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-INVOICING-00340; replay_failed_messages on invoicing-worker; notify_service_owner on invoicing-worker; add_monitoring on invoicing-worker | 62 s |
| BENCH-0046 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-BILLING-00347; notify_service_owner on billing-processor; add_contract_test on billing-processor; add_monitoring on billing-processor | 57 s |
| BENCH-0047 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-SHIPPING-00356; add_monitoring on shipping-worker; notify_service_owner on shipping-worker | 58 s |
| BENCH-0048 | unknown | unknown | abstained | None | None | - | 23 s |
| BENCH-0049 | authorisation | authorisation | diagnosed | 0.35 | 1.0 | notify_service_owner on shipping-worker | 59 s |
| BENCH-0050 | authorisation | authorisation | diagnosed | 0.45 | 1.0 | notify_service_owner on inventory-worker; add_monitoring on inventory-worker | 44 s |
| BENCH-0051 | rate_limiting | rate_limiting | awaiting_approval | 0.65 | 1.0 | enable_rate_limiting on rewards-worker; replay_failed_messages on rewards-worker; notify_service_owner on rewards-worker; add_monitoring on rewards-worker | 54 s |
| BENCH-0052 | file_transfer | file_transfer | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00396; redeliver_file on subscriptions-exporter; add_monitoring on subscriptions-exporter | 48 s |
| BENCH-0053 | authentication | authentication | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00405; replay_failed_messages on subscriptions-worker; notify_service_owner on subscriptions-worker; add_monitoring on subscriptions-worker; add_contract_test on subscriptions-worker | 54 s |
| BENCH-0054 | authorisation | authorisation | diagnosed | 0.75 | 1.0 | notify_service_owner on ledger-worker; add_monitoring on ledger-worker | 77 s |
| BENCH-0055 | rate_limiting | rate_limiting | awaiting_approval | 0.65 | 1.0 | enable_rate_limiting on catalogue-worker; replay_failed_messages on catalogue-worker; notify_service_owner on catalogue-worker | 52 s |
| BENCH-0056 | file_transfer | file_transfer | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-SHIPPING-00429; redeliver_file on shipping-exporter; add_monitoring on shipping-exporter | 60 s |
| BENCH-0057 | deployment_or_configuration | unknown | abstained | None | None | - | 28 s |
| BENCH-0058 | networking | networking | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00446; replay_failed_messages on claims-processor; add_monitoring on claims-processor; notify_service_owner on claims-processor | 57 s |
| BENCH-0059 | authentication | authentication | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-BILLING-00453; replay_failed_messages on billing-worker; notify_service_owner on billing-worker; add_monitoring on billing-worker | 59 s |
| BENCH-0060 | data_quality | data_quality | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00462; replay_failed_messages on catalogue-processor; add_contract_test on catalogue-gateway; notify_service_owner on catalogue-gateway; add_monitoring on catalogue-processor | 56 s |
| BENCH-0061 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-BILLING-00471; add_monitoring on billing-worker; notify_service_owner on billing-worker | 48 s |
| BENCH-0062 | queue_or_event_processing | unknown | abstained | None | None | - | 22 s |
| BENCH-0063 | file_transfer | file_transfer | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00483; redeliver_file on returns-exporter; notify_service_owner on returns-exporter; add_monitoring on returns-exporter | 48 s |
| BENCH-0064 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.7 | 0.75 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00492; replay_failed_messages on subscriptions-processor; add_contract_test on subscriptions-gateway; notify_service_owner on subscriptions-gateway; add_monitoring on subscriptions-processor | 54 s |
| BENCH-0065 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-SHIPPING-00498; replay_failed_messages on shipping-worker; add_monitoring on shipping-worker | 52 s |
| BENCH-0066 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00507; notify_service_owner on subscriptions-processor; add_contract_test on subscriptions-processor | 46 s |
| BENCH-0067 | queue_or_event_processing | unknown | abstained | None | None | - | 22 s |
| BENCH-0068 | unknown | unknown | abstained | None | None | - | 19 s |
| BENCH-0069 | file_transfer | file_transfer | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-PROCUREMENT-00524; redeliver_file on procurement-exporter; notify_service_owner on procurement-exporter; add_monitoring on procurement-exporter | 52 s |
| BENCH-0070 | networking | networking | diagnosed | 0.75 | 1.0 | add_monitoring on rewards-worker | 58 s |
| BENCH-0071 | data_quality | data_quality | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-PRICING-00541; replay_failed_messages on pricing-processor; add_contract_test on pricing-gateway; notify_service_owner on pricing-gateway | 48 s |
| BENCH-0072 | queue_or_event_processing | unknown | abstained | None | None | - | 18 s |
| BENCH-0073 | rate_limiting | rate_limiting | awaiting_approval | 0.0 | 1.0 | enable_rate_limiting on onboarding-worker; replay_failed_messages on onboarding-worker; add_monitoring on onboarding-worker | 47 s |
| BENCH-0074 | data_quality | data_quality | diagnosed | 0.3 | 1.0 | notify_service_owner on payroll-processor; add_monitoring on payroll-processor | 65 s |
| BENCH-0075 | networking | networking | diagnosed | 0.65 | 1.0 | notify_service_owner on returns-worker; add_monitoring on returns-worker | 66 s |
| BENCH-0076 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.55 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00577; replay_failed_messages on claims-processor; add_contract_test on claims-gateway; notify_service_owner on claims-gateway; add_monitoring on claims-processor | 50 s |
| BENCH-0077 | authorisation | deployment_or_configuration | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00586; replay_failed_messages on returns-worker; notify_service_owner on returns-worker; add_contract_test on returns-worker | 56 s |
| BENCH-0078 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00593; add_monitoring on claims-worker; notify_service_owner on claims-worker | 48 s |
| BENCH-0079 | timeout | deployment_or_configuration | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00600; notify_service_owner on catalogue-db; add_monitoring on catalogue-db | 41 s |
| BENCH-0080 | data_quality | queue_or_event_processing | diagnosed | 0.5 | 1.0 | notify_service_owner on catalogue-processor; add_monitoring on catalogue-processor | 64 s |
| BENCH-0081 | file_transfer | data_quality | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00615; redeliver_file on catalogue-exporter; add_contract_test on catalogue-exporter; notify_service_owner on catalogue-exporter; add_monitoring on catalogue-exporter | 56 s |
| BENCH-0082 | timeout | timeout | awaiting_approval | 0.25 | 1.0 | rollback_deployment on DEPLOY-PAYROLL-00622; replay_failed_messages on payroll-processor; add_monitoring on payroll-processor; notify_service_owner on payroll-processor | 57 s |
| BENCH-0083 | networking | networking | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00631; replay_failed_messages on returns-processor; notify_service_owner on returns-processor; add_monitoring on returns-processor | 51 s |
| BENCH-0084 | file_transfer | file_transfer | awaiting_approval | 0.7 | 1.0 | rollback_deployment on DEPLOY-INVOICING-00640; redeliver_file on invoicing-exporter; add_contract_test on invoicing-exporter; notify_service_owner on invoicing-exporter | 48 s |
| BENCH-0085 | data_quality | file_transfer | diagnosed | 0.5 | 1.0 | - | 71 s |
| BENCH-0086 | queue_or_event_processing | unknown | abstained | None | None | - | 24 s |
| BENCH-0087 | networking | networking | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00661; replay_failed_messages on bookings-processor; add_monitoring on bookings-processor; notify_service_owner on bookings-processor | 42 s |
| BENCH-0088 | unknown | unknown | abstained | None | None | - | 18 s |
| BENCH-0089 | file_transfer | file_transfer | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-00674; redeliver_file on settlements-exporter; add_contract_test on settlements-exporter; notify_service_owner on settlements-exporter; add_monitoring on settlements-exporter | 56 s |
| BENCH-0090 | authorisation | authorisation | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PAYROLL-00682; replay_failed_messages on payroll-worker; add_contract_test on payroll-worker; notify_service_owner on payroll-worker | 52 s |
| BENCH-0091 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-PRICING-00687; replay_failed_messages on pricing-processor; add_contract_test on pricing-gateway; notify_service_owner on pricing-gateway; add_monitoring on pricing-processor | 47 s |
| BENCH-0092 | unknown | unknown | abstained | None | None | - | 20 s |
| BENCH-0093 | networking | networking | diagnosed | 0.55 | 1.0 | notify_service_owner on loyalty-worker; add_monitoring on loyalty-worker | 59 s |
| BENCH-0094 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-ACCOUNTS-00706; notify_service_owner on accounts-worker; add_monitoring on accounts-worker | 43 s |
| BENCH-0095 | timeout | timeout | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-BILLING-00713; replay_failed_messages on billing-processor; add_monitoring on billing-processor | 52 s |
| BENCH-0096 | networking | networking | diagnosed | 0.6 | 1.0 | - | 57 s |
| BENCH-0097 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.65 | 1.0 | update_field_mapping on pricing-gateway; replay_failed_messages on pricing-processor; add_contract_test on pricing-gateway; notify_service_owner on pricing-gateway; add_monitoring on pricing-processor | 46 s |
| BENCH-0098 | timeout | timeout | awaiting_approval | 0.15 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00742; replay_failed_messages on rewards-processor; add_monitoring on rewards-processor; notify_service_owner on rewards-processor | 47 s |
| BENCH-0099 | authorisation | authorisation | diagnosed | 0.65 | 1.0 | notify_service_owner on ledger-worker; add_monitoring on ledger-worker | 69 s |
| BENCH-0100 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.55 | 1.0 | rollback_deployment on DEPLOY-LEDGER-00760; replay_failed_messages on ledger-processor; add_contract_test on ledger-gateway; add_monitoring on ledger-processor | 48 s |
| BENCH-0101 | networking | networking | diagnosed | 0.75 | 1.0 | add_monitoring on bookings-worker | 59 s |
| BENCH-0102 | unknown | unknown | abstained | None | None | - | 21 s |
| BENCH-0103 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.55 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00780; replay_failed_messages on warranty-processor; add_contract_test on warranty-gateway; notify_service_owner on warranty-gateway; add_monitoring on warranty-processor | 55 s |
| BENCH-0104 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on payroll-worker; replay_failed_messages on payroll-worker; add_monitoring on payroll-worker | 40 s |
| BENCH-0105 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00795; replay_failed_messages on onboarding-worker; add_monitoring on onboarding-worker; notify_service_owner on onboarding-worker | 53 s |
| BENCH-0106 | authentication | authentication | awaiting_approval | 0.3 | 1.0 | rotate_credential on settlements-worker; replay_failed_messages on settlements-worker; add_monitoring on settlements-worker | 39 s |
| BENCH-0107 | unknown | unknown | abstained | None | None | - | 16 s |
| BENCH-0108 | rate_limiting | rate_limiting | awaiting_approval | 0.0 | 1.0 | enable_rate_limiting on onboarding-worker; replay_failed_messages on onboarding-worker; notify_service_owner on onboarding-worker | 41 s |
| BENCH-0109 | data_quality | data_quality | diagnosed | 0.65 | 1.0 | notify_service_owner on claims-processor | 35 s |
| BENCH-0110 | data_quality | data_quality | awaiting_approval | 0.15 | 1.0 | rollback_deployment on DEPLOY-SHIPPING-00830; replay_failed_messages on shipping-processor; add_contract_test on shipping-gateway; add_monitoring on shipping-processor; notify_service_owner on shipping-gateway | 52 s |

| Family | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| amounts_in_cents | 5 | 4 (80%) | 100% | 0 |
| backfill_burst | 5 | 5 (100%) | 87% | 0 |
| bad_feature_flag | 5 | 5 (100%) | 80% | 0 |
| consumers_scaled_down | 5 | 4 (80%) | 100% | 0 |
| database_name_change | 5 | 5 (100%) | 100% | 0 |
| dropped_index | 5 | 1 (20%) | 80% | 0 |
| duplicates_after_failover | 5 | 0 (0%) | 0% | 0 |
| encoding_change | 5 | 3 (60%) | 100% | 0 |
| expired_client_credential | 5 | 5 (100%) | 100% | 0 |
| intermittent_resets | 5 | 5 (100%) | n/a | 0 |
| missing_setting | 5 | 4 (80%) | 80% | 0 |
| narrowed_scope | 5 | 4 (80%) | 100% | 0 |
| partner_allowlist_change | 5 | 4 (80%) | 80% | 0 |
| pool_shrunk | 5 | 3 (60%) | 70% | 0 |
| provider_outage | 5 | 5 (100%) | 60% | 0 |
| quota_lowered | 5 | 5 (100%) | 100% | 0 |
| renamed_field | 5 | 5 (100%) | 67% | 0 |
| revoked_key_after_switch | 5 | 5 (100%) | 100% | 0 |
| sporadic_nulls | 5 | 5 (100%) | n/a | 0 |
| stale_reference_data | 5 | 3 (60%) | 70% | 0 |
| type_change | 5 | 5 (100%) | 60% | 0 |
| wrong_directory | 5 | 5 (100%) | 90% | 0 |

| Category | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| authentication | 10 | 10 (100%) | 100% | 0 |
| authorisation | 10 | 8 (80%) | 90% | 0 |
| data_quality | 10 | 7 (70%) | 85% | 0 |
| deployment_or_configuration | 10 | 9 (90%) | 80% | 0 |
| file_transfer | 10 | 8 (80%) | 95% | 0 |
| networking | 10 | 10 (100%) | 80% | 0 |
| queue_or_event_processing | 10 | 4 (40%) | 50% | 0 |
| rate_limiting | 10 | 10 (100%) | 93% | 0 |
| schema_contract_mismatch | 10 | 10 (100%) | 63% | 0 |
| timeout | 10 | 4 (40%) | 75% | 0 |
| unknown | 10 | 10 (100%) | n/a | 0 |

| Confidence | Answers | Right |
|---|---|---|
| 0.00 | 5 | 5 (100%) |
| 0.05 | 2 | 1 (50%) |
| 0.10 | 2 | 2 (100%) |
| 0.15 | 2 | 2 (100%) |
| 0.25 | 1 | 1 (100%) |
| 0.30 | 10 | 9 (90%) |
| 0.35 | 2 | 2 (100%) |
| 0.45 | 4 | 4 (100%) |
| 0.50 | 2 | 0 (0%) |
| 0.55 | 5 | 4 (80%) |
| 0.60 | 1 | 1 (100%) |
| 0.65 | 16 | 14 (88%) |
| 0.70 | 3 | 2 (67%) |
| 0.75 | 17 | 14 (82%) |
| 0.80 | 3 | 2 (67%) |
| 0.85 | 14 | 13 (93%) |
| 0.90 | 1 | 1 (100%) |
| 1.00 | 3 | 3 (100%) |

Steps refused by validation:

- BENCH-0001: replay_failed_messages on pricing-processor: must come after a step that fixes the cause
- BENCH-0001: replay_failed_messages on pricing-processor: must come after a step that fixes the cause
- BENCH-0024: redeliver_file on bookings-exporter: must come after a step that fixes the cause
- BENCH-0040: replay_failed_messages on catalogue-worker: must come after a step that fixes the cause
- BENCH-0040: replay_failed_messages on catalogue-worker: must come after a step that fixes the cause
- BENCH-0049: replay_failed_messages on shipping-worker: must come after a step that fixes the cause
- BENCH-0049: replay_failed_messages on shipping-worker: must come after a step that fixes the cause
- BENCH-0054: replay_failed_messages on ledger-worker: must come after a step that fixes the cause
- BENCH-0054: replay_failed_messages on ledger-worker: must come after a step that fixes the cause
- BENCH-0070: replay_failed_messages on rewards-worker: must come after a step that fixes the cause
- BENCH-0070: replay_failed_messages on rewards-worker: must come after a step that fixes the cause
- BENCH-0074: replay_failed_messages on payroll-processor: must come after a step that fixes the cause
- BENCH-0074: replay_failed_messages on payroll-processor: must come after a step that fixes the cause
- BENCH-0075: replay_failed_messages on returns-worker: must come after a step that fixes the cause
- BENCH-0075: replay_failed_messages on returns-worker: must come after a step that fixes the cause
- BENCH-0080: replay_failed_messages on catalogue-processor: must come after a step that fixes the cause
- BENCH-0080: replay_failed_messages on catalogue-processor: must come after a step that fixes the cause
- BENCH-0085: rerun_job on pricing-processor: must come after a step that fixes the cause
- BENCH-0085: replay_failed_messages on pricing-processor: must come after a step that fixes the cause
- BENCH-0085: redeliver_file on pricing-processor: must come after a step that fixes the cause
- BENCH-0093: replay_failed_messages on loyalty-worker: must come after a step that fixes the cause
- BENCH-0093: replay_failed_messages on loyalty-worker: must come after a step that fixes the cause
- BENCH-0096: replay_failed_messages on bookings-worker: must come after a step that fixes the cause
- BENCH-0096: replay_failed_messages on bookings-worker: must come after a step that fixes the cause
- BENCH-0099: replay_failed_messages on ledger-worker: must come after a step that fixes the cause
- BENCH-0099: replay_failed_messages on ledger-worker: must come after a step that fixes the cause
- BENCH-0101: replay_failed_messages on bookings-worker: must come after a step that fixes the cause
- BENCH-0101: replay_failed_messages on bookings-worker: must come after a step that fixes the cause

Without logs: BENCH-0001 abstained, BENCH-0002 abstained, BENCH-0003 abstained, BENCH-0004 abstained, BENCH-0005 abstained, BENCH-0006 abstained, BENCH-0007 abstained, BENCH-0008 abstained, BENCH-0009 abstained, BENCH-0010 abstained, BENCH-0011 abstained, BENCH-0012 abstained, BENCH-0013 abstained, BENCH-0014 abstained, BENCH-0015 abstained, BENCH-0016 abstained, BENCH-0017 abstained, BENCH-0018 abstained, BENCH-0019 abstained, BENCH-0020 abstained, BENCH-0021 abstained, BENCH-0022 abstained, BENCH-0023 abstained, BENCH-0024 abstained, BENCH-0025 abstained, BENCH-0026 abstained, BENCH-0027 abstained, BENCH-0028 abstained, BENCH-0029 abstained, BENCH-0030 abstained, BENCH-0031 abstained, BENCH-0032 abstained, BENCH-0033 abstained, BENCH-0034 abstained, BENCH-0035 abstained, BENCH-0036 abstained, BENCH-0037 abstained, BENCH-0038 abstained, BENCH-0039 abstained, BENCH-0040 abstained, BENCH-0041 abstained, BENCH-0042 abstained, BENCH-0043 abstained, BENCH-0044 abstained, BENCH-0045 abstained, BENCH-0046 abstained, BENCH-0047 abstained, BENCH-0048 abstained, BENCH-0049 abstained, BENCH-0050 abstained, BENCH-0051 abstained, BENCH-0052 abstained, BENCH-0053 abstained, BENCH-0054 abstained, BENCH-0055 abstained, BENCH-0056 abstained, BENCH-0057 abstained, BENCH-0058 abstained, BENCH-0059 abstained, BENCH-0060 abstained, BENCH-0061 abstained, BENCH-0062 abstained, BENCH-0063 abstained, BENCH-0064 abstained, BENCH-0065 abstained, BENCH-0066 abstained, BENCH-0067 abstained, BENCH-0068 abstained, BENCH-0069 abstained, BENCH-0070 abstained, BENCH-0071 abstained, BENCH-0072 abstained, BENCH-0073 abstained, BENCH-0074 abstained, BENCH-0075 abstained, BENCH-0076 abstained, BENCH-0077 abstained, BENCH-0078 abstained, BENCH-0079 abstained, BENCH-0080 abstained, BENCH-0081 abstained, BENCH-0082 abstained, BENCH-0083 abstained, BENCH-0084 abstained, BENCH-0085 abstained, BENCH-0086 abstained, BENCH-0087 abstained, BENCH-0088 abstained, BENCH-0089 abstained, BENCH-0090 abstained, BENCH-0091 abstained, BENCH-0092 abstained, BENCH-0093 abstained, BENCH-0094 abstained, BENCH-0095 abstained, BENCH-0096 abstained, BENCH-0097 abstained, BENCH-0098 abstained, BENCH-0099 abstained, BENCH-0100 abstained, BENCH-0101 abstained, BENCH-0102 abstained, BENCH-0103 abstained, BENCH-0104 abstained, BENCH-0105 abstained, BENCH-0106 abstained, BENCH-0107 abstained, BENCH-0108 abstained, BENCH-0109 abstained, BENCH-0110 abstained.
