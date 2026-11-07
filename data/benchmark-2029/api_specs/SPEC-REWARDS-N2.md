---
document_id: SPEC-REWARDS-N2
document_type: api_spec
title: rewards-partner-api availability
system: rewards
service: rewards-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# rewards-partner-api availability

The rewards-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
