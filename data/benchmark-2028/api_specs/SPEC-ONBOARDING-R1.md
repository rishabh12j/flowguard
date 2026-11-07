---
document_id: SPEC-ONBOARDING-R1
document_type: api_spec
title: onboarding-partner-api limits
system: onboarding
service: onboarding-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# onboarding-partner-api limits

The onboarding-partner-api limits contract.

## Rate limits

Each client may send 120 requests per minute. Above that, the API answers 429.

## Retries

Wait for the Retry-After header before retrying.
