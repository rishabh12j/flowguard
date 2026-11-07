---
document_id: SPEC-REWARDS-R1
document_type: api_spec
title: rewards-partner-api limits
system: rewards
service: rewards-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# rewards-partner-api limits

The rewards-partner-api limits contract.

## Rate limits

Each client may send 60 requests per minute. Above that, the API answers 429.

## Retries

Wait for the Retry-After header before retrying.
