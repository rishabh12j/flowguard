---
document_id: SPEC-CLAIMS-N2
document_type: api_spec
title: claims-partner-api availability
system: claims
service: claims-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# claims-partner-api availability

The claims-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
