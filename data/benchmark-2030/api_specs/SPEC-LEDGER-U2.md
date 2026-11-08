---
document_id: SPEC-LEDGER-U2
document_type: api_spec
title: ledger-partner-api connections
system: ledger
service: ledger-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# ledger-partner-api connections

The ledger-partner-api connections contract.

## Keep-alive

Idle connections are closed after 60 seconds.

## Retries

Clients retry once.
