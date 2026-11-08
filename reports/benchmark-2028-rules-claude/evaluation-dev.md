# FlowGuard evaluation: dev set

Model: `claude-sonnet-5-5, rule checked, with the check`. Finished 2026-11-08 13:18 UTC. 110 incidents, each run once with all evidence and once with log searches denied.

| Metric | Result | Target | |
|---|---|---|---|
| diagnosis accuracy | 96% | ≥ 80% | met |
| diagnosis accuracy interval | 90% to 98% |  | n/a |
| top 3 recall | 100% | ≥ 100% | met |
| abstention accuracy | 100% |  |  |
| false abstention rate | 0% |  |  |
| evidence precision | 99% |  |  |
| required evidence recall | 100% | ≥ 90% | met |
| tool call success rate | 100% | ≥ 95% | met |
| latency median seconds | 15.5 s |  |  |
| latency p95 seconds | 18.8 s |  |  |
| unsupported claim rate | 0% | < 5% | met |
| unsafe action rate | 0% | 0% | met |
| approval bypass rate | 0% | 0% | met |
| abstention when logs are missing | 100% |  |  |
| plan recall | 96% |  |  |
| unsafe proposals blocked | 31 |  |  |
| plan precision | 61% |  |  |
| missing fixes | 0 |  |  |
| unneeded fixes | 0 |  |  |
| confidence auroc | 0.85 |  |  |
| high confidence accuracy | 98% |  |  |
| moderate confidence accuracy | 92% |  |  |

