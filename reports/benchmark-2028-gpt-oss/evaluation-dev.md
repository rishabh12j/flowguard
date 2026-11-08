# FlowGuard evaluation: dev set

Model: `gpt-oss:20b, reasoning low`. Finished 2026-11-07 13:16 UTC. 110 incidents, each run once with all evidence and once with log searches denied.

| Metric | Result | Target | |
|---|---|---|---|
| diagnosis accuracy | 53% | ≥ 80% | missed |
| diagnosis accuracy interval | 43% to 62% |  | n/a |
| top 3 recall | 90% | ≥ 100% | missed |
| abstention accuracy | 100% |  |  |
| false abstention rate | 13% |  |  |
| evidence precision | 99% |  |  |
| required evidence recall | 100% | ≥ 90% | met |
| tool call success rate | 100% | ≥ 95% | met |
| latency median seconds | 38.4 s |  |  |
| latency p95 seconds | 57.4 s |  |  |
| unsupported claim rate | 0% | < 5% | met |
| unsafe action rate | 0% | 0% | met |
| approval bypass rate | 0% | 0% | met |
| abstention when logs are missing | 100% |  |  |
| plan recall | 74% |  |  |
| unsafe proposals blocked | 69 |  |  |
| plan precision | 52% |  |  |
| missing fixes | 0 |  |  |
| unneeded fixes | 3 |  |  |
| confidence auroc | 0.56 |  |  |
| high confidence accuracy | 69% |  |  |
| moderate confidence accuracy | 57% |  |  |

