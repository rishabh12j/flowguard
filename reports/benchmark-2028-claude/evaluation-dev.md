# FlowGuard evaluation: dev set

Model: `claude-sonnet-5-5`. Finished 2026-11-08 11:45 UTC. 110 incidents, each run once with all evidence and once with log searches denied.

| Metric | Result | Target | |
|---|---|---|---|
| diagnosis accuracy | 76% | ≥ 80% | missed |
| diagnosis accuracy interval | 67% to 83% |  | n/a |
| top 3 recall | 100% | ≥ 100% | met |
| abstention accuracy | 100% |  |  |
| false abstention rate | 20% |  |  |
| evidence precision | 99% |  |  |
| required evidence recall | 100% | ≥ 90% | met |
| tool call success rate | 100% | ≥ 95% | met |
| latency median seconds | 12.5 s |  |  |
| latency p95 seconds | 16.0 s |  |  |
| unsupported claim rate | 0% | < 5% | met |
| unsafe action rate | 0% | 0% | met |
| approval bypass rate | 0% | 0% | met |
| abstention when logs are missing | 100% |  |  |
| plan recall | 76% |  |  |
| unsafe proposals blocked | 28 |  |  |
| plan precision | 58% |  |  |
| missing fixes | 0 |  |  |
| unneeded fixes | 0 |  |  |
| confidence auroc | 0.91 |  |  |
| high confidence accuracy | 100% |  |  |
| moderate confidence accuracy | 84% |  |  |

