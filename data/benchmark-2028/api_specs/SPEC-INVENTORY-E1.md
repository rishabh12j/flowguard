---
document_id: SPEC-INVENTORY-E1
document_type: api_spec
title: inventory-events delivery
system: inventory
service: inventory-reports
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# inventory-events delivery

The inventory-events delivery contract.

## Delivery

Delivery is at least once: after a failover, events after the last committed offset arrive again.

## Consumers

Consumers must skip events they already processed.
