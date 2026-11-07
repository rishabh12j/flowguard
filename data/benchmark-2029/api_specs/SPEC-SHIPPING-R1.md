---
document_id: SPEC-SHIPPING-R1
document_type: api_spec
title: shipping-partner-api limits
system: shipping
service: shipping-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# shipping-partner-api limits

The shipping-partner-api limits contract.

## Rate limits

Each client may send 100 requests per minute. Above that, the API answers 429.

## Retries

Wait for the Retry-After header before retrying.
