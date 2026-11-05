---
document_id: SPEC-INVENTORY-R1
document_type: api_spec
title: inventory-partner-api limits
system: inventory
service: inventory-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# inventory-partner-api limits

The inventory-partner-api limits contract.

## Rate limits

Each client may send 120 requests per minute. Above that, the API answers 429.

## Retries

Wait for the Retry-After header before retrying.
