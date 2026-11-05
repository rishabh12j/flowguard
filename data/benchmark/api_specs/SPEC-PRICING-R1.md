---
document_id: SPEC-PRICING-R1
document_type: api_spec
title: pricing-partner-api limits
system: pricing
service: pricing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# pricing-partner-api limits

The pricing-partner-api limits contract.

## Rate limits

Each client may send 100 requests per minute. Above that, the API answers 429.

## Retries

Wait for the Retry-After header before retrying.