| Incident | Expected | Got | Status | Confidence | Precision | Plan | Time |
|---|---|---|---|---|---|---|---|
| BENCH-0001 | unknown | unknown | abstained | None | None | - | 8 s |
| BENCH-0002 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00006; notify_service_owner on rewards-worker; add_monitoring on rewards-worker | 10 s |
| BENCH-0003 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.55 | 1.0 | update_field_mapping on invoicing-processor; replay_failed_messages on invoicing-processor; notify_service_owner on invoicing-gateway; add_contract_test on invoicing-gateway; add_monitoring on invoicing-processor | 13 s |
| BENCH-0004 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-PRICING-00022; replay_failed_messages on pricing-processor; notify_service_owner on pricing-gateway; add_contract_test on pricing-gateway; add_monitoring on pricing-processor | 13 s |
| BENCH-0005 | data_quality | data_quality | diagnosed | 0.65 | 1.0 | notify_service_owner on ledger-processor; add_monitoring on ledger-processor | 16 s |
| BENCH-0006 | rate_limiting | unknown | abstained | None | None | - | 7 s |
| BENCH-0007 | file_transfer | file_transfer | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-INVOICING-00044; redeliver_file on invoicing-exporter; add_contract_test on invoicing-exporter; add_monitoring on invoicing-exporter | 13 s |
| BENCH-0008 | file_transfer | file_transfer | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00051; redeliver_file on onboarding-exporter; rerun_job on onboarding-reports; add_contract_test on onboarding-exporter; add_monitoring on onboarding-exporter | 14 s |
| BENCH-0009 | networking | networking | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-PRICING-00059; replay_failed_messages on pricing-processor; notify_service_owner on pricing-processor; add_monitoring on pricing-processor | 11 s |
| BENCH-0010 | networking | networking | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00068; replay_failed_messages on rewards-processor; notify_service_owner on rewards-processor; add_monitoring on rewards-processor | 12 s |
| BENCH-0011 | unknown | unknown | abstained | None | None | - | 8 s |
| BENCH-0012 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on warranty-worker; replay_failed_messages on warranty-worker; notify_service_owner on warranty-reports; add_monitoring on warranty-worker | 11 s |
| BENCH-0013 | timeout | timeout | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00084; notify_service_owner on onboarding-db; add_monitoring on onboarding-processor | 12 s |
| BENCH-0014 | rate_limiting | unknown | abstained | None | None | - | 6 s |
| BENCH-0015 | authorisation | unknown | abstained | None | None | - | 7 s |
| BENCH-0016 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.25 | 1.0 | update_field_mapping on shipping-processor; replay_failed_messages on shipping-processor; add_contract_test on shipping-gateway; notify_service_owner on shipping-gateway | 13 s |
| BENCH-0017 | authentication | authentication | awaiting_approval | 0.75 | 0.857 | rotate_credential on returns-worker; rerun_job on returns-worker; notify_service_owner on returns-reports; add_monitoring on returns-worker | 11 s |
| BENCH-0018 | authorisation | authorisation | diagnosed | 0.65 | 1.0 | notify_service_owner on accounts-worker; add_monitoring on accounts-worker | 16 s |
| BENCH-0019 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on warranty-worker; add_monitoring on warranty-worker | 16 s |
| BENCH-0020 | authorisation | authorisation | awaiting_approval | 0.85 | 1.0 | notify_service_owner on shipping-worker; rollback_deployment on DEPLOY-SHIPPING-00141; replay_failed_messages on shipping-worker; add_contract_test on shipping-worker; add_monitoring on shipping-worker | 14 s |
| BENCH-0021 | data_quality | data_quality | diagnosed | 0.65 | 1.0 | notify_service_owner on pricing-processor; add_monitoring on pricing-processor | 15 s |
| BENCH-0022 | data_quality | data_quality | awaiting_approval | 0.35 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00159; replay_failed_messages on onboarding-processor; notify_service_owner on onboarding-gateway; add_contract_test on onboarding-gateway; add_monitoring on onboarding-processor | 14 s |
| BENCH-0023 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on billing-worker; add_monitoring on billing-worker | 16 s |
| BENCH-0024 | unknown | unknown | abstained | None | None | - | 8 s |
| BENCH-0025 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00178; notify_service_owner on rewards-worker; add_monitoring on rewards-worker | 11 s |
| BENCH-0026 | timeout | timeout | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-BILLING-00186; notify_service_owner on billing-processor; add_contract_test on billing-processor; add_monitoring on billing-processor | 12 s |
| BENCH-0027 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00195; replay_failed_messages on subscriptions-processor; notify_service_owner on subscriptions-processor; add_monitoring on subscriptions-processor | 13 s |
| BENCH-0028 | data_quality | data_quality | diagnosed | 0.6 | 1.0 | notify_service_owner on loyalty-processor; add_monitoring on loyalty-processor | 17 s |
| BENCH-0029 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.4 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00211; notify_service_owner on loyalty-worker; rerun_job on loyalty-reports; add_monitoring on loyalty-worker | 12 s |
| BENCH-0030 | timeout | timeout | awaiting_approval | 0.35 | 1.0 | rollback_deployment on DEPLOY-PAYROLL-00219; replay_failed_messages on payroll-processor; add_monitoring on payroll-processor; add_contract_test on payroll-processor | 13 s |
| BENCH-0031 | file_transfer | file_transfer | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00228; redeliver_file on rewards-exporter; notify_service_owner on rewards-exporter; add_contract_test on rewards-exporter; add_monitoring on rewards-exporter | 13 s |
| BENCH-0032 | data_quality | data_quality | awaiting_approval | 0.4 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00236; replay_failed_messages on subscriptions-processor; notify_service_owner on subscriptions-gateway; add_contract_test on subscriptions-gateway; add_monitoring on subscriptions-reports | 15 s |
| BENCH-0033 | networking | networking | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00246; notify_service_owner on warranty-processor; add_monitoring on warranty-processor | 13 s |
| BENCH-0034 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-PRICING-00256; replay_failed_messages on pricing-processor; notify_service_owner on pricing-processor; add_contract_test on pricing-processor; add_monitoring on pricing-processor | 13 s |
| BENCH-0035 | queue_or_event_processing | unknown | abstained | None | None | - | 8 s |
| BENCH-0036 | queue_or_event_processing | unknown | abstained | None | None | - | 7 s |
| BENCH-0037 | authentication | unknown | abstained | None | None | - | 7 s |
| BENCH-0038 | authentication | authentication | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00285; replay_failed_messages on onboarding-worker; notify_service_owner on onboarding-worker; add_monitoring on onboarding-worker | 12 s |
| BENCH-0039 | authorisation | authorisation | awaiting_approval | 0.55 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00293; replay_failed_messages on catalogue-worker; add_contract_test on catalogue-worker; notify_service_owner on catalogue-worker | 13 s |
| BENCH-0040 | unknown | unknown | abstained | None | None | - | 7 s |
| BENCH-0041 | timeout | timeout | awaiting_approval | 0.55 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00305; notify_service_owner on loyalty-processor; add_monitoring on loyalty-processor | 11 s |
| BENCH-0042 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on warranty-worker; replay_failed_messages on warranty-worker; notify_service_owner on warranty-reports; add_monitoring on warranty-worker | 11 s |
| BENCH-0043 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.75 | 0.857 | rollback_deployment on DEPLOY-CATALOGUE-00320; replay_failed_messages on catalogue-processor; notify_service_owner on catalogue-gateway; add_contract_test on catalogue-gateway; add_monitoring on catalogue-processor | 12 s |
| BENCH-0044 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00328; notify_service_owner on subscriptions-worker; add_contract_test on subscriptions-worker; add_monitoring on subscriptions-worker | 14 s |
| BENCH-0045 | rate_limiting | rate_limiting | awaiting_approval | 0.8 | 1.0 | pause_job on claims-backfill; enable_rate_limiting on claims-worker; replay_failed_messages on claims-worker; rerun_job on claims-backfill; add_monitoring on claims-worker | 12 s |
| BENCH-0046 | networking | networking | awaiting_approval | 0.25 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00346; replay_failed_messages on warranty-processor; notify_service_owner on warranty-reports; add_monitoring on warranty-processor | 12 s |
| BENCH-0047 | authorisation | authorisation | awaiting_approval | 0.4 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00351; replay_failed_messages on catalogue-worker; add_contract_test on catalogue-worker; notify_service_owner on catalogue-worker | 13 s |
| BENCH-0048 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-PROCUREMENT-00359; replay_failed_messages on procurement-processor; notify_service_owner on procurement-gateway; add_contract_test on procurement-gateway; add_monitoring on procurement-processor | 13 s |
| BENCH-0049 | authorisation | deployment_or_configuration | diagnosed | 0.1 | 0.667 | notify_service_owner on payments-worker; add_monitoring on payments-worker | 15 s |
| BENCH-0050 | file_transfer | file_transfer | awaiting_approval | 0.6 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00374; redeliver_file on bookings-exporter; notify_service_owner on bookings-exporter; add_monitoring on bookings-exporter | 12 s |
| BENCH-0051 | timeout | timeout | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-BILLING-00384; notify_service_owner on billing-db; add_monitoring on billing-processor | 13 s |
| BENCH-0052 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00390; notify_service_owner on returns-processor; add_monitoring on returns-processor | 12 s |
| BENCH-0053 | networking | unknown | abstained | None | None | - | 7 s |
| BENCH-0054 | file_transfer | file_transfer | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00406; redeliver_file on payments-exporter; add_contract_test on payments-exporter; add_monitoring on payments-exporter | 13 s |
| BENCH-0055 | rate_limiting | unknown | abstained | None | None | - | 7 s |
| BENCH-0056 | data_quality | data_quality | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00420; replay_failed_messages on loyalty-processor; notify_service_owner on loyalty-reports; add_contract_test on loyalty-gateway; add_monitoring on loyalty-processor | 14 s |
| BENCH-0057 | timeout | timeout | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-LEDGER-00429; notify_service_owner on ledger-db; add_monitoring on ledger-processor | 12 s |
| BENCH-0058 | timeout | unknown | abstained | None | None | - | 7 s |
| BENCH-0059 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.5 | 1.0 | rollback_deployment on DEPLOY-PRICING-00448; add_monitoring on pricing-worker; notify_service_owner on pricing-worker | 12 s |
| BENCH-0060 | schema_contract_mismatch | deployment_or_configuration | awaiting_approval | 0.1 | 0.667 | notify_service_owner on invoicing-gateway; update_field_mapping on invoicing-processor; replay_failed_messages on invoicing-processor; add_contract_test on invoicing-gateway; add_monitoring on invoicing-processor | 13 s |
| BENCH-0061 | schema_contract_mismatch | unknown | abstained | None | None | - | 7 s |
| BENCH-0062 | timeout | timeout | awaiting_approval | 0.35 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00479; notify_service_owner on inventory-processor; replay_failed_messages on inventory-processor; add_monitoring on inventory-processor | 14 s |
| BENCH-0063 | rate_limiting | unknown | abstained | None | None | - | 8 s |
| BENCH-0064 | authorisation | authorisation | awaiting_approval | 0.6 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00495; replay_failed_messages on claims-worker; add_contract_test on claims-worker; notify_service_owner on claims-reports | 14 s |
| BENCH-0065 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-PRICING-00501; replay_failed_messages on pricing-processor; add_contract_test on pricing-processor; add_monitoring on pricing-processor; notify_service_owner on pricing-processor | 11 s |
| BENCH-0066 | rate_limiting | unknown | abstained | None | None | - | 7 s |
| BENCH-0067 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00516; replay_failed_messages on subscriptions-processor; notify_service_owner on subscriptions-processor; add_contract_test on subscriptions-processor; add_monitoring on subscriptions-processor | 13 s |
| BENCH-0068 | file_transfer | file_transfer | awaiting_approval | 0.6 | 1.0 | rollback_deployment on DEPLOY-PRICING-00524; redeliver_file on pricing-exporter; add_contract_test on pricing-exporter; add_monitoring on pricing-exporter | 13 s |
| BENCH-0069 | authentication | authentication | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-00534; rerun_job on settlements-worker; notify_service_owner on settlements-worker; add_monitoring on settlements-worker | 13 s |
| BENCH-0070 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.55 | 1.0 | pause_job on billing-worker; notify_service_owner on billing-worker; add_contract_test on billing-worker; add_monitoring on billing-reports | 13 s |
| BENCH-0071 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00551; notify_service_owner on onboarding-worker; add_monitoring on onboarding-worker | 12 s |
| BENCH-0072 | data_quality | schema_contract_mismatch | awaiting_approval | 0.15 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00558; replay_failed_messages on loyalty-processor; notify_service_owner on loyalty-gateway; add_contract_test on loyalty-gateway; add_monitoring on loyalty-processor | 14 s |
| BENCH-0073 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.7 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00566; notify_service_owner on catalogue-worker; add_monitoring on catalogue-worker | 11 s |
| BENCH-0074 | file_transfer | file_transfer | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00576; redeliver_file on inventory-exporter; notify_service_owner on inventory-exporter; add_contract_test on inventory-exporter; add_monitoring on inventory-exporter | 13 s |
| BENCH-0075 | authentication | unknown | abstained | None | None | - | 7 s |
| BENCH-0076 | unknown | unknown | abstained | None | None | - | 8 s |
| BENCH-0077 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on inventory-worker; add_monitoring on inventory-worker | 16 s |
| BENCH-0078 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-ACCOUNTS-00609; replay_failed_messages on accounts-processor; notify_service_owner on accounts-gateway; add_contract_test on accounts-gateway; add_monitoring on accounts-processor | 14 s |
| BENCH-0079 | unknown | unknown | abstained | None | None | - | 7 s |
| BENCH-0080 | authentication | authentication | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00621; replay_failed_messages on inventory-worker; notify_service_owner on inventory-worker; add_monitoring on inventory-worker | 13 s |
| BENCH-0081 | file_transfer | unknown | abstained | None | None | - | 7 s |
| BENCH-0082 | authentication | authentication | awaiting_approval | 0.1 | 1.0 | notify_service_owner on accounts-worker; rollback_deployment on DEPLOY-ACCOUNTS-00635; replay_failed_messages on accounts-worker; add_monitoring on accounts-worker | 13 s |
| BENCH-0083 | rate_limiting | rate_limiting | awaiting_approval | 0.75 | 1.0 | pause_job on payroll-backfill; enable_rate_limiting on payroll-worker; replay_failed_messages on payroll-worker; add_monitoring on payroll-worker; notify_service_owner on payroll-backfill | 13 s |
| BENCH-0084 | unknown | unknown | abstained | None | None | - | 7 s |
| BENCH-0085 | file_transfer | schema_contract_mismatch | awaiting_approval | 0.35 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00657; redeliver_file on inventory-exporter; add_contract_test on inventory-exporter; add_monitoring on inventory-exporter | 12 s |
| BENCH-0086 | authorisation | unknown | abstained | None | None | - | 7 s |
| BENCH-0087 | rate_limiting | rate_limiting | awaiting_approval | 0.75 | 1.0 | pause_job on payroll-backfill; enable_rate_limiting on payroll-worker; replay_failed_messages on payroll-worker; rerun_job on payroll-backfill; add_monitoring on payroll-worker | 13 s |
| BENCH-0088 | rate_limiting | rate_limiting | awaiting_approval | 0.65 | 1.0 | pause_job on invoicing-backfill; enable_rate_limiting on invoicing-worker; replay_failed_messages on invoicing-worker; rerun_job on invoicing-backfill; add_monitoring on invoicing-worker | 12 s |
| BENCH-0089 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00689; replay_failed_messages on payments-processor; rerun_job on payments-reports; notify_service_owner on payments-gateway; add_contract_test on payments-gateway | 13 s |
| BENCH-0090 | data_quality | data_quality | diagnosed | 0.9 | 1.0 | notify_service_owner on catalogue-processor; add_monitoring on catalogue-processor | 14 s |
| BENCH-0091 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on billing-worker; add_monitoring on billing-worker | 17 s |
| BENCH-0092 | data_quality | unknown | abstained | None | None | - | 7 s |
| BENCH-0093 | authorisation | authorisation | diagnosed | 0.65 | 1.0 | notify_service_owner on catalogue-worker; add_monitoring on catalogue-worker | 17 s |
| BENCH-0094 | timeout | timeout | awaiting_approval | 0.7 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00730; notify_service_owner on payments-db; add_contract_test on payments-db; add_monitoring on payments-processor | 14 s |
| BENCH-0095 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00739; notify_service_owner on payments-worker; add_monitoring on payments-worker | 12 s |
| BENCH-0096 | rate_limiting | unknown | abstained | None | None | - | 8 s |
| BENCH-0097 | timeout | timeout | awaiting_approval | 0.7 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00756; notify_service_owner on subscriptions-db; add_monitoring on subscriptions-processor | 13 s |
| BENCH-0098 | queue_or_event_processing | unknown | abstained | None | None | - | 8 s |
| BENCH-0099 | networking | networking | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00773; notify_service_owner on returns-processor; rerun_job on returns-reports; add_monitoring on returns-processor | 12 s |
| BENCH-0100 | unknown | unknown | abstained | None | None | - | 8 s |
| BENCH-0101 | unknown | unknown | abstained | None | None | - | 7 s |
| BENCH-0102 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.4 | 1.0 | notify_service_owner on bookings-gateway; update_field_mapping on bookings-processor; replay_failed_messages on bookings-processor; add_contract_test on bookings-gateway; add_monitoring on bookings-processor | 13 s |
| BENCH-0103 | file_transfer | unknown | abstained | None | None | - | 8 s |
| BENCH-0104 | queue_or_event_processing | unknown | abstained | None | None | - | 7 s |
| BENCH-0105 | data_quality | data_quality | awaiting_approval | 0.7 | 1.0 | notify_service_owner on settlements-gateway; rollback_deployment on DEPLOY-SETTLEMENTS-00818; replay_failed_messages on settlements-processor; add_contract_test on settlements-gateway; add_monitoring on settlements-processor | 15 s |
| BENCH-0106 | unknown | unknown | abstained | None | None | - | 6 s |
| BENCH-0107 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00831; replay_failed_messages on payments-worker; notify_service_owner on payments-worker; add_monitoring on payments-worker | 12 s |
| BENCH-0108 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-BILLING-00837; notify_service_owner on billing-worker; add_contract_test on billing-worker; add_monitoring on billing-worker | 13 s |
| BENCH-0109 | authentication | authentication | awaiting_approval | 0.55 | 1.0 | rollback_deployment on DEPLOY-PROCUREMENT-00846; replay_failed_messages on procurement-worker; notify_service_owner on procurement-worker; add_monitoring on procurement-worker | 12 s |
| BENCH-0110 | authorisation | authorisation | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00854; replay_failed_messages on loyalty-worker; notify_service_owner on loyalty-worker; add_contract_test on loyalty-worker; add_monitoring on loyalty-worker | 12 s |