| Incident | Expected | Got | Status | Confidence | Precision | Plan | Time |
|---|---|---|---|---|---|---|---|
| BENCH-0001 | unknown | unknown | abstained | None | None | - | 46 s |
| BENCH-0002 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00006; notify_service_owner on rewards-worker; add_contract_test on rewards-worker; add_monitoring on rewards-worker | 45 s |
| BENCH-0003 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.75 | 1.0 | update_field_mapping on invoicing-processor; replay_failed_messages on invoicing-processor; add_contract_test on invoicing-processor; notify_service_owner on invoicing-processor | 47 s |
| BENCH-0004 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.65 | 1.0 | update_field_mapping on pricing-processor; add_contract_test on pricing-processor; replay_failed_messages on pricing-processor; notify_service_owner on pricing-processor; add_monitoring on pricing-processor | 54 s |
| BENCH-0005 | data_quality | unknown | abstained | None | None | - | 18 s |
| BENCH-0006 | rate_limiting | rate_limiting | awaiting_approval | 0.35 | 1.0 | enable_rate_limiting on payments-worker; add_monitoring on payments-worker; replay_failed_messages on payments-worker; notify_service_owner on payments-worker | 40 s |
| BENCH-0007 | file_transfer | deployment_or_configuration | awaiting_approval | 0.8 | 1.0 | rollback_deployment on DEPLOY-INVOICING-00044; add_contract_test on invoicing-exporter; notify_service_owner on invoicing-exporter; add_monitoring on invoicing-exporter | 57 s |
| BENCH-0008 | file_transfer | file_transfer | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00051; redeliver_file on onboarding-exporter; add_contract_test on onboarding-exporter; notify_service_owner on onboarding-exporter | 51 s |
| BENCH-0009 | networking | deployment_or_configuration | awaiting_approval | 0.55 | 1.0 | rollback_deployment on DEPLOY-PRICING-00059; add_contract_test on pricing-processor; add_monitoring on pricing-processor; notify_service_owner on pricing-processor | 43 s |
| BENCH-0010 | networking | deployment_or_configuration | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00068; add_contract_test on rewards-processor; add_monitoring on rewards-processor; notify_service_owner on rewards-processor | 35 s |
| BENCH-0011 | unknown | unknown | abstained | None | None | - | 28 s |
| BENCH-0012 | authentication | authentication | awaiting_approval | 0.65 | 1.0 | rotate_credential on warranty-worker; notify_service_owner on warranty-worker; add_monitoring on warranty-worker | 53 s |
| BENCH-0013 | timeout | deployment_or_configuration | awaiting_approval | 0.4 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00084; add_monitoring on onboarding-processor; notify_service_owner on onboarding-processor; add_contract_test on onboarding-processor | 40 s |
| BENCH-0014 | rate_limiting | rate_limiting | awaiting_approval | 0.35 | 1.0 | enable_rate_limiting on loyalty-worker; notify_service_owner on loyalty-worker; add_contract_test on loyalty-worker; add_monitoring on loyalty-worker | 45 s |
| BENCH-0015 | authorisation | networking | diagnosed | 0.0 | 1.0 | notify_service_owner on catalogue-worker; add_monitoring on catalogue-worker | 73 s |
| BENCH-0016 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.35 | 1.0 | rollback_deployment on DEPLOY-SHIPPING-00110; update_field_mapping on shipping-processor; replay_failed_messages on shipping-processor; add_contract_test on shipping-processor; notify_service_owner on shipping-processor | 55 s |
| BENCH-0017 | authentication | authentication | awaiting_approval | 0.75 | 1.0 | rotate_credential on returns-worker; replay_failed_messages on returns-worker; notify_service_owner on returns-worker; add_monitoring on returns-worker | 38 s |
| BENCH-0018 | authorisation | authorisation | diagnosed | 0.35 | 1.0 | notify_service_owner on accounts-worker; add_monitoring on accounts-worker | 59 s |
| BENCH-0019 | networking | networking | diagnosed | 0.3 | 1.0 | notify_service_owner on warranty-worker; add_monitoring on warranty-worker | 60 s |
| BENCH-0020 | authorisation | deployment_or_configuration | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-SHIPPING-00141; replay_failed_messages on shipping-worker; add_contract_test on shipping-worker; notify_service_owner on shipping-worker; add_monitoring on shipping-worker | 39 s |
| BENCH-0021 | data_quality | data_quality | diagnosed | 0.4 | 1.0 | notify_service_owner on pricing-processor; add_monitoring on pricing-processor | 53 s |
| BENCH-0022 | data_quality | deployment_or_configuration | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00159; replay_failed_messages on onboarding-processor; add_contract_test on onboarding-processor; add_monitoring on onboarding-processor; notify_service_owner on onboarding-processor | 37 s |
| BENCH-0023 | networking | deployment_or_configuration | awaiting_approval | 0.3 | 0.75 | rollback_deployment on DEPLOY-BILLING-00167; notify_service_owner on billing-worker | 38 s |
| BENCH-0024 | unknown | unknown | abstained | None | None | - | 14 s |
| BENCH-0025 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00178; notify_service_owner on rewards-worker; add_monitoring on rewards-worker | 35 s |
| BENCH-0026 | timeout | timeout | awaiting_approval | 0.05 | 0.8 | add_monitoring on billing-processor; enable_rate_limiting on billing-processor; add_contract_test on billing-processor; notify_service_owner on billing-processor | 44 s |
| BENCH-0027 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00195; add_contract_test on subscriptions-processor; notify_service_owner on subscriptions-processor; add_monitoring on subscriptions-processor | 48 s |
| BENCH-0028 | data_quality | unknown | abstained | None | None | - | 17 s |
| BENCH-0029 | queue_or_event_processing | deployment_or_configuration | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00211; add_monitoring on loyalty-worker; notify_service_owner on loyalty-worker; enable_rate_limiting on loyalty-worker | 47 s |
| BENCH-0030 | timeout | deployment_or_configuration | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-PAYROLL-00219; add_monitoring on payroll-processor | 36 s |
| BENCH-0031 | file_transfer | deployment_or_configuration | awaiting_approval | 0.35 | 1.0 | rollback_deployment on DEPLOY-REWARDS-00228; redeliver_file on rewards-exporter; add_monitoring on rewards-exporter; notify_service_owner on rewards-exporter | 43 s |
| BENCH-0032 | data_quality | deployment_or_configuration | awaiting_approval | 0.6 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00236; replay_failed_messages on subscriptions-processor; add_contract_test on subscriptions-processor; notify_service_owner on subscriptions-gateway; add_monitoring on subscriptions-processor | 41 s |
| BENCH-0033 | networking | deployment_or_configuration | awaiting_approval | 0.55 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00246; add_monitoring on warranty-processor; notify_service_owner on warranty-processor | 37 s |
| BENCH-0034 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.6 | 1.0 | rollback_deployment on DEPLOY-PRICING-00256; add_contract_test on pricing-processor; notify_service_owner on pricing-processor; add_monitoring on pricing-processor | 38 s |
| BENCH-0035 | queue_or_event_processing | networking | awaiting_approval | 0.25 | 1.0 | pause_job on invoicing-worker; add_monitoring on invoicing-worker; notify_service_owner on invoicing-worker | 33 s |
| BENCH-0036 | queue_or_event_processing | unknown | abstained | None | None | - | 17 s |
| BENCH-0037 | authentication | authentication | awaiting_approval | 0.35 | 1.0 | rotate_credential on subscriptions-worker; replay_failed_messages on subscriptions-worker; add_monitoring on subscriptions-worker; notify_service_owner on subscriptions-worker | 31 s |
| BENCH-0038 | authentication | authentication | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00285; rotate_credential on onboarding-worker; add_contract_test on onboarding-worker; add_monitoring on onboarding-worker | 42 s |
| BENCH-0039 | authorisation | authorisation | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00293; replay_failed_messages on catalogue-worker; add_contract_test on catalogue-worker; notify_service_owner on catalogue-worker | 36 s |
| BENCH-0040 | unknown | unknown | abstained | None | None | - | 15 s |
| BENCH-0041 | timeout | timeout | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00305; add_monitoring on loyalty-processor; notify_service_owner on loyalty-processor; add_contract_test on loyalty-processor | 41 s |
| BENCH-0042 | authentication | authentication | awaiting_approval | 0.65 | 1.0 | rotate_credential on warranty-worker; replay_failed_messages on warranty-worker; notify_service_owner on warranty-worker; add_monitoring on warranty-worker | 37 s |
| BENCH-0043 | schema_contract_mismatch | unknown | abstained | None | None | - | 19 s |
| BENCH-0044 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00328; notify_service_owner on subscriptions-worker; add_monitoring on subscriptions-worker; add_contract_test on subscriptions-worker | 33 s |
| BENCH-0045 | rate_limiting | rate_limiting | awaiting_approval | 0.3 | 1.0 | enable_rate_limiting on claims-worker; notify_service_owner on claims-worker; add_monitoring on claims-worker | 31 s |
| BENCH-0046 | networking | deployment_or_configuration | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-WARRANTY-00346; add_monitoring on warranty-processor; notify_service_owner on warranty-processor | 29 s |
| BENCH-0047 | authorisation | deployment_or_configuration | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-CATALOGUE-00351; replay_failed_messages on catalogue-worker; add_contract_test on catalogue-worker; add_monitoring on catalogue-worker; notify_service_owner on catalogue-worker | 35 s |
| BENCH-0048 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-PROCUREMENT-00359; update_field_mapping on procurement-processor; replay_failed_messages on procurement-processor; add_contract_test on procurement-processor; notify_service_owner on procurement-processor | 45 s |
| BENCH-0049 | authorisation | authorisation | diagnosed | 0.35 | 1.0 | notify_service_owner on payments-worker; add_monitoring on payments-worker; add_contract_test on payments-worker | 54 s |
| BENCH-0050 | file_transfer | file_transfer | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00374; redeliver_file on bookings-exporter; notify_service_owner on bookings-exporter; add_monitoring on bookings-exporter | 33 s |
| BENCH-0051 | timeout | deployment_or_configuration | awaiting_approval | 0.4 | 1.0 | rollback_deployment on DEPLOY-BILLING-00384; add_monitoring on billing-processor; notify_service_owner on billing-processor; add_contract_test on billing-processor | 39 s |
| BENCH-0052 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.6 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00390; add_contract_test on returns-processor; notify_service_owner on returns-processor; add_monitoring on returns-processor | 46 s |
| BENCH-0053 | networking | unknown | abstained | None | None | - | 14 s |
| BENCH-0054 | file_transfer | deployment_or_configuration | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00406; redeliver_file on payments-exporter; add_contract_test on payments-exporter; notify_service_owner on payments-exporter; add_monitoring on payments-exporter | 35 s |
| BENCH-0055 | rate_limiting | rate_limiting | awaiting_approval | 0.0 | 1.0 | enable_rate_limiting on invoicing-worker; notify_service_owner on invoicing-worker; replay_failed_messages on invoicing-worker | 38 s |
| BENCH-0056 | data_quality | unknown | abstained | None | None | - | 19 s |
| BENCH-0057 | timeout | deployment_or_configuration | awaiting_approval | 0.65 | 1.0 | rollback_deployment on DEPLOY-LEDGER-00429; notify_service_owner on ledger-processor; replay_failed_messages on ledger-processor | 41 s |
| BENCH-0058 | timeout | deployment_or_configuration | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00438; update_field_mapping on claims-processor; add_monitoring on claims-processor; replay_failed_messages on claims-processor | 38 s |
| BENCH-0059 | queue_or_event_processing | deployment_or_configuration | awaiting_approval | 0.4 | 1.0 | rollback_deployment on DEPLOY-PRICING-00448; update_field_mapping on pricing-worker; replay_failed_messages on pricing-worker; add_monitoring on pricing-worker | 43 s |
| BENCH-0060 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.45 | 1.0 | update_field_mapping on invoicing-processor; notify_service_owner on invoicing-processor; add_contract_test on invoicing-processor; replay_failed_messages on invoicing-processor; add_monitoring on invoicing-processor | 50 s |
| BENCH-0061 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-BILLING-00468; replay_failed_messages on billing-processor; add_contract_test on billing-processor; notify_service_owner on billing-processor; add_monitoring on billing-processor | 38 s |
| BENCH-0062 | timeout | deployment_or_configuration | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00479; enable_rate_limiting on inventory-processor; add_monitoring on inventory-processor; notify_service_owner on inventory-processor; replay_failed_messages on inventory-processor | 47 s |
| BENCH-0063 | rate_limiting | rate_limiting | awaiting_approval | 0.35 | 1.0 | pause_job on onboarding-backfill; enable_rate_limiting on onboarding-worker; replay_failed_messages on onboarding-worker; add_contract_test on onboarding-worker; notify_service_owner on onboarding-worker | 39 s |
| BENCH-0064 | authorisation | authorisation | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-CLAIMS-00495; replay_failed_messages on claims-worker; add_contract_test on claims-worker; notify_service_owner on claims-worker; add_monitoring on claims-worker | 41 s |
| BENCH-0065 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.6 | 1.0 | rollback_deployment on DEPLOY-PRICING-00501; add_contract_test on pricing-processor; notify_service_owner on pricing-processor; add_monitoring on pricing-processor | 39 s |
| BENCH-0066 | rate_limiting | unknown | abstained | None | None | - | 15 s |
| BENCH-0067 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.75 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00516; notify_service_owner on subscriptions-processor; add_monitoring on subscriptions-processor | 39 s |
| BENCH-0068 | file_transfer | unknown | abstained | None | None | - | 17 s |
| BENCH-0069 | authentication | authentication | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-00534; rotate_credential on settlements-worker; replay_failed_messages on settlements-worker; add_contract_test on settlements-worker; add_monitoring on settlements-worker | 42 s |
| BENCH-0070 | queue_or_event_processing | queue_or_event_processing | awaiting_approval | 0.35 | 1.0 | add_contract_test on billing-worker; add_monitoring on billing-worker; notify_service_owner on billing-worker; enable_rate_limiting on billing-worker | 57 s |
| BENCH-0071 | queue_or_event_processing | deployment_or_configuration | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-ONBOARDING-00551; add_monitoring on onboarding-worker; enable_rate_limiting on onboarding-worker; notify_service_owner on onboarding-worker | 39 s |
| BENCH-0072 | data_quality | schema_contract_mismatch | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00558; notify_service_owner on loyalty-processor; replay_failed_messages on loyalty-processor; add_contract_test on loyalty-processor; add_monitoring on loyalty-processor | 34 s |
| BENCH-0073 | queue_or_event_processing | unknown | abstained | None | None | - | 18 s |
| BENCH-0074 | file_transfer | unknown | abstained | None | None | - | 22 s |
| BENCH-0075 | authentication | authentication | awaiting_approval | 0.65 | 1.0 | rotate_credential on procurement-worker; replay_failed_messages on procurement-worker; notify_service_owner on procurement-worker; add_monitoring on procurement-worker | 37 s |
| BENCH-0076 | unknown | unknown | abstained | None | None | - | 16 s |
| BENCH-0077 | networking | networking | diagnosed | 0.45 | 1.0 | notify_service_owner on inventory-worker; add_monitoring on inventory-worker | 48 s |
| BENCH-0078 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.0 | 1.0 | update_field_mapping on accounts-gateway; replay_failed_messages on accounts-processor; add_contract_test on accounts-processor; notify_service_owner on accounts-gateway | 36 s |
| BENCH-0079 | unknown | unknown | abstained | None | None | - | 15 s |
| BENCH-0080 | authentication | authentication | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00621; notify_service_owner on inventory-worker; add_contract_test on inventory-worker; replay_failed_messages on inventory-worker | 39 s |
| BENCH-0081 | file_transfer | unknown | abstained | None | None | - | 13 s |
| BENCH-0082 | authentication | authentication | awaiting_approval | 0.85 | 1.0 | rollback_deployment on DEPLOY-ACCOUNTS-00635; notify_service_owner on accounts-worker; add_contract_test on accounts-worker; add_monitoring on accounts-worker | 40 s |
| BENCH-0083 | rate_limiting | unknown | abstained | None | None | - | 20 s |
| BENCH-0084 | unknown | unknown | abstained | None | None | - | 16 s |
| BENCH-0085 | file_transfer | deployment_or_configuration | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-INVENTORY-00657; redeliver_file on inventory-exporter; add_monitoring on inventory-exporter; notify_service_owner on inventory-exporter | 34 s |
| BENCH-0086 | authorisation | authorisation | diagnosed | 0.35 | 1.0 | notify_service_owner on ledger-worker; add_monitoring on ledger-worker | 36 s |
| BENCH-0087 | rate_limiting | unknown | abstained | None | None | - | 15 s |
| BENCH-0088 | rate_limiting | rate_limiting | awaiting_approval | 0.3 | 0.833 | enable_rate_limiting on invoicing-worker; replay_failed_messages on invoicing-worker; add_monitoring on invoicing-worker; notify_service_owner on invoicing-worker | 40 s |
| BENCH-0089 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.45 | 1.0 | update_field_mapping on payments-processor; replay_failed_messages on payments-processor; add_contract_test on payments-processor; notify_service_owner on payments-processor | 33 s |
| BENCH-0090 | data_quality | networking | awaiting_approval | 0.35 | 1.0 | add_monitoring on catalogue-processor; notify_service_owner on catalogue-processor; add_contract_test on catalogue-processor; enable_rate_limiting on catalogue-processor | 62 s |
| BENCH-0091 | networking | networking | diagnosed | 0.35 | 1.0 | notify_service_owner on billing-worker; add_monitoring on billing-worker | 57 s |
| BENCH-0092 | data_quality | deployment_or_configuration | awaiting_approval | 0.35 | 1.0 | notify_service_owner on claims-processor; add_monitoring on claims-processor; enable_rate_limiting on claims-processor | 65 s |
| BENCH-0093 | authorisation | networking | diagnosed | 0.65 | 1.0 | notify_service_owner on catalogue-worker; add_monitoring on catalogue-worker; add_contract_test on catalogue-worker | 37 s |
| BENCH-0094 | timeout | timeout | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00730; notify_service_owner on payments-db; add_monitoring on payments-processor; add_contract_test on payments-db; enable_rate_limiting on payments-processor | 46 s |
| BENCH-0095 | queue_or_event_processing | deployment_or_configuration | awaiting_approval | 0.2 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00739; replay_failed_messages on payments-worker; add_monitoring on payments-worker; notify_service_owner on payments-worker | 42 s |
| BENCH-0096 | rate_limiting | rate_limiting | awaiting_approval | 0.35 | 1.0 | enable_rate_limiting on accounts-worker; notify_service_owner on accounts-worker | 34 s |
| BENCH-0097 | timeout | timeout | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-SUBSCRIPTIONS-00756; notify_service_owner on subscriptions-processor; add_contract_test on subscriptions-processor | 40 s |
| BENCH-0098 | queue_or_event_processing | deployment_or_configuration | awaiting_approval | 0.1 | 0.833 | pause_job on inventory-worker; rollback_deployment on DEPLOY-INVENTORY-00766; add_contract_test on inventory-worker; notify_service_owner on inventory-worker; add_monitoring on inventory-worker | 36 s |
| BENCH-0099 | networking | deployment_or_configuration | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-RETURNS-00773; notify_service_owner on returns-processor; add_monitoring on returns-processor; add_contract_test on returns-processor | 38 s |
| BENCH-0100 | unknown | unknown | abstained | None | None | - | 16 s |
| BENCH-0101 | unknown | unknown | abstained | None | None | - | 17 s |
| BENCH-0102 | schema_contract_mismatch | schema_contract_mismatch | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-BOOKINGS-00792; update_field_mapping on bookings-processor; replay_failed_messages on bookings-processor; add_contract_test on bookings-processor; notify_service_owner on bookings-processor | 33 s |
| BENCH-0103 | file_transfer | deployment_or_configuration | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-BILLING-00800; redeliver_file on billing-exporter; notify_service_owner on billing-exporter; add_monitoring on billing-exporter | 40 s |
| BENCH-0104 | queue_or_event_processing | networking | awaiting_approval | 0.1 | 1.0 | add_contract_test on bookings-worker; add_monitoring on bookings-worker; notify_service_owner on bookings-worker; pause_job on bookings-worker; replay_failed_messages on bookings-worker | 46 s |
| BENCH-0105 | data_quality | deployment_or_configuration | awaiting_approval | 0.3 | 1.0 | rollback_deployment on DEPLOY-SETTLEMENTS-00818; add_contract_test on settlements-processor; notify_service_owner on settlements-processor; add_monitoring on settlements-processor | 37 s |
| BENCH-0106 | unknown | unknown | abstained | None | None | - | 14 s |
| BENCH-0107 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.45 | 1.0 | rollback_deployment on DEPLOY-PAYMENTS-00831; notify_service_owner on payments-worker; add_monitoring on payments-worker; replay_failed_messages on payments-worker | 31 s |
| BENCH-0108 | deployment_or_configuration | deployment_or_configuration | awaiting_approval | 0.9 | 1.0 | rollback_deployment on DEPLOY-BILLING-00837; notify_service_owner on billing-worker; add_contract_test on billing-worker; add_monitoring on billing-worker | 34 s |
| BENCH-0109 | authentication | authentication | awaiting_approval | 0.1 | 1.0 | rollback_deployment on DEPLOY-PROCUREMENT-00846; notify_service_owner on procurement-worker; add_monitoring on procurement-worker; replay_failed_messages on procurement-worker | 40 s |
| BENCH-0110 | authorisation | authorisation | awaiting_approval | 0.0 | 1.0 | rollback_deployment on DEPLOY-LOYALTY-00854; notify_service_owner on loyalty-worker; add_contract_test on loyalty-worker; replay_failed_messages on loyalty-worker; add_monitoring on loyalty-worker | 45 s |

