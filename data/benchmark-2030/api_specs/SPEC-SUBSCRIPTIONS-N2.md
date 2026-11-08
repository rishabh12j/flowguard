---
document_id: SPEC-SUBSCRIPTIONS-N2
document_type: api_spec
title: subscriptions-partner-api availability
system: subscriptions
service: subscriptions-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# subscriptions-partner-api availability

The subscriptions-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
