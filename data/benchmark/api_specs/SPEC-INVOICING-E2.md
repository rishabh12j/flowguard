---
document_id: SPEC-INVOICING-E2
document_type: api_spec
title: invoicing-worker capacity
system: invoicing
service: invoicing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# invoicing-worker capacity

The invoicing-worker capacity contract.

## Throughput

Each replica handles about 300 events a minute; peak traffic needs 5.

## Deadlines

Events must be processed within 10 minutes.