| Incident | Expected | Got | Status | Confidence | Precision | Plan | Time |
|---|---|---|---|---|---|---|---|
| BENCH-0001 | unknown | unknown | abstained | None | None | - | 12 s |
| BENCH-0002 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00006; rerun_job on rewards-worker; add_contract_test on rewards-worker; add_monitoring on rewards-worker | 15 s |
| BENCH-0003 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.1 | 1.0 | update_field_mapping on invoicing-processor; replay_failed_messages on invoicing-processor; notify_service_owner on invoicing-gateway; add_contract_test on invoicing-gateway; add_monitoring on invoicing-processor | 16 s |
| BENCH-0004 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.55 | 1.0 | update_field_mapping on pricing-gateway; replay_failed_messages on pricing-processor; add_contract_test on pricing-gateway; add_monitoring on pricing-processor | 15 s |
| BENCH-0005 | data_quality | data_quality | diagnosed | 0.85 | 1.0 | notify_service_owner on ledger-processor; add_monitoring on ledger-processor | 18 s |
| BENCH-0006 | rate_limiting | rate_limiting | awaiting_approval | 0.6 | 1.0 | enable_rate_limiting on payments-worker; replay_failed_messages on payments-worker; notify_service_owner on payments-worker; add_monitoring on payments-worker | 15 s |
| BENCH-0007 | file_transfer | file_transfer | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-INVOICING-00044; redeliver_file on invoicing-exporter; add_contract_test on invoicing-exporter; add_monitoring on invoicing-exporter | 16 s |
| BENCH-0008 | file_transfer | file_transfer | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00051; redeliver_file on onboarding-exporter; rerun_job on onboarding-reports; add_contract_test on onboarding-exporter; add_monitoring on onboarding-exporter | 15 s |
| BENCH-0009 | networking | deployment_or_configuration | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-PRICING-00059; replay_failed_messages on pricing-processor; notify_service_owner on pricing-processor; add_monitoring on pricing-processor | 17 s |
| BENCH-0010 | networking | networking | awaiting_approval | 0.2 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00068; replay_failed_messages on rewards-processor; notify_service_owner on rewards-reports; add_monitoring on rewards-processor | 15 s |
| BENCH-0011 | unknown | unknown | abstained | None | None | - | 8 s |
| BENCH-0012 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on warranty-worker; replay_failed_messages on warranty-worker; notify_service_owner on warranty-worker; add_monitoring on warranty-worker | 13 s |
| BENCH-0013 | timeout | timeout | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00084; notify_service_owner on onboarding-db; add_monitoring on onboarding-processor | 16 s |
| BENCH-0014 | rate_limiting | rate_limiting | awaiting_approval | 0.55 | 1.0 | enable_rate_limiting on loyalty-worker; replay_failed_messages on loyalty-worker; add_monitoring on loyalty-worker | 14 s |
| BENCH-0015 | authorisation | authorisation | diagnosed | 0.55 | 1.0 | notify_service_owner on catalogue-worker; add_monitoring on catalogue-worker | 20 s |
| BENCH-0016 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.45 | 1.0 | notify_service_owner on shipping-gateway; update_field_mapping on shipping-processor; replay_failed_messages on shipping-processor; add_contract_test on shipping-gateway; add_monitoring on shipping-processor | 16 s |
| BENCH-0017 | authentication | authentication | awaiting_approval | 0.55 | 1.0 | rotate_credential on returns-worker; replay_failed_messages on returns-worker; notify_service_owner on returns-reports; add_monitoring on returns-worker | 14 s |
| BENCH-0018 | authorisation | authorisation | diagnosed | 0.45 | 1.0 | notify_service_owner on accounts-worker; add_monitoring on accounts-worker | 18 s |
| BENCH-0019 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on warranty-worker; add_monitoring on warranty-worker | 17 s |
| BENCH-0020 | authorisation | authorisation | awaiting_approval | 0.65 | 1.0 | notify_service_owner on shipping-worker; rollback_deployment on DEPLOY-SHIPPING-00141; replay_failed_messages on shipping-worker; add_contract_test on shipping-worker; add_monitoring on shipping-worker | 15 s |
| BENCH-0021 | data_quality | data_quality | diagnosed | 0.6 | 1.0 | notify_service_owner on pricing-processor; add_monitoring on pricing-processor | 18 s |
| BENCH-0022 | data_quality | data_quality | awaiting_approval | 0.35 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00159; replay_failed_messages on onboarding-processor; notify_service_owner on onboarding-gateway; add_contract_test on onboarding-gateway | 15 s |
| BENCH-0023 | networking | networking | diagnosed | 0.55 | 1.0 | notify_service_owner on billing-worker; add_monitoring on billing-worker | 17 s |
| BENCH-0024 | unknown | unknown | abstained | None | None | - | 11 s |
| BENCH-0025 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00178; notify_service_owner on rewards-worker; add_contract_test on rewards-worker; add_monitoring on rewards-worker | 16 s |
| BENCH-0026 | timeout | timeout | awaiting_approval | 0.4 | 1.0 | rollback_deployment on DEPLOY-BILLING-00186; update_field_mapping on billing-processor; add_monitoring on billing-processor; add_contract_test on billing-processor; notify_service_owner on billing-gateway | 16 s |
| BENCH-0027 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00195; replay_failed_messages on subscriptions-processor; notify_service_owner on subscriptions-processor; add_monitoring on subscriptions-processor | 17 s |
| BENCH-0028 | data_quality | data_quality | diagnosed | 0.9 | 1.0 | notify_service_owner on loyalty-processor; add_monitoring on loyalty-processor | 16 s |
| BENCH-0029 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.5 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00211; notify_service_owner on loyalty-worker; add_monitoring on loyalty-worker | 14 s |
| BENCH-0030 | timeout | timeout | awaiting_approval | 0.35 | 1.0 | rollback_deployment on DEPLOY-PAYROLL-00219; notify_service_owner on payroll-processor; add_monitoring on payroll-processor | 16 s |
| BENCH-0031 | file_transfer | file_transfer | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00228; redeliver_file on rewards-exporter; add_contract_test on rewards-exporter; add_monitoring on rewards-exporter | 16 s |
| BENCH-0032 | data_quality | data_quality | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00236; replay_failed_messages on subscriptions-processor; notify_service_owner on subscriptions-gateway; add_contract_test on subscriptions-gateway | 17 s |
| BENCH-0033 | networking | networking | awaiting_approval | 0.65 | 0.9 | rollback_deployment on DEPLOY-WARRANTY-00246; replay_failed_messages on warranty-processor; notify_service_owner on warranty-processor; add_monitoring on warranty-processor | 17 s |
| BENCH-0034 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-PRICING-00256; replay_failed_messages on pricing-processor; add_contract_test on pricing-processor; add_monitoring on pricing-processor | 13 s |
| BENCH-0035 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.65 | 1.0 | pause_job on invoicing-worker; notify_service_owner on invoicing-worker; add_contract_test on invoicing-worker; add_monitoring on invoicing-reports | 15 s |
| BENCH-0036 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.05 | 1.0 | pause_job on billing-worker; notify_service_owner on billing-worker; add_contract_test on billing-worker; add_monitoring on billing-reports | 14 s |
| BENCH-0037 | authentication | authentication | awaiting_approval | 0.55 | 1.0 | rotate_credential on subscriptions-worker; replay_failed_messages on subscriptions-worker; notify_service_owner on subscriptions-reports; add_monitoring on subscriptions-worker | 14 s |
| BENCH-0038 | authentication | authentication | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00285; replay_failed_messages on onboarding-worker; notify_service_owner on onboarding-worker; add_monitoring on onboarding-worker | 16 s |
| BENCH-0039 | authorisation | authorisation | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00293; replay_failed_messages on catalogue-worker; notify_service_owner on catalogue-worker; add_contract_test on catalogue-worker; add_monitoring on catalogue-reports | 16 s |
| BENCH-0040 | unknown | unknown | abstained | None | None | - | 10 s |
| BENCH-0041 | timeout | timeout | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00305; notify_service_owner on loyalty-processor; add_monitoring on loyalty-processor | 16 s |
| BENCH-0042 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on warranty-worker; replay_failed_messages on warranty-worker; add_monitoring on warranty-worker; notify_service_owner on warranty-reports | 12 s |
| BENCH-0043 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.65 | 0.857 | rollback_deployment on DEPLOY-CATALOGUE-00320; replay_failed_messages on catalogue-processor; notify_service_owner on catalogue-gateway; add_contract_test on catalogue-gateway; add_monitoring on catalogue-processor | 16 s |
| BENCH-0044 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 1.0 | 0.875 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00328; replay_failed_messages on subscriptions-worker; notify_service_owner on subscriptions-worker; add_monitoring on subscriptions-worker | 15 s |
| BENCH-0045 | rate_limiting | rate_limiting | awaiting_approval | 0.8 | 1.0 | pause_job on claims-backfill; enable_rate_limiting on claims-worker; replay_failed_messages on claims-worker; rerun_job on claims-backfill; add_monitoring on claims-worker | 14 s |
| BENCH-0046 | networking | networking | awaiting_approval | 0.25 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00346; replay_failed_messages on warranty-processor; add_contract_test on warranty-processor; add_monitoring on warranty-processor | 16 s |
| BENCH-0047 | authorisation | authorisation | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00351; replay_failed_messages on catalogue-worker; notify_service_owner on catalogue-reports; add_contract_test on catalogue-worker | 15 s |
| BENCH-0048 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-PROCUREMENT-00359; replay_failed_messages on procurement-processor; notify_service_owner on procurement-gateway; add_contract_test on procurement-gateway | 16 s |
| BENCH-0049 | authorisation | authorisation | diagnosed | 0.65 | 1.0 | notify_service_owner on payments-worker; add_monitoring on payments-worker | 17 s |
| BENCH-0050 | file_transfer | file_transfer | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00374; redeliver_file on bookings-exporter; add_monitoring on bookings-exporter; notify_service_owner on bookings-exporter | 14 s |
| BENCH-0051 | timeout | timeout | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-BILLING-00384; notify_service_owner on billing-db; replay_failed_messages on billing-processor; add_monitoring on billing-processor | 13 s |
| BENCH-0052 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00390; notify_service_owner on returns-processor; add_contract_test on returns-processor; add_monitoring on returns-processor | 15 s |
| BENCH-0053 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on claims-worker; add_monitoring on claims-worker | 18 s |
| BENCH-0054 | file_transfer | file_transfer | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00406; redeliver_file on payments-exporter; add_contract_test on payments-exporter; add_monitoring on payments-exporter | 16 s |
| BENCH-0055 | rate_limiting | rate_limiting | awaiting_approval | 0.45 | 1.0 | enable_rate_limiting on invoicing-worker; replay_failed_messages on invoicing-worker; add_monitoring on invoicing-worker | 14 s |
| BENCH-0056 | data_quality | data_quality | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00420; replay_failed_messages on loyalty-processor; notify_service_owner on loyalty-gateway; add_contract_test on loyalty-gateway; add_monitoring on loyalty-processor | 17 s |
| BENCH-0057 | timeout | timeout | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-LEDGER-00429; notify_service_owner on ledger-db; add_monitoring on ledger-processor | 16 s |
| BENCH-0058 | timeout | timeout | awaiting_approval | 0.35 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00438; notify_service_owner on claims-processor; add_monitoring on claims-processor | 14 s |
| BENCH-0059 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.4 | 1.0 | rollback_deployment on DEPLOY-PRICING-00448; notify_service_owner on pricing-worker; add_monitoring on pricing-worker | 15 s |
| BENCH-0060 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.55 | 1.0 | update_field_mapping on invoicing-processor; replay_failed_messages on invoicing-processor; notify_service_owner on invoicing-gateway; add_contract_test on invoicing-gateway; add_monitoring on invoicing-processor | 15 s |
| BENCH-0061 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-BILLING-00468; replay_failed_messages on billing-processor; notify_service_owner on billing-gateway; add_contract_test on billing-gateway; add_monitoring on billing-processor | 16 s |
| BENCH-0062 | timeout | timeout | awaiting_approval | 0.15 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00479; notify_service_owner on inventory-processor; add_monitoring on inventory-processor | 15 s |
| BENCH-0063 | rate_limiting | rate_limiting | awaiting_approval | 0.65 | 1.0 | pause_job on onboarding-backfill; enable_rate_limiting on onboarding-worker; replay_failed_messages on onboarding-worker; add_monitoring on onboarding-worker | 16 s |
| BENCH-0064 | authorisation | authorisation | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00495; replay_failed_messages on claims-worker; add_contract_test on claims-worker; notify_service_owner on claims-worker | 16 s |
| BENCH-0065 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-PRICING-00501; notify_service_owner on pricing-processor; add_contract_test on pricing-processor; add_monitoring on pricing-processor | 13 s |
| BENCH-0066 | rate_limiting | rate_limiting | awaiting_approval | 0.45 | 0.857 | pause_job on payroll-worker; enable_rate_limiting on payroll-worker; replay_failed_messages on payroll-worker; add_monitoring on payroll-worker | 15 s |
| BENCH-0067 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00516; replay_failed_messages on subscriptions-processor; add_contract_test on subscriptions-processor; add_monitoring on subscriptions-processor | 14 s |
| BENCH-0068 | file_transfer | file_transfer | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PRICING-00524; redeliver_file on pricing-exporter; add_contract_test on pricing-exporter; add_monitoring on pricing-exporter | 21 s |
| BENCH-0069 | authentication | authentication | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-00534; replay_failed_messages on settlements-worker; notify_service_owner on settlements-worker; add_monitoring on settlements-worker | 19 s |
| BENCH-0070 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.15 | 1.0 | pause_job on billing-worker; notify_service_owner on billing-worker; add_contract_test on billing-worker; add_monitoring on billing-reports | 31 s |
| BENCH-0071 | queue_or_event_processing | deployment_or_configuration | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00551; notify_service_owner on onboarding-worker; add_monitoring on onboarding-worker | 26 s |
| BENCH-0072 | data_quality | data_quality | awaiting_approval | 0.7 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00558; replay_failed_messages on loyalty-processor; notify_service_owner on loyalty-gateway; add_contract_test on loyalty-gateway; add_monitoring on loyalty-processor | 28 s |
| BENCH-0073 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00566; notify_service_owner on catalogue-worker; add_monitoring on catalogue-worker | 15 s |
| BENCH-0074 | file_transfer | file_transfer | awaiting_approval | 0.95 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00576; redeliver_file on inventory-exporter; add_monitoring on inventory-exporter | 15 s |
| BENCH-0075 | authentication | authentication | awaiting_approval | 0.55 | 0.875 | rotate_credential on procurement-worker; replay_failed_messages on procurement-worker; notify_service_owner on procurement-worker; add_monitoring on procurement-worker | 11 s |
| BENCH-0076 | unknown | unknown | abstained | None | None | - | 10 s |
| BENCH-0077 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on inventory-worker; add_monitoring on inventory-worker | 17 s |
| BENCH-0078 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-ACCOUNTS-00609; replay_failed_messages on accounts-processor; notify_service_owner on accounts-gateway; add_contract_test on accounts-gateway; add_monitoring on accounts-processor | 16 s |
| BENCH-0079 | unknown | unknown | abstained | None | None | - | 11 s |
| BENCH-0080 | authentication | authentication | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00621; replay_failed_messages on inventory-worker; notify_service_owner on inventory-worker; add_contract_test on inventory-worker; add_monitoring on inventory-worker | 16 s |
| BENCH-0081 | file_transfer | file_transfer | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-BILLING-00628; redeliver_file on billing-exporter; notify_service_owner on billing-reports; add_contract_test on billing-exporter; add_monitoring on billing-exporter | 16 s |
| BENCH-0082 | authentication | authentication | awaiting_approval | 0.55 | 1.0 | rollback_deployment on DEPLOY-ACCOUNTS-00635; replay_failed_messages on accounts-worker; notify_service_owner on accounts-worker; add_monitoring on accounts-worker | 15 s |
| BENCH-0083 | rate_limiting | rate_limiting | awaiting_approval | 0.75 | 1.0 | pause_job on payroll-backfill; enable_rate_limiting on payroll-worker; replay_failed_messages on payroll-worker; add_monitoring on payroll-worker; notify_service_owner on payroll-backfill | 16 s |
| BENCH-0084 | unknown | unknown | abstained | None | None | - | 10 s |
| BENCH-0085 | file_transfer | file_transfer | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00657; redeliver_file on inventory-exporter; notify_service_owner on inventory-exporter; add_contract_test on inventory-exporter; add_monitoring on inventory-exporter | 15 s |
| BENCH-0086 | authorisation | authorisation | diagnosed | 0.45 | 1.0 | notify_service_owner on ledger-worker; add_monitoring on ledger-worker | 17 s |
| BENCH-0087 | rate_limiting | rate_limiting | awaiting_approval | 0.55 | 1.0 | pause_job on payroll-backfill; enable_rate_limiting on payroll-worker; replay_failed_messages on payroll-worker; add_monitoring on payroll-worker; notify_service_owner on payroll-backfill | 14 s |
| BENCH-0088 | rate_limiting | rate_limiting | awaiting_approval | 0.45 | 1.0 | pause_job on invoicing-backfill; enable_rate_limiting on invoicing-worker; replay_failed_messages on invoicing-worker; rerun_job on invoicing-backfill; add_monitoring on invoicing-worker | 15 s |
| BENCH-0089 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00689; replay_failed_messages on payments-processor; notify_service_owner on payments-gateway; add_contract_test on payments-gateway; add_monitoring on payments-processor | 15 s |
| BENCH-0090 | data_quality | data_quality | diagnosed | 0.55 | 1.0 | notify_service_owner on catalogue-processor; add_monitoring on catalogue-processor | 16 s |
| BENCH-0091 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on billing-worker; add_monitoring on billing-worker | 19 s |
| BENCH-0092 | data_quality | data_quality | diagnosed | 0.35 | 1.0 | notify_service_owner on claims-processor; add_monitoring on claims-processor | 18 s |
| BENCH-0093 | authorisation | authorisation | diagnosed | 0.65 | 1.0 | notify_service_owner on catalogue-worker; add_monitoring on catalogue-worker | 19 s |
| BENCH-0094 | timeout | timeout | awaiting_approval | 0.7 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00730; notify_service_owner on payments-db; add_monitoring on payments-processor | 15 s |
| BENCH-0095 | queue_or_event_processing | deployment_or_configuration | awaiting_approval | 0.55 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00739; notify_service_owner on payments-worker; add_monitoring on payments-worker | 16 s |
| BENCH-0096 | rate_limiting | rate_limiting | awaiting_approval | 0.6 | 1.0 | enable_rate_limiting on accounts-worker; replay_failed_messages on accounts-worker; notify_service_owner on accounts-worker; add_monitoring on accounts-worker | 14 s |
| BENCH-0097 | timeout | timeout | awaiting_approval | 0.7 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00756; notify_service_owner on subscriptions-db; add_monitoring on subscriptions-processor | 15 s |
| BENCH-0098 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.35 | 1.0 | pause_job on inventory-worker; notify_service_owner on inventory-worker; add_monitoring on inventory-reports | 15 s |
| BENCH-0099 | networking | networking | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00773; replay_failed_messages on returns-processor; notify_service_owner on returns-processor; add_monitoring on returns-processor | 16 s |
| BENCH-0100 | unknown | unknown | abstained | None | None | - | 10 s |
| BENCH-0101 | unknown | unknown | abstained | None | None | - | 10 s |
| BENCH-0102 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.6 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00792; replay_failed_messages on bookings-processor; notify_service_owner on bookings-gateway; add_contract_test on bookings-gateway; add_monitoring on bookings-processor | 16 s |
| BENCH-0103 | file_transfer | schema_contract_mismatch | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-BILLING-00800; redeliver_file on billing-exporter; notify_service_owner on billing-exporter; add_contract_test on billing-exporter; add_monitoring on billing-exporter | 19 s |
| BENCH-0104 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.05 | 1.0 | pause_job on bookings-worker; notify_service_owner on bookings-worker; add_contract_test on bookings-worker; add_monitoring on bookings-reports | 15 s |
| BENCH-0105 | data_quality | data_quality | awaiting_approval | 0.7 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-00818; replay_failed_messages on settlements-processor; notify_service_owner on settlements-gateway; add_contract_test on settlements-gateway; add_monitoring on settlements-processor | 16 s |
| BENCH-0106 | unknown | unknown | abstained | None | None | - | 10 s |
| BENCH-0107 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 0.833 | rollback_deployment on DEPLOY-PAYMENTS-00831; rerun_job on payments-worker; notify_service_owner on payments-worker; add_monitoring on payments-worker | 14 s |
| BENCH-0108 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-BILLING-00837; notify_service_owner on billing-worker; add_contract_test on billing-worker; add_monitoring on billing-worker | 15 s |
| BENCH-0109 | authentication | authentication | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-PROCUREMENT-00846; replay_failed_messages on procurement-worker; notify_service_owner on procurement-worker; add_monitoring on procurement-worker | 16 s |
| BENCH-0110 | authorisation | authorisation | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00854; replay_failed_messages on loyalty-worker; notify_service_owner on loyalty-worker; add_contract_test on loyalty-worker; add_monitoring on loyalty-worker | 16 s |

