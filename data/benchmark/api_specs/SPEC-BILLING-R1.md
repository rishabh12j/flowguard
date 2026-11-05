---
document_id: SPEC-BILLING-R1
document_type: api_spec
title: billing-partner-api limits
system: billing
service: billing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# billing-partner-api limits

The billing-partner-api limits contract.

## Rate limits

Each client may send 60 requests per minute. Above that, the API answers 429.

## Retries

Wait for the Retry-After header before retrying.
