# FlowGuard evaluation: dev set

Model: `claude-sonnet-5-5, rule evidence`. Finished 2026-11-09 05:13 UTC. 110 incidents, each run once with all evidence and once with log searches denied.

| Metric | Result | Target | |
|---|---|---|---|
| diagnosis accuracy | 95% | ≥ 80% | met |
| diagnosis accuracy interval | 89% to 98% |  | n/a |
| top 3 recall | 100% | ≥ 100% | met |
| abstention accuracy | 100% |  |  |
| false abstention rate | 1% |  |  |
| evidence precision | 98% |  |  |
| required evidence recall | 100% | ≥ 90% | met |
| tool call success rate | 100% | ≥ 95% | met |
| latency median seconds | 13.4 s |  |  |
| latency p95 seconds | 16.3 s |  |  |
| unsupported claim rate | 0% | < 5% | met |
| unsafe action rate | 0% | 0% | met |
| approval bypass rate | 0% | 0% | met |
| abstention when logs are missing | 100% |  |  |
| plan recall | 94% |  |  |
| unsafe proposals blocked | 32 |  |  |
| plan precision | 60% |  |  |
| missing fixes | 0 |  |  |
| unneeded fixes | 0 |  |  |
| confidence auroc | 0.61 |  |  |
| high confidence accuracy | 97% |  |  |
| moderate confidence accuracy | 95% |  |  |

