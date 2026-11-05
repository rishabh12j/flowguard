---
document_id: SPEC-CATALOGUE-N2
document_type: api_spec
title: catalogue-partner-api availability
system: catalogue
service: catalogue-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# catalogue-partner-api availability

The catalogue-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
