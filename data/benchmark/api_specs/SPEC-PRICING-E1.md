---
document_id: SPEC-PRICING-E1
document_type: api_spec
title: pricing-events delivery
system: pricing
service: pricing-reports
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# pricing-events delivery

The pricing-events delivery contract.

## Delivery

Delivery is at least once: after a failover, events after the last committed offset arrive again.

## Consumers

Consumers must skip events they already processed.
