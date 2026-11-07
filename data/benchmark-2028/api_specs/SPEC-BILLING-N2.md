---
document_id: SPEC-BILLING-N2
document_type: api_spec
title: billing-partner-api availability
system: billing
service: billing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# billing-partner-api availability

The billing-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