| Family | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| amounts_in_cents | 5 | 4 (80%) | 100% | 0 |
| backfill_burst | 5 | 4 (80%) | 80% | 0 |
| bad_feature_flag | 5 | 5 (100%) | 100% | 0 |
| consumers_scaled_down | 5 | 5 (100%) | 100% | 0 |
| database_name_change | 5 | 5 (100%) | 80% | 0 |
| dropped_index | 5 | 5 (100%) | 100% | 0 |
| duplicates_after_failover | 5 | 1 (20%) | 13% | 0 |
| encoding_change | 5 | 3 (60%) | 80% | 0 |
| expired_client_credential | 5 | 3 (60%) | 53% | 0 |
| intermittent_resets | 5 | 5 (100%) | n/a | 0 |
| missing_setting | 5 | 5 (100%) | 100% | 0 |
| narrowed_scope | 5 | 5 (100%) | 100% | 0 |
| partner_allowlist_change | 5 | 2 (40%) | 60% | 0 |
| pool_shrunk | 5 | 4 (80%) | 80% | 0 |
| provider_outage | 5 | 4 (80%) | 80% | 0 |
| quota_lowered | 5 | 0 (0%) | 0% | 0 |
| renamed_field | 5 | 3 (60%) | 73% | 0 |
| revoked_key_after_switch | 5 | 5 (100%) | 90% | 0 |
| sporadic_nulls | 5 | 5 (100%) | n/a | 0 |
| stale_reference_data | 5 | 4 (80%) | 80% | 0 |
| type_change | 5 | 5 (100%) | 73% | 0 |
| wrong_directory | 5 | 4 (80%) | 80% | 0 |

