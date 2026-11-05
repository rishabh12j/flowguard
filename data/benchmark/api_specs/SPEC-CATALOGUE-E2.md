---
document_id: SPEC-CATALOGUE-E2
document_type: api_spec
title: catalogue-worker capacity
system: catalogue
service: catalogue-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# catalogue-worker capacity

The catalogue-worker capacity contract.

## Throughput

Each replica handles about 300 events a minute; peak traffic needs 5.

## Deadlines

Events must be processed within 10 minutes.
