# FlowGuard evaluation: dev set

Model: `gemma4:12b`. Finished 2026-11-07 05:51 UTC. 110 incidents, each run once with all evidence and once with log searches denied.

| Metric | Result | Target | |
|---|---|---|---|
| diagnosis accuracy | 87% | ≥ 80% | met |
| diagnosis accuracy interval | 79% to 92% |  | n/a |
| top 3 recall | 93% | ≥ 100% | missed |
| abstention accuracy | 100% |  |  |
| false abstention rate | 5% |  |  |
| evidence precision | 100% |  |  |
| required evidence recall | 100% | ≥ 90% | met |
| tool call success rate | 100% | ≥ 95% | met |
| latency median seconds | 41.5 s |  |  |
| latency p95 seconds | 61.5 s |  |  |
| unsupported claim rate | 0% | < 5% | met |
| unsafe action rate | 0% | 0% | met |
| approval bypass rate | 0% | 0% | met |
| abstention when logs are missing | 100% |  |  |
| plan recall | 86% |  |  |
| unsafe proposals blocked | 33 |  |  |
| plan precision | 62% |  |  |
| missing fixes | 2 |  |  |
| unneeded fixes | 0 |  |  |
| confidence auroc | 0.42 |  |  |
| high confidence accuracy | 91% |  |  |
| moderate confidence accuracy | 92% |  |  |

