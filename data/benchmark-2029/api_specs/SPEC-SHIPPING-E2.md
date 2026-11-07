---
document_id: SPEC-SHIPPING-E2
document_type: api_spec
title: shipping-worker capacity
system: shipping
service: shipping-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# shipping-worker capacity

The shipping-worker capacity contract.

## Throughput

Each replica handles about 300 events a minute; peak traffic needs 5.

## Deadlines

Events must be processed within 10 minutes.