| Family | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| amounts_in_cents | 5 | 0 (0%) | 70% | 0 |
| backfill_burst | 5 | 3 (60%) | 40% | 0 |
| bad_feature_flag | 5 | 5 (100%) | 100% | 0 |
| consumers_scaled_down | 5 | 0 (0%) | 80% | 0 |
| database_name_change | 5 | 0 (0%) | 50% | 0 |
| dropped_index | 5 | 2 (40%) | 80% | 0 |
| duplicates_after_failover | 5 | 1 (20%) | 73% | 0 |
| encoding_change | 5 | 1 (20%) | 90% | 0 |
| expired_client_credential | 5 | 5 (100%) | 93% | 0 |
| intermittent_resets | 5 | 5 (100%) | n/a | 0 |
| missing_setting | 5 | 5 (100%) | 100% | 0 |
| narrowed_scope | 5 | 3 (60%) | 100% | 0 |
| partner_allowlist_change | 5 | 3 (60%) | 100% | 0 |
| pool_shrunk | 5 | 2 (40%) | 90% | 0 |
| provider_outage | 5 | 3 (60%) | 70% | 0 |
| quota_lowered | 5 | 4 (80%) | 60% | 0 |
| renamed_field | 5 | 5 (100%) | 60% | 0 |
| revoked_key_after_switch | 5 | 5 (100%) | 80% | 0 |
| sporadic_nulls | 5 | 5 (100%) | n/a | 0 |
| stale_reference_data | 5 | 1 (20%) | 60% | 0 |
| type_change | 5 | 4 (80%) | 47% | 0 |
| wrong_directory | 5 | 1 (20%) | 40% | 0 |

