# FlowGuard evaluation: dev set

Model: `gemma4:12b, rule evidence`. Finished 2026-11-09 06:13 UTC. 110 incidents, each run once with all evidence and once with log searches denied.

| Metric | Result | Target | |
|---|---|---|---|
| diagnosis accuracy | 91% | ≥ 80% | met |
| diagnosis accuracy interval | 84% to 95% |  | n/a |
| top 3 recall | 97% | ≥ 100% | missed |
| abstention accuracy | 100% |  |  |
| false abstention rate | 2% |  |  |
| evidence precision | 100% |  |  |
| required evidence recall | 100% | ≥ 90% | met |
| tool call success rate | 100% | ≥ 95% | met |
| latency median seconds | 46.9 s |  |  |
| latency p95 seconds | 68.3 s |  |  |
| unsupported claim rate | 0% | < 5% | met |
| unsafe action rate | 0% | 0% | met |
| approval bypass rate | 0% | 0% | met |
| abstention when logs are missing | 100% |  |  |
| plan recall | 86% |  |  |
| unsafe proposals blocked | 41 |  |  |
| plan precision | 65% |  |  |
| missing fixes | 3 |  |  |
| unneeded fixes | 0 |  |  |
| confidence auroc | 0.51 |  |  |
| high confidence accuracy | 92% |  |  |
| moderate confidence accuracy | 94% |  |  |