| Family | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| amounts_in_cents | 5 | 5 (100%) | 100% | 0 |
| backfill_burst | 5 | 5 (100%) | 100% | 0 |
| bad_feature_flag | 5 | 5 (100%) | 100% | 0 |
| consumers_scaled_down | 5 | 3 (60%) | 100% | 0 |
| database_name_change | 5 | 4 (80%) | 100% | 0 |
| dropped_index | 5 | 5 (100%) | 100% | 0 |
| duplicates_after_failover | 5 | 5 (100%) | 67% | 0 |
| encoding_change | 5 | 4 (80%) | 100% | 0 |
| expired_client_credential | 5 | 5 (100%) | 100% | 0 |
| intermittent_resets | 5 | 5 (100%) | n/a | 0 |
| missing_setting | 5 | 5 (100%) | 100% | 0 |
| narrowed_scope | 5 | 5 (100%) | 100% | 0 |
| partner_allowlist_change | 5 | 5 (100%) | 100% | 0 |
| pool_shrunk | 5 | 5 (100%) | 100% | 0 |
| provider_outage | 5 | 5 (100%) | 100% | 0 |
| quota_lowered | 5 | 5 (100%) | 100% | 0 |
| renamed_field | 5 | 5 (100%) | 87% | 0 |
| revoked_key_after_switch | 5 | 5 (100%) | 100% | 0 |
| sporadic_nulls | 5 | 5 (100%) | n/a | 0 |
| stale_reference_data | 5 | 5 (100%) | 100% | 0 |
| type_change | 5 | 5 (100%) | 67% | 0 |
| wrong_directory | 5 | 5 (100%) | 100% | 0 |

