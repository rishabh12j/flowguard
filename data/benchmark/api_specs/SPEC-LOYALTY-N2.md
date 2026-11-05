---
document_id: SPEC-LOYALTY-N2
document_type: api_spec
title: loyalty-partner-api availability
system: loyalty
service: loyalty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# loyalty-partner-api availability

The loyalty-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
