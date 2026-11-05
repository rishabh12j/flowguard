---
document_id: SPEC-LEDGER-R2
document_type: api_spec
title: ledger-partner-api limits
system: ledger
service: ledger-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# ledger-partner-api limits

The ledger-partner-api limits contract.

## Quotas

Each client has a per-minute quota, announced by alert when it changes.

## Responses

Requests over the quota get 429.
