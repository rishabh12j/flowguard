---
document_id: SPEC-LEDGER-R1
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

## Rate limits

Each client may send 60 requests per minute. Above that, the API answers 429.

## Retries

Wait for the Retry-After header before retrying.
