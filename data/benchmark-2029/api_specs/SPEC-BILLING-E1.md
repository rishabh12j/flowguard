---
document_id: SPEC-BILLING-E1
document_type: api_spec
title: billing-events delivery
system: billing
service: billing-reports
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# billing-events delivery

The billing-events delivery contract.

## Delivery

Delivery is at least once: after a failover, events after the last committed offset arrive again.

## Consumers

Consumers must skip events they already processed.
