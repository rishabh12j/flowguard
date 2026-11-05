---
document_id: SPEC-LEDGER-E2
document_type: api_spec
title: ledger-worker capacity
system: ledger
service: ledger-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# ledger-worker capacity

The ledger-worker capacity contract.

## Throughput

Each replica handles about 300 events a minute; peak traffic needs 5.

## Deadlines

Events must be processed within 10 minutes.