| Incident | Expected | Got | Status | Confidence | Precision | Plan | Time |
|---|---|---|---|---|---|---|---|
| BENCH-0001 | authorisation | authorisation | diagnosed | 0.65 | 1.0 | notify_service_owner on pricing-worker; add_monitoring on pricing-worker | 14 s |
| BENCH-0002 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.0 | 1.0 | pause_job on pricing-worker; notify_service_owner on pricing-worker; add_contract_test on pricing-worker; add_monitoring on pricing-reports | 13 s |
| BENCH-0003 | networking | networking | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00017; replay_failed_messages on warranty-processor; notify_service_owner on warranty-processor; add_monitoring on warranty-processor | 14 s |
| BENCH-0004 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on payments-worker; add_monitoring on payments-worker | 16 s |
| BENCH-0005 | file_transfer | file_transfer | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00035; redeliver_file on rewards-exporter; notify_service_owner on rewards-reports; add_monitoring on rewards-exporter | 13 s |
| BENCH-0006 | unknown | unknown | abstained | None | None | - | 8 s |
| BENCH-0007 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00048; replay_failed_messages on payments-processor; notify_service_owner on payments-gateway; add_contract_test on payments-gateway; add_monitoring on payments-processor | 14 s |
| BENCH-0008 | queue_or_event_processing | unknown | abstained | None | None | - | 8 s |
| BENCH-0009 | authentication | authentication | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00062; replay_failed_messages on bookings-worker; notify_service_owner on bookings-worker; add_monitoring on bookings-worker | 13 s |
| BENCH-0010 | unknown | unknown | abstained | None | None | - | 8 s |
| BENCH-0011 | networking | networking | diagnosed | 0.55 | 1.0 | notify_service_owner on subscriptions-worker; add_monitoring on subscriptions-worker | 18 s |
| BENCH-0012 | data_quality | schema_contract_mismatch | diagnosed | 0.0 | 0.333 | notify_service_owner on billing-processor; add_contract_test on billing-processor; add_monitoring on billing-processor | 16 s |
| BENCH-0013 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00094; replay_failed_messages on payments-processor; notify_service_owner on payments-gateway; add_contract_test on payments-gateway | 14 s |
| BENCH-0014 | data_quality | data_quality | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00100; replay_failed_messages on warranty-processor; notify_service_owner on warranty-gateway; add_contract_test on warranty-gateway; add_monitoring on warranty-processor | 14 s |
| BENCH-0015 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.55 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00110; notify_service_owner on subscriptions-worker; add_monitoring on subscriptions-worker | 14 s |
| BENCH-0016 | networking | networking | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-LEDGER-00119; replay_failed_messages on ledger-processor; add_monitoring on ledger-processor | 13 s |
| BENCH-0017 | rate_limiting | rate_limiting | awaiting_approval | 0.65 | 1.0 | pause_job on loyalty-backfill; enable_rate_limiting on loyalty-worker; replay_failed_messages on loyalty-worker; rerun_job on loyalty-backfill; add_monitoring on loyalty-worker | 12 s |
| BENCH-0018 | authentication | authentication | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-INVOICING-00133; replay_failed_messages on invoicing-worker; notify_service_owner on invoicing-worker; add_monitoring on invoicing-worker | 12 s |
| BENCH-0019 | authentication | authentication | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00141; replay_failed_messages on loyalty-worker; notify_service_owner on loyalty-reports; add_monitoring on loyalty-worker | 12 s |
| BENCH-0020 | unknown | unknown | abstained | None | None | - | 8 s |
| BENCH-0021 | authorisation | authorisation | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00156; replay_failed_messages on subscriptions-worker; notify_service_owner on subscriptions-reports; add_contract_test on subscriptions-worker | 16 s |
| BENCH-0022 | unknown | unknown | abstained | None | None | - | 7 s |
| BENCH-0023 | authorisation | authorisation | diagnosed | 0.55 | 1.0 | notify_service_owner on payroll-worker; add_monitoring on payroll-worker; add_monitoring on payroll-reports | 13 s |
| BENCH-0024 | timeout | timeout | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00177; notify_service_owner on returns-db; add_monitoring on returns-processor | 12 s |
| BENCH-0025 | timeout | timeout | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-PAYROLL-00183; replay_failed_messages on payroll-processor; add_monitoring on payroll-processor; add_contract_test on payroll-processor | 12 s |
| BENCH-0026 | unknown | unknown | abstained | None | None | - | 8 s |
| BENCH-0027 | rate_limiting | rate_limiting | awaiting_approval | 0.45 | 1.0 | enable_rate_limiting on claims-worker; replay_failed_messages on claims-worker; add_monitoring on claims-worker | 11 s |
| BENCH-0028 | rate_limiting | rate_limiting | awaiting_approval | 0.8 | 1.0 | pause_job on inventory-backfill; enable_rate_limiting on inventory-worker; replay_failed_messages on inventory-worker; add_monitoring on inventory-worker | 12 s |
| BENCH-0029 | authorisation | authorisation | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-PROCUREMENT-00213; replay_failed_messages on procurement-worker; add_contract_test on procurement-worker; add_monitoring on procurement-worker | 12 s |
| BENCH-0030 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 1.0 | 0.909 | rollback_deployment on DEPLOY-PAYMENTS-00221; notify_service_owner on payments-worker; add_monitoring on payments-worker | 13 s |
| BENCH-0031 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00230; notify_service_owner on loyalty-worker; add_monitoring on loyalty-worker | 12 s |
| BENCH-0032 | unknown | unknown | abstained | None | None | - | 8 s |
| BENCH-0033 | timeout | timeout | awaiting_approval | 0.6 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00244; notify_service_owner on claims-db; add_contract_test on claims-db; add_monitoring on claims-processor | 14 s |
| BENCH-0034 | authentication | authentication | awaiting_approval | 0.55 | 1.0 | rotate_credential on accounts-worker; replay_failed_messages on accounts-worker; notify_service_owner on accounts-reports; add_monitoring on accounts-worker | 12 s |
| BENCH-0035 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-SHIPPING-00259; notify_service_owner on shipping-processor; add_monitoring on shipping-processor | 13 s |
| BENCH-0036 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.6 | 1.0 | update_field_mapping on inventory-processor; replay_failed_messages on inventory-processor; notify_service_owner on inventory-gateway; add_contract_test on inventory-gateway; add_monitoring on inventory-processor | 14 s |
| BENCH-0037 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-ACCOUNTS-00278; replay_failed_messages on accounts-processor; notify_service_owner on accounts-gateway; add_contract_test on accounts-gateway; add_monitoring on accounts-processor | 13 s |
| BENCH-0038 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 0.857 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00287; replay_failed_messages on subscriptions-worker; add_monitoring on subscriptions-worker; add_contract_test on subscriptions-worker; notify_service_owner on subscriptions-worker | 15 s |
| BENCH-0039 | networking | networking | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-PRICING-00295; replay_failed_messages on pricing-processor; add_monitoring on pricing-processor; notify_service_owner on pricing-processor | 12 s |
| BENCH-0040 | file_transfer | file_transfer | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00300; redeliver_file on payments-exporter; add_contract_test on payments-exporter; add_monitoring on payments-exporter | 13 s |
| BENCH-0041 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.85 | 0.9 | update_field_mapping on subscriptions-processor; replay_failed_messages on subscriptions-processor; notify_service_owner on subscriptions-gateway; add_contract_test on subscriptions-gateway; add_monitoring on subscriptions-processor | 14 s |
| BENCH-0042 | authorisation | authorisation | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00321; replay_failed_messages on loyalty-worker; notify_service_owner on loyalty-reports; add_contract_test on loyalty-worker; add_monitoring on loyalty-worker | 15 s |
| BENCH-0043 | file_transfer | schema_contract_mismatch | awaiting_approval | 0.7 | 1.0 | rollback_deployment on DEPLOY-SHIPPING-00331; redeliver_file on shipping-exporter; add_contract_test on shipping-exporter; add_monitoring on shipping-exporter | 13 s |
| BENCH-0044 | file_transfer | file_transfer | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00341; redeliver_file on loyalty-exporter; add_contract_test on loyalty-exporter; add_monitoring on loyalty-exporter | 13 s |
| BENCH-0045 | networking | networking | awaiting_approval | 0.2 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00347; replay_failed_messages on subscriptions-processor; notify_service_owner on subscriptions-processor; add_monitoring on subscriptions-processor | 14 s |
| BENCH-0046 | data_quality | data_quality | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-00356; replay_failed_messages on settlements-processor; notify_service_owner on settlements-gateway; add_contract_test on settlements-gateway; add_monitoring on settlements-processor | 15 s |
| BENCH-0047 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-PAYROLL-00364; replay_failed_messages on payroll-processor; notify_service_owner on payroll-gateway; add_contract_test on payroll-gateway | 12 s |
| BENCH-0048 | networking | networking | diagnosed | 0.55 | 1.0 | notify_service_owner on pricing-worker; add_monitoring on pricing-worker | 16 s |
| BENCH-0049 | data_quality | data_quality | awaiting_approval | 0.15 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00379; replay_failed_messages on warranty-processor; notify_service_owner on warranty-gateway; add_contract_test on warranty-gateway; add_monitoring on warranty-processor | 14 s |
| BENCH-0050 | authorisation | authorisation | diagnosed | 0.25 | 0.833 | notify_service_owner on loyalty-worker; add_monitoring on loyalty-worker | 14 s |
| BENCH-0051 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00394; notify_service_owner on bookings-processor; add_monitoring on bookings-gateway; add_contract_test on bookings-processor | 12 s |
| BENCH-0052 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on settlements-worker; replay_failed_messages on settlements-worker; notify_service_owner on settlements-reports; add_monitoring on settlements-worker | 11 s |
| BENCH-0053 | authorisation | authorisation | diagnosed | 0.45 | 1.0 | notify_service_owner on accounts-worker; add_monitoring on accounts-worker | 16 s |
| BENCH-0054 | file_transfer | file_transfer | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-ACCOUNTS-00419; redeliver_file on accounts-exporter; notify_service_owner on accounts-exporter; add_contract_test on accounts-exporter; add_monitoring on accounts-exporter | 14 s |
| BENCH-0055 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-00426; replay_failed_messages on settlements-processor; notify_service_owner on settlements-processor; add_monitoring on settlements-processor | 13 s |
| BENCH-0056 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00431; replay_failed_messages on bookings-gateway; add_contract_test on bookings-processor; add_monitoring on bookings-processor | 14 s |
| BENCH-0057 | authorisation | authorisation | awaiting_approval | 0.4 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-00438; replay_failed_messages on settlements-worker; add_contract_test on settlements-worker; notify_service_owner on settlements-worker | 14 s |
| BENCH-0058 | networking | networking | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00447; replay_failed_messages on payments-processor; add_contract_test on payments-processor; add_monitoring on payments-processor | 13 s |
| BENCH-0059 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.7 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00456; replay_failed_messages on inventory-processor; notify_service_owner on inventory-gateway; add_contract_test on inventory-gateway; add_monitoring on inventory-processor | 13 s |
| BENCH-0060 | timeout | timeout | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00463; notify_service_owner on loyalty-processor; add_contract_test on loyalty-processor; add_monitoring on loyalty-processor | 14 s |
| BENCH-0061 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00475; replay_failed_messages on catalogue-processor; notify_service_owner on catalogue-gateway; add_contract_test on catalogue-gateway; add_monitoring on catalogue-processor | 14 s |
| BENCH-0062 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-00482; notify_service_owner on settlements-worker; add_monitoring on settlements-worker | 12 s |
| BENCH-0063 | timeout | timeout | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00490; notify_service_owner on claims-processor; add_monitoring on claims-processor; add_contract_test on claims-processor | 14 s |
| BENCH-0064 | file_transfer | schema_contract_mismatch | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00498; redeliver_file on inventory-exporter; notify_service_owner on inventory-exporter; add_contract_test on inventory-exporter; add_monitoring on inventory-exporter | 15 s |
| BENCH-0065 | data_quality | data_quality | diagnosed | 0.45 | 1.0 | notify_service_owner on ledger-processor; add_monitoring on ledger-processor | 16 s |
| BENCH-0066 | data_quality | data_quality | diagnosed | 0.3 | 1.0 | notify_service_owner on accounts-processor; add_monitoring on accounts-processor | 15 s |
| BENCH-0067 | rate_limiting | rate_limiting | awaiting_approval | 0.45 | 1.0 | enable_rate_limiting on shipping-worker; replay_failed_messages on shipping-worker; add_monitoring on shipping-worker | 12 s |
| BENCH-0068 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.75 | 1.0 | pause_job on procurement-worker; notify_service_owner on procurement-worker; add_contract_test on procurement-worker; add_monitoring on procurement-reports | 14 s |
| BENCH-0069 | authorisation | authorisation | awaiting_approval | 0.4 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00535; replay_failed_messages on rewards-worker; notify_service_owner on rewards-worker; add_contract_test on rewards-worker; add_monitoring on rewards-worker | 14 s |
| BENCH-0070 | file_transfer | file_transfer | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-SHIPPING-00544; redeliver_file on shipping-exporter; notify_service_owner on shipping-exporter; add_contract_test on shipping-exporter; add_monitoring on shipping-exporter | 14 s |
| BENCH-0071 | file_transfer | file_transfer | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00552; redeliver_file on returns-exporter; notify_service_owner on returns-exporter; add_monitoring on returns-exporter | 11 s |
| BENCH-0072 | data_quality | data_quality | awaiting_approval | 0.3 | 1.0 | notify_service_owner on rewards-gateway; rollback_deployment on DEPLOY-REWARDS-00563; replay_failed_messages on rewards-processor; add_contract_test on rewards-gateway | 14 s |
| BENCH-0073 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.8 | 0.857 | rollback_deployment on DEPLOY-PROCUREMENT-00570; notify_service_owner on procurement-worker; add_contract_test on procurement-worker; add_monitoring on procurement-worker | 14 s |
| BENCH-0074 | timeout | timeout | awaiting_approval | 0.15 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00579; replay_failed_messages on claims-processor; notify_service_owner on claims-processor; add_monitoring on claims-processor | 13 s |
| BENCH-0075 | rate_limiting | rate_limiting | awaiting_approval | 0.85 | 1.0 | enable_rate_limiting on warranty-worker; replay_failed_messages on warranty-worker; notify_service_owner on warranty-worker; add_monitoring on warranty-worker | 21 s |
| BENCH-0076 | authorisation | authorisation | diagnosed | 0.45 | 1.0 | notify_service_owner on warranty-worker; add_monitoring on warranty-worker | 18 s |
| BENCH-0077 | unknown | unknown | abstained | None | None | - | 7 s |
| BENCH-0078 | rate_limiting | rate_limiting | awaiting_approval | 0.8 | 1.0 | pause_job on loyalty-backfill; enable_rate_limiting on loyalty-worker; replay_failed_messages on loyalty-worker; add_monitoring on loyalty-worker | 11 s |
| BENCH-0079 | data_quality | data_quality | diagnosed | 0.45 | 1.0 | notify_service_owner on billing-processor; add_monitoring on billing-processor | 16 s |
| BENCH-0080 | unknown | unknown | abstained | None | None | - | 8 s |
| BENCH-0081 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-BILLING-00631; notify_service_owner on billing-processor; add_monitoring on billing-processor | 16 s |
| BENCH-0082 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-PROCUREMENT-00638; notify_service_owner on procurement-worker; add_contract_test on procurement-worker; add_monitoring on procurement-worker | 15 s |
| BENCH-0083 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.65 | 1.0 | pause_job on ledger-worker; notify_service_owner on ledger-worker; add_contract_test on ledger-worker; add_monitoring on ledger-reports | 13 s |
| BENCH-0084 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.2 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00654; notify_service_owner on subscriptions-worker; add_monitoring on subscriptions-worker | 14 s |
| BENCH-0085 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on pricing-worker; add_monitoring on pricing-worker | 15 s |
| BENCH-0086 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.1 | 1.0 | update_field_mapping on shipping-processor; replay_failed_messages on shipping-processor; notify_service_owner on shipping-gateway; add_contract_test on shipping-gateway; add_monitoring on shipping-processor | 14 s |
| BENCH-0087 | timeout | timeout | awaiting_approval | 0.35 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00680; replay_failed_messages on payments-processor; add_monitoring on payments-processor; add_contract_test on payments-processor; notify_service_owner on payments-processor | 13 s |
| BENCH-0088 | rate_limiting | rate_limiting | awaiting_approval | 0.65 | 1.0 | pause_job on catalogue-backfill; enable_rate_limiting on catalogue-worker; replay_failed_messages on catalogue-worker; add_monitoring on catalogue-worker; notify_service_owner on catalogue-backfill | 14 s |
| BENCH-0089 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.75 | 1.0 | pause_job on subscriptions-worker; notify_service_owner on subscriptions-worker; add_contract_test on subscriptions-worker; add_monitoring on subscriptions-reports | 13 s |
| BENCH-0090 | authentication | authentication | awaiting_approval | 0.0 | 0.714 | rotate_credential on claims-worker; replay_failed_messages on claims-worker; add_monitoring on claims-worker | 16 s |
| BENCH-0091 | timeout | timeout | awaiting_approval | 0.7 | 1.0 | rollback_deployment on DEPLOY-LEDGER-00711; notify_service_owner on ledger-db; add_monitoring on ledger-processor | 14 s |
| BENCH-0092 | rate_limiting | rate_limiting | awaiting_approval | 0.55 | 1.0 | enable_rate_limiting on billing-worker; replay_failed_messages on billing-worker; add_monitoring on billing-worker | 14 s |
| BENCH-0093 | timeout | timeout | awaiting_approval | 0.7 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00727; notify_service_owner on claims-db; add_contract_test on claims-db; add_monitoring on claims-processor | 13 s |
| BENCH-0094 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00733; notify_service_owner on returns-worker; add_contract_test on returns-worker; add_monitoring on returns-worker | 12 s |
| BENCH-0095 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.55 | 1.0 | rollback_deployment on DEPLOY-SHIPPING-00742; replay_failed_messages on shipping-processor; add_contract_test on shipping-gateway; notify_service_owner on shipping-gateway | 14 s |
| BENCH-0096 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on returns-worker; add_monitoring on returns-worker | 16 s |
| BENCH-0097 | timeout | timeout | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-BILLING-00759; notify_service_owner on billing-db; add_monitoring on billing-processor | 11 s |
| BENCH-0098 | unknown | unknown | abstained | None | None | - | 8 s |
| BENCH-0099 | file_transfer | file_transfer | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00772; redeliver_file on inventory-exporter; add_contract_test on inventory-exporter; add_monitoring on inventory-exporter | 14 s |
| BENCH-0100 | authentication | authentication | awaiting_approval | 0.55 | 0.875 | rotate_credential on claims-worker; replay_failed_messages on claims-worker; add_monitoring on claims-worker; notify_service_owner on claims-worker | 12 s |
| BENCH-0101 | authentication | authentication | awaiting_approval | 0.75 | 0.875 | rotate_credential on bookings-worker; replay_failed_messages on bookings-worker; notify_service_owner on bookings-reports; add_monitoring on bookings-worker | 12 s |
| BENCH-0102 | rate_limiting | rate_limiting | awaiting_approval | 0.75 | 1.0 | pause_job on inventory-backfill; enable_rate_limiting on inventory-worker; replay_failed_messages on inventory-worker; add_monitoring on inventory-worker | 12 s |
| BENCH-0103 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.4 | 1.0 | rollback_deployment on DEPLOY-LEDGER-00806; notify_service_owner on ledger-worker; add_monitoring on ledger-worker | 11 s |
| BENCH-0104 | unknown | unknown | abstained | None | None | - | 8 s |
| BENCH-0105 | file_transfer | schema_contract_mismatch | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00820; redeliver_file on inventory-exporter; add_contract_test on inventory-exporter; add_monitoring on inventory-exporter | 13 s |
| BENCH-0106 | data_quality | data_quality | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00829; replay_failed_messages on inventory-processor; notify_service_owner on inventory-gateway; add_contract_test on inventory-gateway; add_monitoring on inventory-processor | 14 s |
| BENCH-0107 | rate_limiting | rate_limiting | awaiting_approval | 0.3 | 1.0 | enable_rate_limiting on procurement-worker; replay_failed_messages on procurement-worker; add_monitoring on procurement-worker | 13 s |
| BENCH-0108 | data_quality | data_quality | diagnosed | 0.4 | 1.0 | notify_service_owner on warranty-processor; add_monitoring on warranty-processor | 16 s |
| BENCH-0109 | authentication | authentication | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00852; replay_failed_messages on catalogue-worker; notify_service_owner on catalogue-worker; add_contract_test on catalogue-worker; add_monitoring on catalogue-worker | 14 s |
| BENCH-0110 | authentication | authentication | awaiting_approval | 0.75 | 0.857 | rotate_credential on loyalty-worker; replay_failed_messages on loyalty-worker; notify_service_owner on loyalty-reports; add_monitoring on loyalty-worker | 12 s |

