---
document_id: SPEC-SETTLEMENTS-R1
document_type: api_spec
title: settlements-partner-api limits
system: settlements
service: settlements-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# settlements-partner-api limits

The settlements-partner-api limits contract.

## Rate limits

Each client may send 100 requests per minute. Above that, the API answers 429.

## Retries

Wait for the Retry-After header before retrying.