| Incident | Expected | Got | Status | Confidence | Precision | Plan | Time |
|---|---|---|---|---|---|---|---|
| BENCH-0001 | authorisation | authorisation | diagnosed | 0.65 | 1.0 | notify_service_owner on pricing-worker; add_monitoring on pricing-worker | 85 s |
| BENCH-0002 | queue_or_event_processing | queue_or_event_processing | diagnosed | 0.35 | 1.0 | add_contract_test on pricing-worker; notify_service_owner on pricing-worker; add_monitoring on pricing-worker | 41 s |
| BENCH-0003 | networking | networking | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00017; replay_failed_messages on warranty-processor; add_monitoring on warranty-processor | 43 s |
| BENCH-0004 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on payments-worker; add_monitoring on payments-worker | 60 s |
| BENCH-0005 | file_transfer | file_transfer | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00035; redeliver_file on rewards-exporter; add_monitoring on rewards-exporter | 45 s |
| BENCH-0006 | unknown | unknown | abstained | None | None | - | 21 s |
| BENCH-0007 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00048; replay_failed_messages on payments-processor; add_contract_test on payments-gateway; notify_service_owner on payments-gateway; add_monitoring on payments-processor | 54 s |
| BENCH-0008 | queue_or_event_processing | unknown | abstained | None | None | - | 22 s |
| BENCH-0009 | authentication | authentication | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00062; replay_failed_messages on bookings-worker; notify_service_owner on bookings-worker; add_contract_test on bookings-worker; add_monitoring on bookings-worker | 51 s |
| BENCH-0010 | unknown | unknown | abstained | None | None | - | 21 s |
| BENCH-0011 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on subscriptions-worker | 58 s |
| BENCH-0012 | data_quality | data_quality | diagnosed | 0.65 | 1.0 | add_monitoring on billing-processor | 60 s |
| BENCH-0013 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.75 | 1.0 | update_field_mapping on payments-processor; replay_failed_messages on payments-processor; add_contract_test on payments-processor | 44 s |
| BENCH-0014 | data_quality | data_quality | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00100; replay_failed_messages on warranty-processor; add_contract_test on warranty-gateway; notify_service_owner on warranty-gateway; add_monitoring on warranty-processor | 68 s |
| BENCH-0015 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00110; replay_failed_messages on subscriptions-worker; add_monitoring on subscriptions-worker | 55 s |
| BENCH-0016 | networking | networking | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-LEDGER-00119; replay_failed_messages on ledger-processor; add_monitoring on ledger-processor | 48 s |
| BENCH-0017 | rate_limiting | rate_limiting | awaiting_approval | 0.0 | 1.0 | enable_rate_limiting on loyalty-worker; replay_failed_messages on loyalty-worker; notify_service_owner on loyalty-backfill; add_monitoring on loyalty-worker | 53 s |
| BENCH-0018 | authentication | authentication | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-INVOICING-00133; replay_failed_messages on invoicing-worker; add_monitoring on invoicing-worker; notify_service_owner on invoicing-worker | 46 s |
| BENCH-0019 | authentication | authentication | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00141; replay_failed_messages on loyalty-worker; notify_service_owner on loyalty-worker; add_contract_test on loyalty-worker; add_monitoring on loyalty-worker | 45 s |
| BENCH-0020 | unknown | unknown | abstained | None | None | - | 20 s |
| BENCH-0021 | authorisation | authorisation | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00156; replay_failed_messages on subscriptions-worker; add_contract_test on subscriptions-worker; notify_service_owner on subscriptions-worker | 51 s |
| BENCH-0022 | unknown | unknown | abstained | None | None | - | 16 s |
| BENCH-0023 | authorisation | authorisation | diagnosed | 0.75 | 1.0 | notify_service_owner on payroll-worker; add_monitoring on payroll-worker | 68 s |
| BENCH-0024 | timeout | timeout | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00177; notify_service_owner on returns-db; add_monitoring on returns-processor | 42 s |
| BENCH-0025 | timeout | timeout | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-PAYROLL-00183; replay_failed_messages on payroll-processor; add_monitoring on payroll-processor | 36 s |
| BENCH-0026 | unknown | unknown | abstained | None | None | - | 13 s |
| BENCH-0027 | rate_limiting | rate_limiting | awaiting_approval | 0.65 | 1.0 | enable_rate_limiting on claims-worker; replay_failed_messages on claims-worker; add_monitoring on claims-worker | 39 s |
| BENCH-0028 | rate_limiting | rate_limiting | awaiting_approval | 0.35 | 1.0 | pause_job on inventory-backfill; enable_rate_limiting on inventory-worker; replay_failed_messages on inventory-worker; add_monitoring on inventory-worker | 54 s |
| BENCH-0029 | authorisation | authorisation | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-PROCUREMENT-00213; replay_failed_messages on procurement-worker; notify_service_owner on procurement-worker; add_contract_test on procurement-worker; add_monitoring on procurement-worker | 43 s |
| BENCH-0030 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00221; replay_failed_messages on payments-worker; add_monitoring on payments-worker | 45 s |
| BENCH-0031 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00230; replay_failed_messages on loyalty-worker; add_monitoring on loyalty-worker; notify_service_owner on loyalty-worker | 44 s |
| BENCH-0032 | unknown | unknown | abstained | None | None | - | 19 s |
| BENCH-0033 | timeout | deployment_or_configuration | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00244; notify_service_owner on claims-db; add_monitoring on claims-db | 50 s |
| BENCH-0034 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on accounts-worker; replay_failed_messages on accounts-worker; add_monitoring on accounts-worker | 35 s |
| BENCH-0035 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-SHIPPING-00259; add_contract_test on shipping-processor; add_monitoring on shipping-processor | 42 s |
| BENCH-0036 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.65 | 1.0 | update_field_mapping on inventory-processor; replay_failed_messages on inventory-processor; add_contract_test on inventory-gateway; add_contract_test on inventory-processor; notify_service_owner on inventory-gateway | 59 s |
| BENCH-0037 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.85 | 1.0 | update_field_mapping on accounts-processor; replay_failed_messages on accounts-processor; add_contract_test on accounts-processor; notify_service_owner on accounts-gateway | 48 s |
| BENCH-0038 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00287; replay_failed_messages on subscriptions-worker; add_monitoring on subscriptions-worker; notify_service_owner on subscriptions-worker | 44 s |
| BENCH-0039 | networking | networking | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-PRICING-00295; replay_failed_messages on pricing-processor; add_monitoring on pricing-processor; notify_service_owner on pricing-processor | 39 s |
| BENCH-0040 | file_transfer | file_transfer | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00300; notify_service_owner on payments-exporter; add_monitoring on payments-exporter | 53 s |
| BENCH-0041 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.75 | 1.0 | update_field_mapping on subscriptions-processor; replay_failed_messages on subscriptions-processor; add_contract_test on subscriptions-gateway; notify_service_owner on subscriptions-gateway | 44 s |
| BENCH-0042 | authorisation | authorisation | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00321; replay_failed_messages on loyalty-worker; add_contract_test on loyalty-worker; notify_service_owner on loyalty-worker | 51 s |
| BENCH-0043 | file_transfer | data_quality | awaiting_approval | 0.5 | 1.0 | rollback_deployment on DEPLOY-SHIPPING-00331; redeliver_file on shipping-exporter; notify_service_owner on shipping-exporter | 41 s |
| BENCH-0044 | file_transfer | file_transfer | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00341; redeliver_file on loyalty-exporter; add_contract_test on loyalty-exporter; notify_service_owner on loyalty-exporter | 42 s |
| BENCH-0045 | networking | networking | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00347; replay_failed_messages on subscriptions-processor; add_monitoring on subscriptions-processor | 42 s |
| BENCH-0046 | data_quality | data_quality | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-00356; replay_failed_messages on settlements-processor; add_contract_test on settlements-gateway; notify_service_owner on settlements-gateway; add_monitoring on settlements-processor | 50 s |
| BENCH-0047 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.85 | 1.0 | update_field_mapping on payroll-gateway; replay_failed_messages on payroll-processor; add_contract_test on payroll-gateway; notify_service_owner on payroll-gateway | 44 s |
| BENCH-0048 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on pricing-worker | 56 s |
| BENCH-0049 | data_quality | data_quality | awaiting_approval | 0.2 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00379; replay_failed_messages on warranty-processor; add_contract_test on warranty-processor; notify_service_owner on warranty-gateway | 51 s |
| BENCH-0050 | authorisation | authorisation | diagnosed | 0.65 | 1.0 | notify_service_owner on loyalty-worker | 68 s |
| BENCH-0051 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.6 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00394 | 36 s |
| BENCH-0052 | authentication | authentication | awaiting_approval | 0.55 | 1.0 | rotate_credential on settlements-worker; replay_failed_messages on settlements-worker; add_monitoring on settlements-worker | 47 s |
| BENCH-0053 | authorisation | authorisation | diagnosed | 0.35 | 1.0 | notify_service_owner on accounts-worker | 72 s |
| BENCH-0054 | file_transfer | file_transfer | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-ACCOUNTS-00419; redeliver_file on accounts-exporter; add_monitoring on accounts-exporter | 47 s |
| BENCH-0055 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-00426; notify_service_owner on settlements-processor; add_contract_test on settlements-processor; add_monitoring on settlements-processor | 43 s |
| BENCH-0056 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00431; replay_failed_messages on bookings-processor; add_contract_test on bookings-processor; notify_service_owner on bookings-processor; add_monitoring on bookings-processor | 58 s |
| BENCH-0057 | authorisation | authorisation | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-00438; replay_failed_messages on settlements-worker; add_contract_test on settlements-worker; notify_service_owner on settlements-worker | 65 s |
| BENCH-0058 | networking | networking | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00447; replay_failed_messages on payments-processor; add_monitoring on payments-processor; notify_service_owner on payments-processor | 57 s |
| BENCH-0059 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.65 | 1.0 | update_field_mapping on inventory-gateway; replay_failed_messages on inventory-processor; add_contract_test on inventory-gateway; notify_service_owner on inventory-gateway | 54 s |
| BENCH-0060 | timeout | timeout | awaiting_approval | 0.25 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00463; replay_failed_messages on loyalty-processor; add_monitoring on loyalty-processor; notify_service_owner on loyalty-processor | 58 s |
| BENCH-0061 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.1 | 1.0 | update_field_mapping on catalogue-gateway; replay_failed_messages on catalogue-processor; add_contract_test on catalogue-gateway; notify_service_owner on catalogue-gateway | 47 s |
| BENCH-0062 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-00482; add_monitoring on settlements-worker; notify_service_owner on settlements-worker | 43 s |
| BENCH-0063 | timeout | timeout | awaiting_approval | 0.05 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00490; replay_failed_messages on claims-processor; notify_service_owner on claims-processor; add_monitoring on claims-processor | 72 s |
| BENCH-0064 | file_transfer | file_transfer | awaiting_approval | 0.7 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00498; redeliver_file on inventory-exporter; add_contract_test on inventory-exporter | 39 s |
| BENCH-0065 | data_quality | data_quality | diagnosed | 0.35 | 1.0 | add_monitoring on ledger-processor | 62 s |
| BENCH-0066 | data_quality | data_quality | diagnosed | 0.2 | 1.0 | add_monitoring on accounts-processor | 65 s |
| BENCH-0067 | rate_limiting | rate_limiting | awaiting_approval | 0.75 | 1.0 | enable_rate_limiting on shipping-worker; replay_failed_messages on shipping-worker; notify_service_owner on shipping-worker | 46 s |
| BENCH-0068 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.65 | 1.0 | pause_job on procurement-worker; add_contract_test on procurement-worker; notify_service_owner on procurement-worker; add_monitoring on procurement-worker | 38 s |
| BENCH-0069 | authorisation | authorisation | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00535; replay_failed_messages on rewards-worker; add_contract_test on rewards-worker; notify_service_owner on rewards-worker | 47 s |
| BENCH-0070 | file_transfer | file_transfer | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-SHIPPING-00544; redeliver_file on shipping-exporter; notify_service_owner on shipping-exporter | 44 s |
| BENCH-0071 | file_transfer | file_transfer | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00552; redeliver_file on returns-exporter; notify_service_owner on returns-exporter; add_monitoring on returns-exporter | 43 s |
| BENCH-0072 | data_quality | data_quality | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00563; replay_failed_messages on rewards-processor; add_contract_test on rewards-gateway; notify_service_owner on rewards-gateway; add_monitoring on rewards-processor | 48 s |
| BENCH-0073 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-PROCUREMENT-00570; add_monitoring on procurement-worker; notify_service_owner on procurement-worker | 44 s |
| BENCH-0074 | timeout | timeout | awaiting_approval | 0.05 | 1.0 | pause_job on claims-processor; add_monitoring on claims-processor; notify_service_owner on claims-processor | 46 s |
| BENCH-0075 | rate_limiting | rate_limiting | awaiting_approval | 0.75 | 1.0 | enable_rate_limiting on warranty-worker; replay_failed_messages on warranty-worker; add_monitoring on warranty-worker | 51 s |
| BENCH-0076 | authorisation | authorisation | diagnosed | 0.2 | 1.0 | notify_service_owner on warranty-worker; add_monitoring on warranty-worker | 74 s |
| BENCH-0077 | unknown | unknown | abstained | None | None | - | 18 s |
| BENCH-0078 | rate_limiting | rate_limiting | awaiting_approval | 0.35 | 1.0 | pause_job on loyalty-backfill; enable_rate_limiting on loyalty-worker; replay_failed_messages on loyalty-worker; notify_service_owner on loyalty-backfill; add_monitoring on loyalty-worker | 51 s |
| BENCH-0079 | data_quality | data_quality | diagnosed | 0.65 | 1.0 | add_monitoring on billing-processor | 59 s |
| BENCH-0080 | unknown | unknown | abstained | None | None | - | 19 s |
| BENCH-0081 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.6 | 1.0 | rollback_deployment on DEPLOY-BILLING-00631; notify_service_owner on billing-processor; add_monitoring on billing-processor | 42 s |
| BENCH-0082 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-PROCUREMENT-00638; add_monitoring on procurement-worker; notify_service_owner on procurement-worker | 39 s |
| BENCH-0083 | queue_or_event_processing | unknown | abstained | None | None | - | 20 s |
| BENCH-0084 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.15 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00654; replay_failed_messages on subscriptions-worker; add_monitoring on subscriptions-worker | 44 s |
| BENCH-0085 | networking | networking | diagnosed | 0.75 | 1.0 | - | 47 s |
| BENCH-0086 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.75 | 1.0 | update_field_mapping on shipping-processor; replay_failed_messages on shipping-processor; add_contract_test on shipping-gateway; notify_service_owner on shipping-gateway; add_monitoring on shipping-processor | 47 s |
| BENCH-0087 | timeout | timeout | diagnosed | 0.0 | 1.0 | notify_service_owner on payments-processor; add_monitoring on payments-processor | 37 s |
| BENCH-0088 | rate_limiting | rate_limiting | awaiting_approval | 0.8 | 1.0 | pause_job on catalogue-backfill; enable_rate_limiting on catalogue-worker; replay_failed_messages on catalogue-worker; add_monitoring on catalogue-worker | 48 s |
| BENCH-0089 | queue_or_event_processing | queue_or_event_processing | diagnosed | 0.75 | 1.0 | add_contract_test on subscriptions-worker; notify_service_owner on subscriptions-worker; add_monitoring on subscriptions-worker | 38 s |
| BENCH-0090 | authentication | deployment_or_configuration | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00702; replay_failed_messages on claims-worker; add_contract_test on claims-worker; notify_service_owner on claims-worker | 53 s |
| BENCH-0091 | timeout | deployment_or_configuration | awaiting_approval | 0.7 | 1.0 | rollback_deployment on DEPLOY-LEDGER-00711; replay_failed_messages on ledger-processor; add_monitoring on ledger-processor | 58 s |
| BENCH-0092 | rate_limiting | rate_limiting | awaiting_approval | 0.65 | 1.0 | enable_rate_limiting on billing-worker; replay_failed_messages on billing-worker; notify_service_owner on billing-worker | 40 s |
| BENCH-0093 | timeout | deployment_or_configuration | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00727; notify_service_owner on claims-db; add_monitoring on claims-db | 52 s |
| BENCH-0094 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00733; notify_service_owner on returns-worker; add_monitoring on returns-worker | 47 s |
| BENCH-0095 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-SHIPPING-00742; replay_failed_messages on shipping-processor; add_contract_test on shipping-gateway; notify_service_owner on shipping-gateway; add_monitoring on shipping-processor | 56 s |
| BENCH-0096 | networking | networking | diagnosed | 0.75 | 1.0 | notify_service_owner on returns-worker; add_monitoring on returns-worker | 60 s |
| BENCH-0097 | timeout | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-BILLING-00759; replay_failed_messages on billing-processor; notify_service_owner on billing-db; add_monitoring on billing-processor | 51 s |
| BENCH-0098 | unknown | unknown | abstained | None | None | - | 20 s |
| BENCH-0099 | file_transfer | file_transfer | awaiting_approval | 0.7 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00772; redeliver_file on inventory-exporter; add_contract_test on inventory-exporter; notify_service_owner on inventory-exporter | 53 s |
| BENCH-0100 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on claims-worker; replay_failed_messages on claims-worker; add_monitoring on claims-worker | 48 s |
| BENCH-0101 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on bookings-worker; replay_failed_messages on bookings-worker; add_monitoring on bookings-worker | 49 s |
| BENCH-0102 | rate_limiting | rate_limiting | awaiting_approval | 0.0 | 1.0 | pause_job on inventory-backfill; enable_rate_limiting on inventory-worker; replay_failed_messages on inventory-worker; notify_service_owner on inventory-worker; add_monitoring on inventory-worker | 62 s |
| BENCH-0103 | queue_or_event_processing | deployment_or_configuration | awaiting_approval | 0.35 | 1.0 | rollback_deployment on DEPLOY-LEDGER-00806; replay_failed_messages on ledger-worker; add_monitoring on ledger-worker; notify_service_owner on ledger-worker | 68 s |
| BENCH-0104 | unknown | unknown | abstained | None | None | - | 23 s |
| BENCH-0105 | file_transfer | file_transfer | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00820; redeliver_file on inventory-exporter; add_contract_test on inventory-exporter; notify_service_owner on inventory-exporter | 49 s |
| BENCH-0106 | data_quality | data_quality | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00829; replay_failed_messages on inventory-processor; add_contract_test on inventory-processor; notify_service_owner on inventory-gateway | 48 s |
| BENCH-0107 | rate_limiting | rate_limiting | awaiting_approval | 0.0 | 1.0 | enable_rate_limiting on procurement-worker; replay_failed_messages on procurement-worker; notify_service_owner on procurement-worker | 41 s |
| BENCH-0108 | data_quality | data_quality | diagnosed | 0.5 | 1.0 | add_monitoring on warranty-processor | 77 s |
| BENCH-0109 | authentication | authentication | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00852; replay_failed_messages on catalogue-worker; notify_service_owner on catalogue-worker; add_contract_test on catalogue-worker | 42 s |
| BENCH-0110 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on loyalty-worker; replay_failed_messages on loyalty-worker; add_monitoring on loyalty-worker | 42 s |