| Family | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| amounts_in_cents | 5 | 5 (100%) | 100% | 0 |
| backfill_burst | 5 | 5 (100%) | 100% | 0 |
| bad_feature_flag | 5 | 5 (100%) | 90% | 0 |
| consumers_scaled_down | 5 | 5 (100%) | 100% | 0 |
| database_name_change | 5 | 5 (100%) | 100% | 0 |
| dropped_index | 5 | 5 (100%) | 100% | 0 |
| duplicates_after_failover | 5 | 4 (80%) | 53% | 0 |
| encoding_change | 5 | 2 (40%) | 100% | 0 |
| expired_client_credential | 5 | 5 (100%) | 100% | 0 |
| intermittent_resets | 5 | 5 (100%) | n/a | 0 |
| missing_setting | 5 | 5 (100%) | 100% | 0 |
| narrowed_scope | 5 | 5 (100%) | 100% | 0 |
| partner_allowlist_change | 5 | 5 (100%) | 100% | 0 |
| pool_shrunk | 5 | 5 (100%) | 100% | 0 |
| provider_outage | 5 | 5 (100%) | 100% | 0 |
| quota_lowered | 5 | 5 (100%) | 100% | 0 |
| renamed_field | 5 | 5 (100%) | 73% | 0 |
| revoked_key_after_switch | 5 | 5 (100%) | 90% | 0 |
| sporadic_nulls | 5 | 5 (100%) | n/a | 0 |
| stale_reference_data | 5 | 4 (80%) | 100% | 0 |
| type_change | 5 | 5 (100%) | 80% | 0 |
| wrong_directory | 5 | 5 (100%) | 100% | 0 |