| Category | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| authentication | 10 | 10 (100%) | 100% | 0 |
| authorisation | 10 | 10 (100%) | 100% | 0 |
| data_quality | 10 | 10 (100%) | 100% | 0 |
| deployment_or_configuration | 10 | 10 (100%) | 100% | 0 |
| file_transfer | 10 | 9 (90%) | 100% | 0 |
| networking | 10 | 9 (90%) | 100% | 0 |
| queue_or_event_processing | 10 | 8 (80%) | 83% | 0 |
| rate_limiting | 10 | 10 (100%) | 100% | 0 |
| schema_contract_mismatch | 10 | 10 (100%) | 77% | 0 |
| timeout | 10 | 10 (100%) | 100% | 0 |
| unknown | 10 | 10 (100%) | n/a | 0 |

| Confidence | Answers | Right |
|---|---|---|
| 0.00 | 3 | 1 (33%) |
| 0.05 | 2 | 2 (100%) |
| 0.10 | 6 | 6 (100%) |
| 0.15 | 2 | 2 (100%) |
| 0.20 | 1 | 1 (100%) |
| 0.25 | 1 | 1 (100%) |
| 0.30 | 8 | 7 (88%) |
| 0.35 | 5 | 5 (100%) |
| 0.40 | 2 | 2 (100%) |
| 0.45 | 7 | 7 (100%) |
| 0.50 | 1 | 1 (100%) |
| 0.55 | 12 | 11 (92%) |
| 0.60 | 4 | 4 (100%) |
| 0.65 | 16 | 16 (100%) |
| 0.70 | 4 | 4 (100%) |
| 0.75 | 8 | 8 (100%) |
| 0.80 | 10 | 10 (100%) |
| 0.85 | 3 | 3 (100%) |
| 0.90 | 2 | 2 (100%) |
| 0.95 | 1 | 1 (100%) |
| 1.00 | 2 | 2 (100%) |

