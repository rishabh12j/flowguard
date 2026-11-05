---
document_id: SPEC-SETTLEMENTS-N2
document_type: api_spec
title: settlements-partner-api availability
system: settlements
service: settlements-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# settlements-partner-api availability

The settlements-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
