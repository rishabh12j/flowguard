---
document_id: SPEC-PRICING-E2
document_type: api_spec
title: pricing-worker capacity
system: pricing
service: pricing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# pricing-worker capacity

The pricing-worker capacity contract.

## Throughput

Each replica handles about 300 events a minute; peak traffic needs 5.

## Deadlines

Events must be processed within 10 minutes.
