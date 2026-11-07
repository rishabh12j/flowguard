---
document_id: SPEC-WARRANTY-E1
document_type: api_spec
title: warranty-events delivery
system: warranty
service: warranty-reports
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# warranty-events delivery

The warranty-events delivery contract.

## Delivery

Delivery is at least once: after a failover, events after the last committed offset arrive again.

## Consumers

Consumers must skip events they already processed.