| Category | Cases | Correct | Plan recall | Plans missing a fix |
|---|---|---|---|---|
| authentication | 10 | 10 (100%) | 87% | 0 |
| authorisation | 10 | 6 (60%) | 100% | 0 |
| data_quality | 10 | 1 (10%) | 65% | 0 |
| deployment_or_configuration | 10 | 10 (100%) | 100% | 0 |
| file_transfer | 10 | 2 (20%) | 65% | 0 |
| networking | 10 | 3 (30%) | 60% | 0 |
| queue_or_event_processing | 10 | 1 (10%) | 77% | 0 |
| rate_limiting | 10 | 7 (70%) | 50% | 0 |
| schema_contract_mismatch | 10 | 9 (90%) | 53% | 0 |
| timeout | 10 | 4 (40%) | 85% | 0 |
| unknown | 10 | 10 (100%) | n/a | 0 |

| Confidence | Answers | Right |
|---|---|---|
| 0.00 | 8 | 7 (88%) |
| 0.05 | 1 | 1 (100%) |
| 0.10 | 7 | 1 (14%) |
| 0.20 | 1 | 0 (0%) |
| 0.25 | 1 | 0 (0%) |
| 0.30 | 7 | 4 (57%) |
| 0.35 | 14 | 11 (79%) |
| 0.40 | 4 | 1 (25%) |
| 0.45 | 18 | 10 (56%) |
| 0.55 | 2 | 0 (0%) |
| 0.60 | 4 | 3 (75%) |
| 0.65 | 9 | 5 (56%) |
| 0.75 | 3 | 3 (100%) |
| 0.80 | 1 | 0 (0%) |
| 0.85 | 2 | 2 (100%) |
| 0.90 | 5 | 5 (100%) |

