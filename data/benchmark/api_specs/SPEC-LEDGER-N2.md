---
document_id: SPEC-LEDGER-N2
document_type: api_spec
title: ledger-partner-api availability
system: ledger
service: ledger-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# ledger-partner-api availability

The ledger-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
