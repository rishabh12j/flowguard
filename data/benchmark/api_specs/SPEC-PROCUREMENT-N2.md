---
document_id: SPEC-PROCUREMENT-N2
document_type: api_spec
title: procurement-partner-api availability
system: procurement
service: procurement-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# procurement-partner-api availability

The procurement-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
