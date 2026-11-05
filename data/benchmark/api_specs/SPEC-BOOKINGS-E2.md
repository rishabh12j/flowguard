---
document_id: SPEC-BOOKINGS-E2
document_type: api_spec
title: bookings-worker capacity
system: bookings
service: bookings-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# bookings-worker capacity

The bookings-worker capacity contract.

## Throughput

Each replica handles about 300 events a minute; peak traffic needs 5.

## Deadlines

Events must be processed within 10 minutes.
