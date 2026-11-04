---
document_id: SPEC-BANK-SFTP-V1
document_type: api_spec
title: Bank payment file drop
system: vendor-payments
service: bank-sftp
version: 1.3
effective_date: 2026-03-01
is_current: true
---

# Bank payment file drop

`sftp-uploader` delivers each day's payment batch to the bank's SFTP server, and the bank pays every line in the file.

## File drop

Payment files must be uploaded to `/inbound/payments`. The bank reads no other directory: a file placed anywhere else is kept but never processed, and no error is returned.

## Acknowledgements

Within 60 minutes of picking up a file, the bank writes an acknowledgement file to `/acks`. `bank-ack-poller` waits up to 2 hours for it before raising an error.
