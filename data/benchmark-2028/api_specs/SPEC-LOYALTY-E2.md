---
document_id: SPEC-LOYALTY-E2
document_type: api_spec
title: loyalty-worker capacity
system: loyalty
service: loyalty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# loyalty-worker capacity

The loyalty-worker capacity contract.

## Throughput

Each replica handles about 300 events a minute; peak traffic needs 5.

## Deadlines

Events must be processed within 10 minutes.
