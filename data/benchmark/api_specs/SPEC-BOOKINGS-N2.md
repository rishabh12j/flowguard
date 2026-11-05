---
document_id: SPEC-BOOKINGS-N2
document_type: api_spec
title: bookings-partner-api availability
system: bookings
service: bookings-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# bookings-partner-api availability

The bookings-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