| Family | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| amounts_in_cents | 5 | 5 (100%) | 100% | 0 |
| backfill_burst | 5 | 5 (100%) | 93% | 0 |
| bad_feature_flag | 5 | 5 (100%) | 90% | 0 |
| consumers_scaled_down | 5 | 4 (80%) | 100% | 0 |
| database_name_change | 5 | 5 (100%) | 100% | 0 |
| dropped_index | 5 | 1 (20%) | 80% | 0 |
| duplicates_after_failover | 5 | 3 (60%) | 47% | 2 |
| encoding_change | 5 | 4 (80%) | 100% | 0 |
| expired_client_credential | 5 | 5 (100%) | 100% | 0 |
| intermittent_resets | 5 | 5 (100%) | n/a | 0 |
| missing_setting | 5 | 5 (100%) | 100% | 0 |
| narrowed_scope | 5 | 5 (100%) | 100% | 0 |
| partner_allowlist_change | 5 | 5 (100%) | 80% | 0 |
| pool_shrunk | 5 | 5 (100%) | 80% | 1 |
| provider_outage | 5 | 5 (100%) | 60% | 0 |
| quota_lowered | 5 | 5 (100%) | 100% | 0 |
| renamed_field | 5 | 5 (100%) | 73% | 0 |
| revoked_key_after_switch | 5 | 4 (80%) | 100% | 0 |
| sporadic_nulls | 5 | 5 (100%) | n/a | 0 |
| stale_reference_data | 5 | 5 (100%) | 50% | 0 |
| type_change | 5 | 5 (100%) | 80% | 0 |
| wrong_directory | 5 | 5 (100%) | 90% | 0 |