| Incident | Expected | Got | Status | Confidence | Precision | Plan | Time |
|---|---|---|---|---|---|---|---|
| BENCH-0001 | unknown | unknown | abstained | None | None | - | 29 s |
| BENCH-0002 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00006; add_monitoring on rewards-worker | 29 s |
| BENCH-0003 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.85 | 1.0 | update_field_mapping on invoicing-processor; replay_failed_messages on invoicing-processor; add_contract_test on invoicing-gateway; notify_service_owner on invoicing-processor | 40 s |
| BENCH-0004 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.85 | 1.0 | update_field_mapping on pricing-processor; replay_failed_messages on pricing-processor; add_contract_test on pricing-processor; notify_service_owner on pricing-processor | 38 s |
| BENCH-0005 | data_quality | queue_or_event_processing | diagnosed | 0.75 | 1.0 | notify_service_owner on ledger-processor; add_monitoring on ledger-processor | 56 s |
| BENCH-0006 | rate_limiting | rate_limiting | awaiting_approval | 0.8 | 1.0 | enable_rate_limiting on payments-worker; replay_failed_messages on payments-worker; notify_service_owner on payments-worker; add_monitoring on payments-worker | 40 s |
| BENCH-0007 | file_transfer | file_transfer | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-INVOICING-00044; redeliver_file on invoicing-exporter; add_contract_test on invoicing-exporter; notify_service_owner on invoicing-exporter; add_monitoring on invoicing-exporter | 44 s |
| BENCH-0008 | file_transfer | file_transfer | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00051; redeliver_file on onboarding-exporter; add_contract_test on onboarding-exporter; notify_service_owner on onboarding-exporter | 50 s |
| BENCH-0009 | networking | networking | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PRICING-00059; replay_failed_messages on pricing-processor; add_monitoring on pricing-processor; notify_service_owner on pricing-processor; add_contract_test on pricing-processor | 45 s |
| BENCH-0010 | networking | networking | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00068; replay_failed_messages on rewards-processor; add_monitoring on rewards-processor; notify_service_owner on rewards-processor | 42 s |
| BENCH-0011 | unknown | unknown | abstained | None | None | - | 18 s |
| BENCH-0012 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on warranty-worker; replay_failed_messages on warranty-worker; add_monitoring on warranty-worker | 41 s |
| BENCH-0013 | timeout | timeout | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00084; replay_failed_messages on onboarding-processor; notify_service_owner on onboarding-db; add_monitoring on onboarding-processor | 46 s |
| BENCH-0014 | rate_limiting | rate_limiting | awaiting_approval | 0.65 | 1.0 | enable_rate_limiting on loyalty-worker; replay_failed_messages on loyalty-worker; notify_service_owner on loyalty-worker; add_monitoring on loyalty-worker | 42 s |
| BENCH-0015 | authorisation | unknown | abstained | None | None | - | 23 s |
| BENCH-0016 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.85 | 1.0 | update_field_mapping on shipping-processor; replay_failed_messages on shipping-processor; add_contract_test on shipping-gateway; notify_service_owner on shipping-gateway | 40 s |
| BENCH-0017 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on returns-worker; replay_failed_messages on returns-worker; add_monitoring on returns-worker | 35 s |
| BENCH-0018 | authorisation | authorisation | diagnosed | 0.75 | 1.0 | notify_service_owner on accounts-worker; add_monitoring on accounts-worker | 67 s |
| BENCH-0019 | networking | networking | diagnosed | 0.75 | 1.0 | - | 49 s |
| BENCH-0020 | authorisation | authorisation | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-SHIPPING-00141; replay_failed_messages on shipping-worker; add_contract_test on shipping-worker | 34 s |
| BENCH-0021 | data_quality | data_quality | diagnosed | 0.75 | 1.0 | notify_service_owner on pricing-processor; add_monitoring on pricing-processor | 65 s |
| BENCH-0022 | data_quality | data_quality | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00159; replay_failed_messages on onboarding-processor; add_contract_test on onboarding-gateway; notify_service_owner on onboarding-gateway | 43 s |
| BENCH-0023 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on billing-worker; add_monitoring on billing-worker | 48 s |
| BENCH-0024 | unknown | unknown | abstained | None | None | - | 18 s |
| BENCH-0025 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00178; add_monitoring on rewards-worker; notify_service_owner on rewards-worker | 37 s |
| BENCH-0026 | timeout | deployment_or_configuration | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-BILLING-00186; notify_service_owner on billing-processor; add_monitoring on billing-processor | 53 s |
| BENCH-0027 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00195; notify_service_owner on subscriptions-processor; add_monitoring on subscriptions-processor | 38 s |
| BENCH-0028 | data_quality | data_quality | diagnosed | 0.65 | 1.0 | notify_service_owner on loyalty-processor | 62 s |
| BENCH-0029 | queue_or_event_processing | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00211; replay_failed_messages on loyalty-worker; add_monitoring on loyalty-worker | 47 s |
| BENCH-0030 | timeout | timeout | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PAYROLL-00219; replay_failed_messages on payroll-processor; add_monitoring on payroll-processor | 40 s |
| BENCH-0031 | file_transfer | file_transfer | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00228; notify_service_owner on rewards-exporter; add_monitoring on rewards-exporter | 50 s |
| BENCH-0032 | data_quality | data_quality | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00236; replay_failed_messages on subscriptions-processor; add_contract_test on subscriptions-gateway; notify_service_owner on subscriptions-gateway; add_monitoring on subscriptions-processor | 48 s |
| BENCH-0033 | networking | networking | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00246; replay_failed_messages on warranty-processor; notify_service_owner on warranty-processor; add_monitoring on warranty-processor | 54 s |
| BENCH-0034 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PRICING-00256; notify_service_owner on pricing-processor; add_contract_test on pricing-processor; add_monitoring on pricing-processor | 43 s |
| BENCH-0035 | queue_or_event_processing | unknown | abstained | None | None | - | 20 s |
| BENCH-0036 | queue_or_event_processing | queue_or_event_processing | diagnosed | 0.75 | 1.0 | notify_service_owner on billing-worker; add_contract_test on billing-worker; add_monitoring on billing-worker | 32 s |
| BENCH-0037 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on subscriptions-worker; replay_failed_messages on subscriptions-worker; add_monitoring on subscriptions-worker | 31 s |
| BENCH-0038 | authentication | authentication | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00285; replay_failed_messages on onboarding-worker; notify_service_owner on onboarding-worker; add_monitoring on onboarding-worker | 40 s |
| BENCH-0039 | authorisation | authorisation | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00293; replay_failed_messages on catalogue-worker; add_contract_test on catalogue-worker; notify_service_owner on catalogue-worker | 48 s |
| BENCH-0040 | unknown | unknown | abstained | None | None | - | 13 s |
| BENCH-0041 | timeout | timeout | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00305; replay_failed_messages on loyalty-processor; add_monitoring on loyalty-processor; notify_service_owner on loyalty-processor | 44 s |
| BENCH-0042 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on warranty-worker; replay_failed_messages on warranty-worker; add_monitoring on warranty-worker; notify_service_owner on warranty-worker | 41 s |
| BENCH-0043 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00320; replay_failed_messages on catalogue-processor; add_contract_test on catalogue-gateway; notify_service_owner on catalogue-gateway; add_monitoring on catalogue-processor | 48 s |
| BENCH-0044 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00328; replay_failed_messages on subscriptions-worker; add_monitoring on subscriptions-worker; notify_service_owner on subscriptions-worker; add_contract_test on subscriptions-worker | 44 s |
| BENCH-0045 | rate_limiting | rate_limiting | awaiting_approval | 0.8 | 1.0 | pause_job on claims-backfill; enable_rate_limiting on claims-worker; replay_failed_messages on claims-worker; notify_service_owner on claims-backfill; add_monitoring on claims-worker | 49 s |
| BENCH-0046 | networking | networking | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00346; replay_failed_messages on warranty-processor; notify_service_owner on warranty-processor; add_monitoring on warranty-processor | 44 s |
| BENCH-0047 | authorisation | authorisation | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00351; replay_failed_messages on catalogue-worker; add_contract_test on catalogue-worker; notify_service_owner on catalogue-worker | 39 s |
| BENCH-0048 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PROCUREMENT-00359; replay_failed_messages on procurement-processor; add_contract_test on procurement-gateway; notify_service_owner on procurement-gateway; add_monitoring on procurement-processor | 45 s |
| BENCH-0049 | authorisation | authorisation | diagnosed | 0.75 | 1.0 | notify_service_owner on payments-worker; add_monitoring on payments-worker | 32 s |
| BENCH-0050 | file_transfer | file_transfer | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00374; redeliver_file on bookings-exporter; add_monitoring on bookings-exporter | 33 s |
| BENCH-0051 | timeout | timeout | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-BILLING-00384; replay_failed_messages on billing-processor; notify_service_owner on billing-processor; add_monitoring on billing-processor | 42 s |
| BENCH-0052 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00390; add_contract_test on returns-processor; notify_service_owner on returns-processor | 33 s |
| BENCH-0053 | networking | networking | diagnosed | 0.75 | 1.0 | add_monitoring on claims-worker | 44 s |
| BENCH-0054 | file_transfer | file_transfer | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00406; redeliver_file on payments-exporter; add_contract_test on payments-exporter; notify_service_owner on payments-exporter; add_monitoring on payments-exporter | 41 s |
| BENCH-0055 | rate_limiting | rate_limiting | awaiting_approval | 0.75 | 1.0 | enable_rate_limiting on invoicing-worker; replay_failed_messages on invoicing-worker; notify_service_owner on invoicing-worker; add_monitoring on invoicing-worker | 44 s |
| BENCH-0056 | data_quality | data_quality | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00420; replay_failed_messages on loyalty-processor; add_contract_test on loyalty-gateway; notify_service_owner on loyalty-gateway | 38 s |
| BENCH-0057 | timeout | timeout | awaiting_approval | 1.0 | 1.0 | rollback_deployment on DEPLOY-LEDGER-00429; replay_failed_messages on ledger-processor; notify_service_owner on ledger-db; add_monitoring on ledger-processor | 40 s |
| BENCH-0058 | timeout | timeout | awaiting_approval | 0.8 | 1.0 | pause_job on claims-processor; notify_service_owner on claims-processor; add_monitoring on claims-processor | 49 s |
| BENCH-0059 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PRICING-00448; replay_failed_messages on pricing-worker; add_monitoring on pricing-worker; notify_service_owner on pricing-worker | 38 s |
| BENCH-0060 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-INVOICING-00459; replay_failed_messages on invoicing-processor; add_contract_test on invoicing-gateway; notify_service_owner on invoicing-gateway; add_monitoring on invoicing-processor | 44 s |
| BENCH-0061 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-BILLING-00468; replay_failed_messages on billing-processor; add_contract_test on billing-gateway; notify_service_owner on billing-gateway; add_monitoring on billing-processor | 44 s |
| BENCH-0062 | timeout | timeout | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00479; replay_failed_messages on inventory-processor; add_monitoring on inventory-processor | 66 s |
| BENCH-0063 | rate_limiting | rate_limiting | awaiting_approval | 0.8 | 1.0 | pause_job on onboarding-backfill; enable_rate_limiting on onboarding-worker; replay_failed_messages on onboarding-worker; add_monitoring on onboarding-worker; notify_service_owner on onboarding-backfill | 62 s |
| BENCH-0064 | authorisation | authorisation | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00495; replay_failed_messages on claims-worker; add_contract_test on claims-worker; notify_service_owner on claims-worker | 43 s |
| BENCH-0065 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PRICING-00501; add_contract_test on pricing-processor; add_monitoring on pricing-processor | 34 s |
| BENCH-0066 | rate_limiting | rate_limiting | awaiting_approval | 0.75 | 1.0 | pause_job on payroll-worker; enable_rate_limiting on payroll-worker; replay_failed_messages on payroll-worker; notify_service_owner on payroll-worker; add_monitoring on payroll-worker | 51 s |
| BENCH-0067 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00516; notify_service_owner on subscriptions-processor; add_monitoring on subscriptions-processor | 31 s |
| BENCH-0068 | file_transfer | file_transfer | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PRICING-00524; redeliver_file on pricing-exporter; add_monitoring on pricing-exporter | 61 s |
| BENCH-0069 | authentication | authentication | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-00534; replay_failed_messages on settlements-worker; notify_service_owner on settlements-worker; add_monitoring on settlements-worker | 40 s |
| BENCH-0070 | queue_or_event_processing | queue_or_event_processing | diagnosed | 0.9 | 1.0 | notify_service_owner on billing-worker; add_contract_test on billing-worker; add_monitoring on billing-worker | 38 s |
| BENCH-0071 | queue_or_event_processing | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00551; replay_failed_messages on onboarding-worker; add_monitoring on onboarding-worker | 40 s |
| BENCH-0072 | data_quality | data_quality | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00558; replay_failed_messages on loyalty-processor; add_contract_test on loyalty-gateway; add_monitoring on loyalty-processor | 38 s |
| BENCH-0073 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00566; replay_failed_messages on catalogue-worker; add_monitoring on catalogue-worker | 37 s |
| BENCH-0074 | file_transfer | file_transfer | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00576; redeliver_file on inventory-exporter; notify_service_owner on inventory-exporter; add_monitoring on inventory-exporter | 47 s |
| BENCH-0075 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on procurement-worker; replay_failed_messages on procurement-worker; add_monitoring on procurement-worker | 37 s |
| BENCH-0076 | unknown | unknown | abstained | None | None | - | 10 s |
| BENCH-0077 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on inventory-worker; add_monitoring on inventory-worker | 55 s |
| BENCH-0078 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-ACCOUNTS-00609; replay_failed_messages on accounts-processor; add_contract_test on accounts-gateway; notify_service_owner on accounts-gateway; add_monitoring on accounts-processor | 44 s |
| BENCH-0079 | unknown | unknown | abstained | None | None | - | 18 s |
| BENCH-0080 | authentication | authentication | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00621; replay_failed_messages on inventory-worker; notify_service_owner on inventory-worker; add_monitoring on inventory-worker | 42 s |
| BENCH-0081 | file_transfer | file_transfer | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-BILLING-00628; notify_service_owner on billing-exporter; add_monitoring on billing-exporter | 48 s |
| BENCH-0082 | authentication | authentication | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-ACCOUNTS-00635; replay_failed_messages on accounts-worker; notify_service_owner on accounts-worker; add_contract_test on accounts-worker; add_monitoring on accounts-worker | 46 s |
| BENCH-0083 | rate_limiting | rate_limiting | awaiting_approval | 0.75 | 1.0 | pause_job on payroll-backfill; enable_rate_limiting on payroll-worker; replay_failed_messages on payroll-worker; notify_service_owner on payroll-worker; add_monitoring on payroll-worker | 51 s |
| BENCH-0084 | unknown | unknown | abstained | None | None | - | 16 s |
| BENCH-0085 | file_transfer | schema_contract_mismatch | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00657; redeliver_file on inventory-exporter; add_contract_test on inventory-exporter; notify_service_owner on inventory-exporter | 34 s |
| BENCH-0086 | authorisation | authorisation | diagnosed | 0.75 | 1.0 | notify_service_owner on ledger-worker; add_monitoring on ledger-worker | 53 s |
| BENCH-0087 | rate_limiting | rate_limiting | awaiting_approval | 0.65 | 1.0 | pause_job on payroll-backfill; enable_rate_limiting on payroll-worker; replay_failed_messages on payroll-worker; add_monitoring on payroll-worker; notify_service_owner on payroll-worker | 46 s |
| BENCH-0088 | rate_limiting | rate_limiting | awaiting_approval | 0.65 | 1.0 | pause_job on invoicing-backfill; enable_rate_limiting on invoicing-worker; replay_failed_messages on invoicing-worker; notify_service_owner on invoicing-worker; add_monitoring on invoicing-worker | 55 s |
| BENCH-0089 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00689; replay_failed_messages on payments-processor; add_contract_test on payments-gateway; notify_service_owner on payments-gateway; add_monitoring on payments-processor | 43 s |
| BENCH-0090 | data_quality | data_quality | diagnosed | 0.75 | 1.0 | add_monitoring on catalogue-processor | 61 s |
| BENCH-0091 | networking | networking | diagnosed | 0.75 | 1.0 | add_monitoring on billing-worker | 52 s |
| BENCH-0092 | data_quality | data_quality | diagnosed | 0.65 | 1.0 | add_monitoring on claims-processor; notify_service_owner on claims-processor | 62 s |
| BENCH-0093 | authorisation | unknown | abstained | None | None | - | 20 s |
| BENCH-0094 | timeout | schema_contract_mismatch | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00730 | 33 s |
| BENCH-0095 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00739; replay_failed_messages on payments-worker; add_monitoring on payments-worker | 37 s |
| BENCH-0096 | rate_limiting | rate_limiting | awaiting_approval | 0.8 | 1.0 | enable_rate_limiting on accounts-worker; replay_failed_messages on accounts-worker; notify_service_owner on accounts-worker; add_monitoring on accounts-worker | 48 s |
| BENCH-0097 | timeout | deployment_or_configuration | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00756; notify_service_owner on subscriptions-db; add_monitoring on subscriptions-processor | 36 s |
| BENCH-0098 | queue_or_event_processing | unknown | abstained | None | None | - | 20 s |
| BENCH-0099 | networking | networking | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00773; replay_failed_messages on returns-processor; add_monitoring on returns-processor | 45 s |
| BENCH-0100 | unknown | unknown | abstained | None | None | - | 13 s |
| BENCH-0101 | unknown | unknown | abstained | None | None | - | 12 s |
| BENCH-0102 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00792; replay_failed_messages on bookings-processor; add_contract_test on bookings-gateway; notify_service_owner on bookings-gateway | 38 s |
| BENCH-0103 | file_transfer | schema_contract_mismatch | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-BILLING-00800; redeliver_file on billing-exporter; notify_service_owner on billing-exporter; add_monitoring on billing-exporter | 50 s |
| BENCH-0104 | queue_or_event_processing | unknown | abstained | None | None | - | 20 s |
| BENCH-0105 | data_quality | data_quality | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-00818; replay_failed_messages on settlements-processor; add_contract_test on settlements-gateway; notify_service_owner on settlements-gateway | 38 s |
| BENCH-0106 | unknown | unknown | abstained | None | None | - | 17 s |
| BENCH-0107 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00831; add_monitoring on payments-worker; notify_service_owner on payments-worker | 34 s |
| BENCH-0108 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-BILLING-00837; add_monitoring on billing-worker; notify_service_owner on billing-worker | 33 s |
| BENCH-0109 | authentication | authentication | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PROCUREMENT-00846; replay_failed_messages on procurement-worker; notify_service_owner on procurement-worker; add_monitoring on procurement-worker; add_contract_test on procurement-worker | 49 s |
| BENCH-0110 | authorisation | authorisation | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00854; replay_failed_messages on loyalty-worker; add_contract_test on loyalty-worker; notify_service_owner on loyalty-worker; add_monitoring on loyalty-worker | 44 s |

