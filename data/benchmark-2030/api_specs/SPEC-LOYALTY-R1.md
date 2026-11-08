---
document_id: SPEC-LOYALTY-R1
document_type: api_spec
title: loyalty-partner-api limits
system: loyalty
service: loyalty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# loyalty-partner-api limits

The loyalty-partner-api limits contract.

## Rate limits

Each client may send 100 requests per minute. Above that, the API answers 429.

## Retries

Wait for the Retry-After header before retrying.
