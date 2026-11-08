---
document_id: SPEC-PAYMENTS-N2
document_type: api_spec
title: payments-partner-api availability
system: payments
service: payments-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payments-partner-api availability

The payments-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