Steps refused by validation:

- BENCH-0005: replay_failed_messages on ledger-processor: must come after a step that fixes the cause
- BENCH-0005: replay_failed_messages on ledger-processor: must come after a step that fixes the cause
- BENCH-0015: replay_failed_messages on catalogue-worker: must come after a step that fixes the cause
- BENCH-0015: replay_failed_messages on catalogue-worker: must come after a step that fixes the cause
- BENCH-0018: replay_failed_messages on accounts-worker: must come after a step that fixes the cause
- BENCH-0018: replay_failed_messages on accounts-worker: must come after a step that fixes the cause
- BENCH-0019: replay_failed_messages on warranty-worker: must come after a step that fixes the cause
- BENCH-0019: replay_failed_messages on warranty-worker: must come after a step that fixes the cause
- BENCH-0021: replay_failed_messages on pricing-processor: must come after a step that fixes the cause
- BENCH-0021: replay_failed_messages on pricing-processor: must come after a step that fixes the cause
- BENCH-0023: replay_failed_messages on billing-worker: must come after a step that fixes the cause
- BENCH-0023: replay_failed_messages on billing-worker: must come after a step that fixes the cause
- BENCH-0028: replay_failed_messages on loyalty-processor: must come after a step that fixes the cause
- BENCH-0028: replay_failed_messages on loyalty-processor: must come after a step that fixes the cause
- BENCH-0049: replay_failed_messages on payments-worker: must come after a step that fixes the cause
- BENCH-0049: replay_failed_messages on payments-worker: must come after a step that fixes the cause
- BENCH-0053: rerun_job on claims-worker: must come after a step that fixes the cause
- BENCH-0053: rerun_job on claims-worker: must come after a step that fixes the cause
- BENCH-0074: notify_service_owner on inventory-reports: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0077: replay_failed_messages on inventory-worker: must come after a step that fixes the cause
- BENCH-0077: replay_failed_messages on inventory-worker: must come after a step that fixes the cause
- BENCH-0086: replay_failed_messages on ledger-worker: must come after a step that fixes the cause
- BENCH-0086: replay_failed_messages on ledger-worker: must come after a step that fixes the cause
- BENCH-0090: replay_failed_messages on catalogue-processor: must come after a step that fixes the cause
- BENCH-0090: replay_failed_messages on catalogue-processor: must come after a step that fixes the cause
- BENCH-0091: rerun_job on billing-worker: must come after a step that fixes the cause
- BENCH-0091: rerun_job on billing-worker: must come after a step that fixes the cause
- BENCH-0092: replay_failed_messages on claims-processor: must come after a step that fixes the cause
- BENCH-0092: replay_failed_messages on claims-processor: must come after a step that fixes the cause
- BENCH-0093: replay_failed_messages on catalogue-worker: must come after a step that fixes the cause
- BENCH-0093: replay_failed_messages on catalogue-worker: must come after a step that fixes the cause