| Category | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| authentication | 10 | 8 (80%) | 72% | 0 |
| authorisation | 10 | 7 (70%) | 80% | 0 |
| data_quality | 10 | 8 (80%) | 90% | 0 |
| deployment_or_configuration | 10 | 10 (100%) | 100% | 0 |
| file_transfer | 10 | 7 (70%) | 80% | 0 |
| networking | 10 | 9 (90%) | 80% | 0 |
| queue_or_event_processing | 10 | 6 (60%) | 57% | 0 |
| rate_limiting | 10 | 4 (40%) | 40% | 0 |
| schema_contract_mismatch | 10 | 8 (80%) | 73% | 0 |
| timeout | 10 | 9 (90%) | 90% | 0 |
| unknown | 10 | 10 (100%) | n/a | 0 |

| Confidence | Answers | Right |
|---|---|---|
| 0.00 | 2 | 2 (100%) |
| 0.10 | 6 | 4 (67%) |
| 0.15 | 1 | 0 (0%) |
| 0.25 | 2 | 2 (100%) |
| 0.30 | 3 | 3 (100%) |
| 0.35 | 4 | 3 (75%) |
| 0.40 | 4 | 4 (100%) |
| 0.45 | 3 | 3 (100%) |
| 0.50 | 1 | 1 (100%) |
| 0.55 | 5 | 5 (100%) |
| 0.60 | 4 | 4 (100%) |
| 0.65 | 14 | 14 (100%) |
| 0.70 | 4 | 4 (100%) |
| 0.75 | 12 | 12 (100%) |
| 0.80 | 10 | 10 (100%) |
| 0.85 | 2 | 2 (100%) |
| 0.90 | 1 | 1 (100%) |
| 1.00 | 2 | 2 (100%) |

