---
document_id: SPEC-INVENTORY-F1
document_type: api_spec
title: inventory-partner-sftp file drop
system: inventory
service: inventory-exporter
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# inventory-partner-sftp file drop

The inventory-partner-sftp file drop contract.

## Directory

Files must be uploaded to /inbound. Files anywhere else are never read.

## Acknowledgements

Files are acknowledged within an hour.
