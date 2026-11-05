---
document_id: SPEC-SETTLEMENTS-E2
document_type: api_spec
title: settlements-worker capacity
system: settlements
service: settlements-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# settlements-worker capacity

The settlements-worker capacity contract.

## Throughput

Each replica handles about 300 events a minute; peak traffic needs 5.

## Deadlines

Events must be processed within 10 minutes.
