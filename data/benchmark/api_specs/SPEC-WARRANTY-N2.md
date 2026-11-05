---
document_id: SPEC-WARRANTY-N2
document_type: api_spec
title: warranty-partner-api availability
system: warranty
service: warranty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# warranty-partner-api availability

The warranty-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