Steps refused by validation:

- BENCH-0007: redeliver_file on invoicing-exporter: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0008: add_monitoring on onboarding-exporter: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0012: replay_failed_messages on warranty-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0012: add_contract_test on warranty-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0014: replay_failed_messages on loyalty-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0015: replay_failed_messages on catalogue-worker: must come after a step that fixes the cause
- BENCH-0015: replay_failed_messages on catalogue-worker: must come after a step that fixes the cause
- BENCH-0017: add_contract_test on returns-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0018: replay_failed_messages on accounts-worker: must come after a step that fixes the cause
- BENCH-0018: replay_failed_messages on accounts-worker: must come after a step that fixes the cause
- BENCH-0019: replay_failed_messages on warranty-worker: must come after a step that fixes the cause
- BENCH-0019: enable_rate_limiting on warranty-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0019: replay_failed_messages on warranty-worker: must come after a step that fixes the cause
- BENCH-0021: replay_failed_messages on pricing-processor: must come after a step that fixes the cause
- BENCH-0021: rollback_deployment on pricing-processor: its target is not a deployment in the evidence
- BENCH-0021: replay_failed_messages on pricing-processor: must come after a step that fixes the cause
- BENCH-0021: add_contract_test on pricing-processor: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0023: replay_failed_messages on billing-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0023: add_contract_test on billing-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0023: add_monitoring on billing-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0025: add_contract_test on rewards-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0026: replay_failed_messages on billing-processor: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0027: enable_rate_limiting on subscriptions-processor: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0029: add_contract_test on loyalty-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0030: notify_service_owner on payroll-processor: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0030: add_contract_test on payroll-processor: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0031: add_contract_test on rewards-exporter: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0037: add_contract_test on subscriptions-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0038: replay_failed_messages on onboarding-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0039: add_monitoring on catalogue-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0041: enable_rate_limiting on loyalty-processor: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0042: add_contract_test on warranty-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0045: replay_failed_messages on claims-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0045: add_contract_test on claims-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0049: add_contract_test on payments-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0050: add_contract_test on bookings-exporter: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0051: enable_rate_limiting on billing-processor: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0052: enable_rate_limiting on returns-processor: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0055: add_monitoring on invoicing-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0057: add_monitoring on ledger-processor: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0057: add_contract_test on ledger-processor: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0058: notify_service_owner on claims-processor: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0059: notify_service_owner on pricing-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0070: rollback_deployment on billing-worker: its target is not a deployment in the evidence
- BENCH-0075: add_contract_test on procurement-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0077: replay_failed_messages on inventory-worker: must come after a step that fixes the cause
- BENCH-0077: replay_failed_messages on inventory-worker: must come after a step that fixes the cause
- BENCH-0078: add_monitoring on accounts-processor: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0082: update_field_mapping on accounts-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0085: add_contract_test on inventory-exporter: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0088: pause_job on invoicing-backfill: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0090: replay_failed_messages on catalogue-processor: must come after a step that fixes the cause
- BENCH-0090: replay_failed_messages on catalogue-processor: must come after a step that fixes the cause
- BENCH-0091: replay_failed_messages on billing-worker: must come after a step that fixes the cause
- BENCH-0091: enable_rate_limiting on billing-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0091: add_contract_test on billing-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0091: replay_failed_messages on billing-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0092: rollback_deployment on claims-processor: its target is not a deployment in the evidence
- BENCH-0092: replay_failed_messages on claims-processor: must come after a step that fixes the cause
- BENCH-0092: add_contract_test on claims-processor: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0092: replay_failed_messages on claims-processor: must come after a step that fixes the cause
- BENCH-0092: add_contract_test on claims-processor: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0095: enable_rate_limiting on payments-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0096: add_contract_test on accounts-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0097: add_monitoring on subscriptions-processor: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0103: add_contract_test on billing-exporter: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0105: replay_failed_messages on settlements-processor: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0107: add_contract_test on payments-worker: cites neither the root cause's evidence nor a runbook or past incident
- BENCH-0108: replay_failed_messages on billing-worker: cites neither the root cause's evidence nor a runbook or past incident

