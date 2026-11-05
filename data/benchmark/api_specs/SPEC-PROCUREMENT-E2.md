---
document_id: SPEC-PROCUREMENT-E2
document_type: api_spec
title: procurement-worker capacity
system: procurement
service: procurement-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# procurement-worker capacity

The procurement-worker capacity contract.

## Throughput

Each replica handles about 300 events a minute; peak traffic needs 5.

## Deadlines

Events must be processed within 10 minutes.
