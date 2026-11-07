---
document_id: SPEC-RETURNS-E2
document_type: api_spec
title: returns-worker capacity
system: returns
service: returns-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# returns-worker capacity

The returns-worker capacity contract.

## Throughput

Each replica handles about 300 events a minute; peak traffic needs 5.

## Deadlines

Events must be processed within 10 minutes.