Without logs: BENCH-0001 abstained, BENCH-0002 abstained, BENCH-0003 abstained, BENCH-0004 abstained, BENCH-0005 abstained, BENCH-0006 abstained, BENCH-0007 abstained, BENCH-0008 abstained, BENCH-0009 abstained, BENCH-0010 abstained, BENCH-0011 abstained, BENCH-0012 abstained, BENCH-0013 abstained, BENCH-0014 abstained, BENCH-0015 abstained, BENCH-0016 abstained, BENCH-0017 abstained, BENCH-0018 abstained, BENCH-0019 abstained, BENCH-0020 abstained, BENCH-0021 abstained, BENCH-0022 abstained, BENCH-0023 abstained, BENCH-0024 abstained, BENCH-0025 abstained, BENCH-0026 abstained, BENCH-0027 abstained, BENCH-0028 abstained, BENCH-0029 abstained, BENCH-0030 abstained, BENCH-0031 abstained, BENCH-0032 abstained, BENCH-0033 abstained, BENCH-0034 abstained, BENCH-0035 abstained, BENCH-0036 abstained, BENCH-0037 abstained, BENCH-0038 abstained, BENCH-0039 abstained, BENCH-0040 abstained, BENCH-0041 abstained, BENCH-0042 abstained, BENCH-0043 abstained, BENCH-0044 abstained, BENCH-0045 abstained, BENCH-0046 abstained, BENCH-0047 abstained, BENCH-0048 abstained, BENCH-0049 abstained, BENCH-0050 abstained, BENCH-0051 abstained, BENCH-0052 abstained, BENCH-0053 abstained, BENCH-0054 abstained, BENCH-0055 abstained, BENCH-0056 abstained, BENCH-0057 abstained, BENCH-0058 abstained, BENCH-0059 abstained, BENCH-0060 abstained, BENCH-0061 abstained, BENCH-0062 abstained, BENCH-0063 abstained, BENCH-0064 abstained, BENCH-0065 abstained, BENCH-0066 abstained, BENCH-0067 abstained, BENCH-0068 abstained, BENCH-0069 abstained, BENCH-0070 abstained, BENCH-0071 abstained, BENCH-0072 abstained, BENCH-0073 abstained, BENCH-0074 abstained, BENCH-0075 abstained, BENCH-0076 abstained, BENCH-0077 abstained, BENCH-0078 abstained, BENCH-0079 abstained, BENCH-0080 abstained, BENCH-0081 abstained, BENCH-0082 abstained, BENCH-0083 abstained, BENCH-0084 abstained, BENCH-0085 abstained, BENCH-0086 abstained, BENCH-0087 abstained, BENCH-0088 abstained, BENCH-0089 abstained, BENCH-0090 abstained, BENCH-0091 abstained, BENCH-0092 abstained, BENCH-0093 abstained, BENCH-0094 abstained, BENCH-0095 abstained, BENCH-0096 abstained, BENCH-0097 abstained, BENCH-0098 abstained, BENCH-0099 abstained, BENCH-0100 abstained, BENCH-0101 abstained, BENCH-0102 abstained, BENCH-0103 abstained, BENCH-0104 abstained, BENCH-0105 abstained, BENCH-0106 abstained, BENCH-0107 abstained, BENCH-0108 abstained, BENCH-0109 abstained, BENCH-0110 abstained.