Steps refused by validation:

- BENCH-0005: replay_failed_messages on ledger-processor: must come after a step that fixes the cause
- BENCH-0005: replay_failed_messages on ledger-processor: must come after a step that fixes the cause
- BENCH-0018: rerun_job on accounts-worker: must come after a step that fixes the cause
- BENCH-0018: rerun_job on accounts-worker: must come after a step that fixes the cause
- BENCH-0019: replay_failed_messages on warranty-worker: must come after a step that fixes the cause
- BENCH-0019: replay_failed_messages on warranty-worker: must come after a step that fixes the cause
- BENCH-0021: replay_failed_messages on pricing-processor: must come after a step that fixes the cause
- BENCH-0021: replay_failed_messages on pricing-processor: must come after a step that fixes the cause
- BENCH-0023: replay_failed_messages on billing-worker: must come after a step that fixes the cause
- BENCH-0023: rerun_job on billing-reports: must come after a step that fixes the cause
- BENCH-0023: replay_failed_messages on billing-worker: must come after a step that fixes the cause
- BENCH-0023: rerun_job on billing-reports: must come after a step that fixes the cause
- BENCH-0028: replay_failed_messages on loyalty-processor: must come after a step that fixes the cause
- BENCH-0028: rerun_job on loyalty-reports: must come after a step that fixes the cause
- BENCH-0028: replay_failed_messages on loyalty-processor: must come after a step that fixes the cause
- BENCH-0028: rerun_job on loyalty-reports: must come after a step that fixes the cause
- BENCH-0049: replay_failed_messages on payments-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0049: replay_failed_messages on payments-worker: must come after a step that fixes the cause
- BENCH-0077: rerun_job on inventory-worker: must come after a step that fixes the cause
- BENCH-0077: rerun_job on inventory-worker: must come after a step that fixes the cause
- BENCH-0090: replay_failed_messages on catalogue-processor: must come after a step that fixes the cause
- BENCH-0090: replay_failed_messages on catalogue-processor: must come after a step that fixes the cause
- BENCH-0091: rerun_job on billing-worker: must come after a step that fixes the cause
- BENCH-0091: rerun_job on billing-worker: must come after a step that fixes the cause
- BENCH-0093: replay_failed_messages on catalogue-worker: must come after a step that fixes the cause
- BENCH-0093: rerun_job on catalogue-reports: must come after a step that fixes the cause
- BENCH-0093: replay_failed_messages on catalogue-worker: must come after a step that fixes the cause
- BENCH-0093: rerun_job on catalogue-reports: must come after a step that fixes the cause