| Family | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| amounts_in_cents | 5 | 5 (100%) | 100% | 0 |
| backfill_burst | 5 | 5 (100%) | 100% | 0 |
| bad_feature_flag | 5 | 5 (100%) | 90% | 0 |
| consumers_scaled_down | 5 | 3 (60%) | 100% | 0 |
| database_name_change | 5 | 5 (100%) | 100% | 0 |
| dropped_index | 5 | 3 (60%) | 90% | 0 |
| duplicates_after_failover | 5 | 2 (40%) | 27% | 2 |
| encoding_change | 5 | 3 (60%) | 100% | 0 |
| expired_client_credential | 5 | 5 (100%) | 100% | 0 |
| intermittent_resets | 5 | 5 (100%) | n/a | 0 |
| missing_setting | 5 | 5 (100%) | 100% | 0 |
| narrowed_scope | 5 | 5 (100%) | 100% | 0 |
| partner_allowlist_change | 5 | 3 (60%) | 60% | 0 |
| pool_shrunk | 5 | 4 (80%) | 90% | 0 |
| provider_outage | 5 | 5 (100%) | 60% | 0 |
| quota_lowered | 5 | 5 (100%) | 100% | 0 |
| renamed_field | 5 | 5 (100%) | 80% | 0 |
| revoked_key_after_switch | 5 | 5 (100%) | 100% | 0 |
| sporadic_nulls | 5 | 5 (100%) | n/a | 0 |
| stale_reference_data | 5 | 4 (80%) | 80% | 0 |
| type_change | 5 | 5 (100%) | 67% | 0 |
| wrong_directory | 5 | 5 (100%) | 80% | 0 |

