---
document_id: SPEC-CLAIMS-R1
document_type: api_spec
title: claims-partner-api limits
system: claims
service: claims-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# claims-partner-api limits

The claims-partner-api limits contract.

## Rate limits

Each client may send 120 requests per minute. Above that, the API answers 429.

## Retries

Wait for the Retry-After header before retrying.
