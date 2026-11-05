---
document_id: SPEC-SUBSCRIPTIONS-E2
document_type: api_spec
title: subscriptions-worker capacity
system: subscriptions
service: subscriptions-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# subscriptions-worker capacity

The subscriptions-worker capacity contract.

## Throughput

Each replica handles about 300 events a minute; peak traffic needs 5.

## Deadlines

Events must be processed within 10 minutes.
