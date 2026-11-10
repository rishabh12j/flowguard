# What failed: dev set

Model: `gemma4:12b`. Finished 2026-11-10 07:43 UTC. The model saw only the symptoms (logs, API specs, the dependency map), with neutral IDs.

**The probe fails its marks.**

- pass: 90 of 100 right (at least 90 needed)
- fail: unknown for 0 of 10 with no cause (at least 9 needed)

With a cause: 90 right, 10 wrong, 0 answered unknown.

| Family | Expected | Right | Answers |
|---|---|---|---|
| amounts_in_cents | data_quality | 5 of 5 | data_quality 5 |
| backfill_burst | rate_limiting | 5 of 5 | rate_limiting 5 |
| bad_feature_flag | deployment_or_configuration | 5 of 5 | deployment_or_configuration 5 |
| consumers_scaled_down | queue_or_event_processing | 5 of 5 | queue_or_event_processing 5 |
| database_name_change | networking | 5 of 5 | networking 5 |
| dropped_index | timeout | 5 of 5 | timeout 5 |
| duplicates_after_failover | queue_or_event_processing | 5 of 5 | queue_or_event_processing 5 |
| encoding_change | file_transfer | 0 of 5 | schema_contract_mismatch 4, data_quality 1 |
| expired_client_credential | authentication | 5 of 5 | authentication 5 |
| intermittent_resets | unknown | 0 of 5 | networking 5 |
| missing_setting | deployment_or_configuration | 5 of 5 | deployment_or_configuration 5 |
| narrowed_scope | authorisation | 5 of 5 | authorisation 5 |
| partner_allowlist_change | authorisation | 5 of 5 | authorisation 5 |
| pool_shrunk | timeout | 5 of 5 | timeout 5 |
| provider_outage | networking | 5 of 5 | networking 5 |
| quota_lowered | rate_limiting | 5 of 5 | rate_limiting 5 |
| renamed_field | schema_contract_mismatch | 5 of 5 | schema_contract_mismatch 5 |
| revoked_key_after_switch | authentication | 5 of 5 | authentication 5 |
| sporadic_nulls | unknown | 0 of 5 | data_quality 3, schema_contract_mismatch 2 |
| stale_reference_data | data_quality | 5 of 5 | data_quality 5 |
| type_change | schema_contract_mismatch | 5 of 5 | schema_contract_mismatch 5 |
| wrong_directory | file_transfer | 0 of 5 | timeout 5 |

## Misses

- BENCH-0001 (intermittent_resets): expected unknown, got networking. Model: The pricing-worker is experiencing repeated connection resets when attempting to communicate with the pricing-partner-api.
- BENCH-0007 (encoding_change): expected file_transfer, got schema_contract_mismatch. Model: The exported files were rejected by the partner because they contained an unsupported character encoding, violating the required UTF-8 format.
- BENCH-0008 (encoding_change): expected file_transfer, got data_quality. Model: The export files are being rejected by the partner's SFTP server because they contain an unsupported character encoding, violating the required UTF-8 format.
- BENCH-0011 (sporadic_nulls): expected unknown, got data_quality. Model: The payroll-processor is rejecting records because the 'account_id' field contains null values, which violates the requirement that records with missing values be rejected.
- BENCH-0024 (sporadic_nulls): expected unknown, got schema_contract_mismatch. Model: The payments-processor is rejecting records because a required field, 'order_id', contains a null value, violating the expected data structure.
- BENCH-0031 (wrong_directory): expected file_transfer, got timeout. Model: The rewards-exporter system failed to receive a timely acknowledgement from the rewards-partner-sftp service after uploading a file, exceeding the allowed time limit.
- BENCH-0040 (intermittent_resets): expected unknown, got networking. Model: The rewards-worker is experiencing connection resets when attempting to communicate with the rewards-partner-api.
- BENCH-0050 (wrong_directory): expected file_transfer, got timeout. Model: The system failed to receive a confirmation for a file upload within the expected timeframe, resulting in a timeout error.
- BENCH-0054 (encoding_change): expected file_transfer, got schema_contract_mismatch. Model: The partner's SFTP server is rejecting the exported files because they contain an unsupported character encoding.
- BENCH-0068 (wrong_directory): expected file_transfer, got timeout. Model: The pricing-exporter successfully uploaded the file, but the system timed out while waiting for a required acknowledgement from the pricing-partner-sftp service.
- BENCH-0074 (wrong_directory): expected file_transfer, got timeout. Model: The system failed to receive a confirmation for an uploaded file within the expected timeframe, resulting in a timeout error.
- BENCH-0076 (intermittent_resets): expected unknown, got networking. Model: The accounts-worker service is experiencing intermittent connection resets when attempting to communicate with the accounts-partner-api.
- BENCH-0079 (sporadic_nulls): expected unknown, got data_quality. Model: The bookings-processor is rejecting records because the 'order_id' field contains a null value, which violates the requirement that records must not have missing values.
- BENCH-0081 (wrong_directory): expected file_transfer, got timeout. Model: The billing exporter successfully uploaded the file but failed to receive a required acknowledgement from the partner's SFTP server within the allotted time frame.
- BENCH-0084 (sporadic_nulls): expected unknown, got schema_contract_mismatch. Model: The procurement-processor is rejecting records because the 'order_id' field contains null values, which violates the requirement that records must not have missing values.
- BENCH-0085 (encoding_change): expected file_transfer, got schema_contract_mismatch. Model: The inventory export file was rejected by the partner system because it contained an unsupported character encoding, violating the expected file format.
- BENCH-0100 (sporadic_nulls): expected unknown, got data_quality. Model: The payroll-processor is rejecting records because the 'account_id' field contains null values, which violates the requirement that records with missing values be rejected.
- BENCH-0101 (intermittent_resets): expected unknown, got networking. Model: The payments-worker service is experiencing intermittent connection resets when attempting to communicate with the payments-partner-api.
- BENCH-0103 (encoding_change): expected file_transfer, got schema_contract_mismatch. Model: The billing export file was rejected by the partner SFTP because it contained an unsupported character encoding, violating the expected file format.
- BENCH-0106 (intermittent_resets): expected unknown, got networking. Model: The warranty-worker is unable to maintain a stable connection to the warranty-partner-api, resulting in repeated connection resets by the peer.
