---
document_id: SPEC-LEDGER-DB-V1
document_type: api_spec
title: Ledger database access
system: ledger-sync
service: ledger-db
version: 1.2
effective_date: 2026-01-20
is_current: true
---

# Ledger database access

`ledger-sync` copies the previous day's ledger rows from `ledger-db` every night at 02:00 UTC.

## Connection

Clients connect to `ledger-db.ledger.internal` on port 5432. The name is resolved through `internal-dns`, which serves the `ledger.internal` zone. Clients must use the name, not an IP address, because the database can move between hosts.

## Sync window

The sync must finish by 05:00 UTC, before the finance reports are built.