| Category | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| authentication | 10 | 10 (100%) | 100% | 0 |
| authorisation | 10 | 8 (80%) | 80% | 0 |
| data_quality | 10 | 9 (90%) | 90% | 0 |
| deployment_or_configuration | 10 | 10 (100%) | 95% | 0 |
| file_transfer | 10 | 8 (80%) | 90% | 0 |
| networking | 10 | 10 (100%) | 80% | 0 |
| queue_or_event_processing | 10 | 5 (50%) | 63% | 2 |
| rate_limiting | 10 | 10 (100%) | 100% | 0 |
| schema_contract_mismatch | 10 | 10 (100%) | 73% | 0 |
| timeout | 10 | 7 (70%) | 90% | 0 |
| unknown | 10 | 10 (100%) | n/a | 0 |

| Confidence | Answers | Right |
|---|---|---|
| 0.65 | 6 | 6 (100%) |
| 0.75 | 27 | 24 (89%) |
| 0.80 | 5 | 5 (100%) |
| 0.85 | 42 | 40 (95%) |
| 0.90 | 11 | 8 (73%) |
| 1.00 | 4 | 4 (100%) |

Steps refused by validation:

- BENCH-0005: replay_failed_messages on ledger-processor: must come after a step that fixes the cause
- BENCH-0005: rerun_job on ledger-processor: must come after a step that fixes the cause
- BENCH-0005: replay_failed_messages on ledger-processor: must come after a step that fixes the cause
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
- BENCH-0031: redeliver_file on rewards-exporter: must come after a step that fixes the cause
- BENCH-0053: replay_failed_messages on claims-worker: must come after a step that fixes the cause
- BENCH-0053: replay_failed_messages on claims-worker: must come after a step that fixes the cause
- BENCH-0062: replay_failed_messages on inventory-processor: must come after a step that fixes the cause
- BENCH-0068: redeliver_file on pricing-exporter: must come after a step that fixes the cause
- BENCH-0077: replay_failed_messages on inventory-worker: must come after a step that fixes the cause
- BENCH-0077: replay_failed_messages on inventory-worker: must come after a step that fixes the cause
- BENCH-0081: redeliver_file on billing-exporter: must come after a step that fixes the cause
- BENCH-0086: replay_failed_messages on ledger-worker: must come after a step that fixes the cause
- BENCH-0086: replay_failed_messages on ledger-worker: must come after a step that fixes the cause
- BENCH-0090: replay_failed_messages on catalogue-processor: must come after a step that fixes the cause
- BENCH-0090: rerun_job on catalogue-processor: must come after a step that fixes the cause
- BENCH-0090: replay_failed_messages on catalogue-processor: must come after a step that fixes the cause
- BENCH-0091: replay_failed_messages on billing-worker: must come after a step that fixes the cause
- BENCH-0091: replay_failed_messages on billing-worker: must come after a step that fixes the cause
- BENCH-0092: rerun_job on claims-processor: must come after a step that fixes the cause
- BENCH-0092: replay_failed_messages on claims-processor: must come after a step that fixes the cause
- BENCH-0092: rerun_job on claims-processor: must come after a step that fixes the cause
- BENCH-0092: replay_failed_messages on claims-processor: must come after a step that fixes the cause
- BENCH-0103: add_contract_test on billing-exporter: cites neither the root cause's evidence nor a runbook or past incident