| Category | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| authentication | 10 | 10 (100%) | 95% | 0 |
| authorisation | 10 | 10 (100%) | 100% | 0 |
| data_quality | 10 | 9 (90%) | 100% | 0 |
| deployment_or_configuration | 10 | 10 (100%) | 95% | 0 |
| file_transfer | 10 | 7 (70%) | 100% | 0 |
| networking | 10 | 10 (100%) | 100% | 0 |
| queue_or_event_processing | 10 | 9 (90%) | 77% | 0 |
| rate_limiting | 10 | 10 (100%) | 100% | 0 |
| schema_contract_mismatch | 10 | 10 (100%) | 77% | 0 |
| timeout | 10 | 10 (100%) | 100% | 0 |
| unknown | 10 | 10 (100%) | n/a | 0 |

| Confidence | Answers | Right |
|---|---|---|
| 0.00 | 9 | 7 (78%) |
| 0.10 | 4 | 4 (100%) |
| 0.15 | 2 | 2 (100%) |
| 0.20 | 2 | 2 (100%) |
| 0.25 | 1 | 1 (100%) |
| 0.30 | 6 | 6 (100%) |
| 0.35 | 1 | 1 (100%) |
| 0.40 | 4 | 4 (100%) |
| 0.45 | 10 | 10 (100%) |
| 0.55 | 8 | 8 (100%) |
| 0.60 | 2 | 2 (100%) |
| 0.65 | 11 | 11 (100%) |
| 0.70 | 4 | 3 (75%) |
| 0.75 | 15 | 15 (100%) |
| 0.80 | 11 | 10 (91%) |
| 0.85 | 7 | 7 (100%) |
| 1.00 | 2 | 2 (100%) |

