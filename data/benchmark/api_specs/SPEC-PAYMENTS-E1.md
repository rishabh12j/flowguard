---
document_id: SPEC-PAYMENTS-E1
document_type: api_spec
title: payments-events delivery
system: payments
service: payments-reports
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payments-events delivery

The payments-events delivery contract.

## Delivery

Delivery is at least once: after a failover, events after the last committed offset arrive again.

## Consumers

Consumers must skip events they already processed.
