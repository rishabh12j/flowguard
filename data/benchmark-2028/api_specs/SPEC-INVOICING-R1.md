---
document_id: SPEC-INVOICING-R1
document_type: api_spec
title: invoicing-partner-api limits
system: invoicing
service: invoicing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# invoicing-partner-api limits

The invoicing-partner-api limits contract.

## Rate limits

Each client may send 100 requests per minute. Above that, the API answers 429.

## Retries

Wait for the Retry-After header before retrying.