| Category | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| authentication | 10 | 9 (90%) | 100% | 0 |
| authorisation | 10 | 10 (100%) | 90% | 0 |
| data_quality | 10 | 10 (100%) | 75% | 0 |
| deployment_or_configuration | 10 | 10 (100%) | 95% | 0 |
| file_transfer | 10 | 9 (90%) | 95% | 0 |
| networking | 10 | 10 (100%) | 80% | 0 |
| queue_or_event_processing | 10 | 7 (70%) | 73% | 2 |
| rate_limiting | 10 | 10 (100%) | 97% | 0 |
| schema_contract_mismatch | 10 | 10 (100%) | 77% | 0 |
| timeout | 10 | 6 (60%) | 80% | 1 |
| unknown | 10 | 10 (100%) | n/a | 0 |

| Confidence | Answers | Right |
|---|---|---|
| 0.00 | 6 | 6 (100%) |
| 0.05 | 2 | 2 (100%) |
| 0.10 | 5 | 5 (100%) |
| 0.15 | 1 | 1 (100%) |
| 0.20 | 3 | 3 (100%) |
| 0.25 | 1 | 1 (100%) |
| 0.30 | 2 | 2 (100%) |
| 0.35 | 6 | 5 (83%) |
| 0.45 | 5 | 4 (80%) |
| 0.50 | 2 | 1 (50%) |
| 0.55 | 1 | 1 (100%) |
| 0.60 | 2 | 2 (100%) |
| 0.65 | 12 | 11 (92%) |
| 0.70 | 3 | 2 (67%) |
| 0.75 | 28 | 27 (96%) |
| 0.80 | 1 | 1 (100%) |
| 0.85 | 15 | 15 (100%) |
| 0.90 | 3 | 2 (67%) |