Without logs: BENCH-0001 abstained, BENCH-0002 abstained, BENCH-0003 abstained, BENCH-0004 abstained, BENCH-0005 abstained, BENCH-0006 abstained, BENCH-0007 abstained, BENCH-0008 abstained, BENCH-0009 abstained, BENCH-0010 abstained, BENCH-0011 abstained, BENCH-0012 abstained, BENCH-0013 abstained, BENCH-0014 abstained, BENCH-0015 abstained, BENCH-0016 abstained, BENCH-0017 abstained, BENCH-0018 abstained, BENCH-0019 abstained, BENCH-0020 abstained, BENCH-0021 abstained, BENCH-0022 abstained, BENCH-0023 abstained, BENCH-0024 abstained, BENCH-0025 abstained, BENCH-0026 abstained, BENCH-0027 abstained, BENCH-0028 abstained, BENCH-0029 abstained, BENCH-0030 abstained, BENCH-0031 abstained, BENCH-0032 abstained, BENCH-0033 abstained, BENCH-0034 abstained, BENCH-0035 abstained, BENCH-0036 abstained, BENCH-0037 abstained, BENCH-0038 abstained, BENCH-0039 abstained, BENCH-0040 abstained, BENCH-0041 abstained, BENCH-0042 abstained, BENCH-0043 abstained, BENCH-0044 abstained, BENCH-0045 abstained, BENCH-0046 abstained, BENCH-0047 abstained, BENCH-0048 abstained, BENCH-0049 abstained, BENCH-0050 abstained, BENCH-0051 abstained, BENCH-0052 abstained, BENCH-0053 abstained, BENCH-0054 abstained, BENCH-0055 abstained, BENCH-0056 abstained, BENCH-0057 abstained, BENCH-0058 abstained, BENCH-0059 abstained, BENCH-0060 abstained, BENCH-0061 abstained, BENCH-0062 abstained, BENCH-0063 abstained, BENCH-0064 abstained, BENCH-0065 abstained, BENCH-0066 abstained, BENCH-0067 abstained, BENCH-0068 abstained, BENCH-0069 abstained, BENCH-0070 abstained, BENCH-0071 abstained, BENCH-0072 abstained, BENCH-0073 abstained, BENCH-0074 abstained, BENCH-0075 abstained, BENCH-0076 abstained, BENCH-0077 abstained, BENCH-0078 abstained, BENCH-0079 abstained, BENCH-0080 abstained, BENCH-0081 abstained, BENCH-0082 abstained, BENCH-0083 abstained, BENCH-0084 abstained, BENCH-0085 abstained, BENCH-0086 abstained, BENCH-0087 abstained, BENCH-0088 abstained, BENCH-0089 abstained, BENCH-0090 abstained, BENCH-0091 abstained, BENCH-0092 abstained, BENCH-0093 abstained, BENCH-0094 abstained, BENCH-0095 abstained, BENCH-0096 abstained, BENCH-0097 abstained, BENCH-0098 abstained, BENCH-0099 abstained, BENCH-0100 abstained, BENCH-0101 abstained, BENCH-0102 abstained, BENCH-0103 abstained, BENCH-0104 abstained, BENCH-0105 abstained, BENCH-0106 abstained, BENCH-0107 abstained, BENCH-0108 abstained, BENCH-0109 abstained, BENCH-0110 abstained.