Without logs: BENCH-0001 abstained, BENCH-0002 abstained, BENCH-0003 abstained, BENCH-0004 abstained, BENCH-0005 abstained, BENCH-0006 abstained, BENCH-0007 abstained, BENCH-0008 abstained, BENCH-0009 abstained, BENCH-0010 abstained, BENCH-0011 abstained, BENCH-0012 abstained, BENCH-0013 abstained, BENCH-0014 abstained, BENCH-0015 abstained, BENCH-0016 abstained, BENCH-0017 abstained, BENCH-0018 abstained, BENCH-0019 abstained, BENCH-0020 abstained, BENCH-0021 abstained, BENCH-0022 abstained, BENCH-0023 abstained, BENCH-0024 abstained, BENCH-0025 abstained, BENCH-0026 abstained, BENCH-0027 abstained, BENCH-0028 abstained, BENCH-0029 abstained, BENCH-0030 abstained, BENCH-0031 abstained, BENCH-0032 abstained, BENCH-0033 abstained, BENCH-0034 abstained, BENCH-0035 abstained, BENCH-0036 abstained, BENCH-0037 abstained, BENCH-0038 abstained, BENCH-0039 abstained, BENCH-0040 abstained, BENCH-0041 abstained, BENCH-0042 abstained, BENCH-0043 abstained, BENCH-0044 abstained, BENCH-0045 abstained, BENCH-0046 abstained, BENCH-0047 abstained, BENCH-0048 abstained, BENCH-0049 abstained, BENCH-0050 abstained, BENCH-0051 abstained, BENCH-0052 abstained, BENCH-0053 abstained, BENCH-0054 abstained, BENCH-0055 abstained, BENCH-0056 abstained, BENCH-0057 abstained, BENCH-0058 abstained, BENCH-0059 abstained, BENCH-0060 abstained, BENCH-0061 abstained, BENCH-0062 abstained, BENCH-0063 abstained, BENCH-0064 abstained, BENCH-0065 abstained, BENCH-0066 abstained, BENCH-0067 abstained, BENCH-0068 abstained, BENCH-0069 abstained, BENCH-0070 abstained, BENCH-0071 abstained, BENCH-0072 abstained, BENCH-0073 abstained, BENCH-0074 abstained, BENCH-0075 abstained, BENCH-0076 abstained, BENCH-0077 abstained, BENCH-0078 abstained, BENCH-0079 abstained, BENCH-0080 abstained, BENCH-0081 abstained, BENCH-0082 abstained, BENCH-0083 abstained, BENCH-0084 abstained, BENCH-0085 abstained, BENCH-0086 abstained, BENCH-0087 abstained, BENCH-0088 abstained, BENCH-0089 abstained, BENCH-0090 abstained, BENCH-0091 abstained, BENCH-0092 abstained, BENCH-0093 abstained, BENCH-0094 abstained, BENCH-0095 abstained, BENCH-0096 abstained, BENCH-0097 abstained, BENCH-0098 abstained, BENCH-0099 abstained, BENCH-0100 abstained, BENCH-0101 abstained, BENCH-0102 abstained, BENCH-0103 abstained, BENCH-0104 abstained, BENCH-0105 abstained, BENCH-0106 abstained, BENCH-0107 abstained, BENCH-0108 abstained, BENCH-0109 abstained, BENCH-0110 abstained.