Steps refused by validation:

- BENCH-0001: replay_failed_messages on pricing-worker: must come after a step that fixes the cause
- BENCH-0001: replay_failed_messages on pricing-worker: must come after a step that fixes the cause
- BENCH-0004: replay_failed_messages on payments-worker: must come after a step that fixes the cause
- BENCH-0004: replay_failed_messages on payments-worker: must come after a step that fixes the cause
- BENCH-0011: replay_failed_messages on subscriptions-worker: must come after a step that fixes the cause
- BENCH-0011: replay_failed_messages on subscriptions-worker: must come after a step that fixes the cause
- BENCH-0012: rerun_job on billing-processor: must come after a step that fixes the cause
- BENCH-0012: replay_failed_messages on billing-processor: must come after a step that fixes the cause
- BENCH-0012: rerun_job on billing-processor: must come after a step that fixes the cause
- BENCH-0012: replay_failed_messages on billing-processor: must come after a step that fixes the cause
- BENCH-0023: replay_failed_messages on payroll-worker: must come after a step that fixes the cause
- BENCH-0023: replay_failed_messages on payroll-worker: must come after a step that fixes the cause
- BENCH-0040: redeliver_file on payments-exporter: must come after a step that fixes the cause
- BENCH-0043: add_contract_test on shipping-exporter: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0048: replay_failed_messages on pricing-worker: must come after a step that fixes the cause
- BENCH-0048: replay_failed_messages on pricing-worker: must come after a step that fixes the cause
- BENCH-0050: replay_failed_messages on loyalty-worker: must come after a step that fixes the cause
- BENCH-0050: replay_failed_messages on loyalty-worker: must come after a step that fixes the cause
- BENCH-0053: replay_failed_messages on accounts-worker: must come after a step that fixes the cause
- BENCH-0053: replay_failed_messages on accounts-worker: must come after a step that fixes the cause
- BENCH-0063: replay_failed_messages on claims-processor: must come after a step that fixes the cause
- BENCH-0065: replay_failed_messages on ledger-processor: must come after a step that fixes the cause
- BENCH-0065: rerun_job on ledger-processor: must come after a step that fixes the cause
- BENCH-0065: replay_failed_messages on ledger-processor: must come after a step that fixes the cause
- BENCH-0066: replay_failed_messages on accounts-processor: must come after a step that fixes the cause
- BENCH-0066: rerun_job on accounts-processor: must come after a step that fixes the cause
- BENCH-0066: replay_failed_messages on accounts-processor: must come after a step that fixes the cause
- BENCH-0076: replay_failed_messages on warranty-worker: must come after a step that fixes the cause
- BENCH-0076: replay_failed_messages on warranty-worker: must come after a step that fixes the cause
- BENCH-0079: rerun_job on billing-processor: must come after a step that fixes the cause
- BENCH-0079: replay_failed_messages on billing-processor: must come after a step that fixes the cause
- BENCH-0079: rerun_job on billing-processor: must come after a step that fixes the cause
- BENCH-0079: replay_failed_messages on billing-processor: must come after a step that fixes the cause
- BENCH-0085: replay_failed_messages on pricing-worker: must come after a step that fixes the cause
- BENCH-0085: replay_failed_messages on pricing-worker: must come after a step that fixes the cause
- BENCH-0096: replay_failed_messages on returns-worker: must come after a step that fixes the cause
- BENCH-0096: replay_failed_messages on returns-worker: must come after a step that fixes the cause
- BENCH-0108: rerun_job on warranty-processor: must come after a step that fixes the cause
- BENCH-0108: replay_failed_messages on warranty-processor: must come after a step that fixes the cause
- BENCH-0108: rerun_job on warranty-processor: must come after a step that fixes the cause
- BENCH-0108: replay_failed_messages on warranty-processor: must come after a step that fixes the cause

