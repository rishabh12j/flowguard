---
document_id: SPEC-INVENTORY-N2
document_type: api_spec
title: inventory-partner-api availability
system: inventory
service: inventory-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# inventory-partner-api availability

The inventory-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
