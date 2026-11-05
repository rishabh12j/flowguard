---
document_id: SPEC-WARRANTY-E2
document_type: api_spec
title: warranty-worker capacity
system: warranty
service: warranty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# warranty-worker capacity

The warranty-worker capacity contract.

## Throughput

Each replica handles about 300 events a minute; peak traffic needs 5.

## Deadlines

Events must be processed within 10 minutes.
