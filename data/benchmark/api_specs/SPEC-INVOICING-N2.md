---
document_id: SPEC-INVOICING-N2
document_type: api_spec
title: invoicing-partner-api availability
system: invoicing
service: invoicing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# invoicing-partner-api availability

The invoicing-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