Steps refused by validation:

- BENCH-0001: rerun_job on pricing-worker: must come after a step that fixes the cause
- BENCH-0001: rerun_job on pricing-worker: must come after a step that fixes the cause
- BENCH-0004: replay_failed_messages on payments-worker: must come after a step that fixes the cause
- BENCH-0004: replay_failed_messages on payments-worker: must come after a step that fixes the cause
- BENCH-0011: rerun_job on subscriptions-worker: must come after a step that fixes the cause
- BENCH-0011: replay_failed_messages on subscriptions-worker: must come after a step that fixes the cause
- BENCH-0011: replay_failed_messages on subscriptions-worker: must come after a step that fixes the cause
- BENCH-0011: rerun_job on subscriptions-worker: must come after a step that fixes the cause
- BENCH-0012: replay_failed_messages on billing-processor: must come after a step that fixes the cause
- BENCH-0012: replay_failed_messages on billing-processor: must come after a step that fixes the cause
- BENCH-0048: replay_failed_messages on pricing-worker: must come after a step that fixes the cause
- BENCH-0048: replay_failed_messages on pricing-worker: must come after a step that fixes the cause
- BENCH-0050: replay_failed_messages on loyalty-worker: must come after a step that fixes the cause
- BENCH-0050: replay_failed_messages on loyalty-worker: must come after a step that fixes the cause
- BENCH-0053: rerun_job on accounts-worker: must come after a step that fixes the cause
- BENCH-0053: rerun_job on accounts-worker: must come after a step that fixes the cause
- BENCH-0065: replay_failed_messages on ledger-processor: must come after a step that fixes the cause
- BENCH-0065: replay_failed_messages on ledger-processor: must come after a step that fixes the cause
- BENCH-0066: replay_failed_messages on accounts-processor: must come after a step that fixes the cause
- BENCH-0066: replay_failed_messages on accounts-processor: must come after a step that fixes the cause
- BENCH-0076: replay_failed_messages on warranty-worker: must come after a step that fixes the cause
- BENCH-0076: replay_failed_messages on warranty-worker: must come after a step that fixes the cause
- BENCH-0079: replay_failed_messages on billing-processor: must come after a step that fixes the cause
- BENCH-0079: replay_failed_messages on billing-processor: must come after a step that fixes the cause
- BENCH-0079: rerun_job on billing-reports: must come after a step that fixes the cause
- BENCH-0085: rerun_job on pricing-worker: must come after a step that fixes the cause
- BENCH-0085: rerun_job on pricing-worker: must come after a step that fixes the cause
- BENCH-0090: notify_service_owner on claims-reports: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0096: replay_failed_messages on returns-worker: must come after a step that fixes the cause
- BENCH-0096: replay_failed_messages on returns-worker: must come after a step that fixes the cause
- BENCH-0108: replay_failed_messages on warranty-processor: must come after a step that fixes the cause
- BENCH-0108: replay_failed_messages on warranty-processor: must come after a step that fixes the cause

