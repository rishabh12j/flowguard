---
document_id: SPEC-PRICING-N2
document_type: api_spec
title: pricing-partner-api availability
system: pricing
service: pricing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# pricing-partner-api availability

The pricing-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