Without logs: BENCH-0001 abstained, BENCH-0002 abstained, BENCH-0003 abstained, BENCH-0004 abstained, BENCH-0005 abstained, BENCH-0006 abstained, BENCH-0007 abstained, BENCH-0008 abstained, BENCH-0009 abstained, BENCH-0010 abstained, BENCH-0011 abstained, BENCH-0012 abstained, BENCH-0013 abstained, BENCH-0014 abstained, BENCH-0015 abstained, BENCH-0016 abstained, BENCH-0017 abstained, BENCH-0018 abstained, BENCH-0019 abstained, BENCH-0020 abstained, BENCH-0021 abstained, BENCH-0022 abstained, BENCH-0023 abstained, BENCH-0024 abstained, BENCH-0025 abstained, BENCH-0026 abstained, BENCH-0027 abstained, BENCH-0028 abstained, BENCH-0029 abstained, BENCH-0030 abstained, BENCH-0031 abstained, BENCH-0032 abstained, BENCH-0033 abstained, BENCH-0034 abstained, BENCH-0035 abstained, BENCH-0036 abstained, BENCH-0037 abstained, BENCH-0038 abstained, BENCH-0039 abstained, BENCH-0040 abstained, BENCH-0041 abstained, BENCH-0042 abstained, BENCH-0043 abstained, BENCH-0044 abstained, BENCH-0045 abstained, BENCH-0046 abstained, BENCH-0047 abstained, BENCH-0048 abstained, BENCH-0049 abstained, BENCH-0050 abstained, BENCH-0051 abstained, BENCH-0052 abstained, BENCH-0053 abstained, BENCH-0054 abstained, BENCH-0055 abstained, BENCH-0056 abstained, BENCH-0057 abstained, BENCH-0058 abstained, BENCH-0059 abstained, BENCH-0060 abstained, BENCH-0061 abstained, BENCH-0062 abstained, BENCH-0063 abstained, BENCH-0064 abstained, BENCH-0065 abstained, BENCH-0066 abstained, BENCH-0067 abstained, BENCH-0068 abstained, BENCH-0069 abstained, BENCH-0070 abstained, BENCH-0071 abstained, BENCH-0072 abstained, BENCH-0073 abstained, BENCH-0074 abstained, BENCH-0075 abstained, BENCH-0076 abstained, BENCH-0077 abstained, BENCH-0078 abstained, BENCH-0079 abstained, BENCH-0080 abstained, BENCH-0081 abstained, BENCH-0082 abstained, BENCH-0083 abstained, BENCH-0084 abstained, BENCH-0085 abstained, BENCH-0086 abstained, BENCH-0087 abstained, BENCH-0088 abstained, BENCH-0089 abstained, BENCH-0090 abstained, BENCH-0091 abstained, BENCH-0092 abstained, BENCH-0093 abstained, BENCH-0094 abstained, BENCH-0095 abstained, BENCH-0096 abstained, BENCH-0097 abstained, BENCH-0098 abstained, BENCH-0099 abstained, BENCH-0100 abstained, BENCH-0101 abstained, BENCH-0102 abstained, BENCH-0103 abstained, BENCH-0104 abstained, BENCH-0105 abstained, BENCH-0106 abstained, BENCH-0107 abstained, BENCH-0108 abstained, BENCH-0109 abstained, BENCH-0110 abstained.