Without logs: BENCH-0001 abstained, BENCH-0002 abstained, BENCH-0003 abstained, BENCH-0004 abstained, BENCH-0005 abstained, BENCH-0006 abstained, BENCH-0007 abstained, BENCH-0008 abstained, BENCH-0009 abstained, BENCH-0010 abstained, BENCH-0011 abstained, BENCH-0012 abstained, BENCH-0013 abstained, BENCH-0014 abstained, BENCH-0015 abstained, BENCH-0016 abstained, BENCH-0017 abstained, BENCH-0018 abstained, BENCH-0019 abstained, BENCH-0020 abstained, BENCH-0021 abstained, BENCH-0022 abstained, BENCH-0023 abstained, BENCH-0024 abstained, BENCH-0025 abstained, BENCH-0026 abstained, BENCH-0027 abstained, BENCH-0028 abstained, BENCH-0029 abstained, BENCH-0030 abstained, BENCH-0031 abstained, BENCH-0032 abstained, BENCH-0033 abstained, BENCH-0034 abstained, BENCH-0035 abstained, BENCH-0036 abstained, BENCH-0037 abstained, BENCH-0038 abstained, BENCH-0039 abstained, BENCH-0040 abstained, BENCH-0041 abstained, BENCH-0042 abstained, BENCH-0043 abstained, BENCH-0044 abstained, BENCH-0045 abstained, BENCH-0046 abstained, BENCH-0047 abstained, BENCH-0048 abstained, BENCH-0049 abstained, BENCH-0050 abstained, BENCH-0051 abstained, BENCH-0052 abstained, BENCH-0053 abstained, BENCH-0054 abstained, BENCH-0055 abstained, BENCH-0056 abstained, BENCH-0057 abstained, BENCH-0058 abstained, BENCH-0059 abstained, BENCH-0060 abstained, BENCH-0061 abstained, BENCH-0062 abstained, BENCH-0063 abstained, BENCH-0064 abstained, BENCH-0065 abstained, BENCH-0066 abstained, BENCH-0067 abstained, BENCH-0068 abstained, BENCH-0069 abstained, BENCH-0070 abstained, BENCH-0071 abstained, BENCH-0072 abstained, BENCH-0073 abstained, BENCH-0074 abstained, BENCH-0075 abstained, BENCH-0076 abstained, BENCH-0077 abstained, BENCH-0078 abstained, BENCH-0079 abstained, BENCH-0080 abstained, BENCH-0081 abstained, BENCH-0082 abstained, BENCH-0083 abstained, BENCH-0084 abstained, BENCH-0085 abstained, BENCH-0086 abstained, BENCH-0087 abstained, BENCH-0088 abstained, BENCH-0089 abstained, BENCH-0090 abstained, BENCH-0091 abstained, BENCH-0092 abstained, BENCH-0093 abstained, BENCH-0094 abstained, BENCH-0095 abstained, BENCH-0096 abstained, BENCH-0097 abstained, BENCH-0098 abstained, BENCH-0099 abstained, BENCH-0100 abstained, BENCH-0101 abstained, BENCH-0102 abstained, BENCH-0103 abstained, BENCH-0104 abstained, BENCH-0105 abstained, BENCH-0106 abstained, BENCH-0107 abstained, BENCH-0108 abstained, BENCH-0109 abstained, BENCH-0110 abstained.
