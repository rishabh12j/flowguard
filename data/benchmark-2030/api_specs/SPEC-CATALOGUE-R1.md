---
document_id: SPEC-CATALOGUE-R1
document_type: api_spec
title: catalogue-partner-api limits
system: catalogue
service: catalogue-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# catalogue-partner-api limits

The catalogue-partner-api limits contract.

## Rate limits

Each client may send 120 requests per minute. Above that, the API answers 429.

## Retries

Wait for the Retry-After header before retrying.
