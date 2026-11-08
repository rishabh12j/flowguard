---
document_id: SPEC-RETURNS-N2
document_type: api_spec
title: returns-partner-api availability
system: returns
service: returns-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# returns-partner-api availability

The returns-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
