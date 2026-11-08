---
document_id: SPEC-PAYMENTS-E2
document_type: api_spec
title: payments-worker capacity
system: payments
service: payments-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payments-worker capacity

The payments-worker capacity contract.

## Throughput

Each replica handles about 300 events a minute; peak traffic needs 5.

## Deadlines

Events must be processed within 10 minutes.