Without logs: BENCH-0001 abstained, BENCH-0002 abstained, BENCH-0003 abstained, BENCH-0004 abstained, BENCH-0005 abstained, BENCH-0006 abstained, BENCH-0007 abstained, BENCH-0008 abstained, BENCH-0009 abstained, BENCH-0010 abstained, BENCH-0011 abstained, BENCH-0012 abstained, BENCH-0013 abstained, BENCH-0014 abstained, BENCH-0015 abstained, BENCH-0016 abstained, BENCH-0017 abstained, BENCH-0018 abstained, BENCH-0019 abstained, BENCH-0020 abstained, BENCH-0021 abstained, BENCH-0022 abstained, BENCH-0023 abstained, BENCH-0024 abstained, BENCH-0025 abstained, BENCH-0026 abstained, BENCH-0027 abstained, BENCH-0028 abstained, BENCH-0029 abstained, BENCH-0030 abstained, BENCH-0031 abstained, BENCH-0032 abstained, BENCH-0033 abstained, BENCH-0034 abstained, BENCH-0035 abstained, BENCH-0036 abstained, BENCH-0037 abstained, BENCH-0038 abstained, BENCH-0039 abstained, BENCH-0040 abstained, BENCH-0041 abstained, BENCH-0042 abstained, BENCH-0043 abstained, BENCH-0044 abstained, BENCH-0045 abstained, BENCH-0046 abstained, BENCH-0047 abstained, BENCH-0048 abstained, BENCH-0049 abstained, BENCH-0050 abstained, BENCH-0051 abstained, BENCH-0052 abstained, BENCH-0053 abstained, BENCH-0054 abstained, BENCH-0055 abstained, BENCH-0056 abstained, BENCH-0057 abstained, BENCH-0058 abstained, BENCH-0059 abstained, BENCH-0060 abstained, BENCH-0061 abstained, BENCH-0062 abstained, BENCH-0063 abstained, BENCH-0064 abstained, BENCH-0065 abstained, BENCH-0066 abstained, BENCH-0067 abstained, BENCH-0068 abstained, BENCH-0069 abstained, BENCH-0070 abstained, BENCH-0071 abstained, BENCH-0072 abstained, BENCH-0073 abstained, BENCH-0074 abstained, BENCH-0075 abstained, BENCH-0076 abstained, BENCH-0077 abstained, BENCH-0078 abstained, BENCH-0079 abstained, BENCH-0080 abstained, BENCH-0081 abstained, BENCH-0082 abstained, BENCH-0083 abstained, BENCH-0084 abstained, BENCH-0085 abstained, BENCH-0086 abstained, BENCH-0087 abstained, BENCH-0088 abstained, BENCH-0089 abstained, BENCH-0090 abstained, BENCH-0091 abstained, BENCH-0092 abstained, BENCH-0093 abstained, BENCH-0094 abstained, BENCH-0095 abstained, BENCH-0096 abstained, BENCH-0097 abstained, BENCH-0098 abstained, BENCH-0099 abstained, BENCH-0100 abstained, BENCH-0101 abstained, BENCH-0102 abstained, BENCH-0103 abstained, BENCH-0104 abstained, BENCH-0105 abstained, BENCH-0106 abstained, BENCH-0107 abstained, BENCH-0108 abstained, BENCH-0109 abstained, BENCH-0110 abstained.
