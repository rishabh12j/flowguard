---
document_id: SPEC-PAYROLL-E2
document_type: api_spec
title: payroll-worker capacity
system: payroll
service: payroll-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payroll-worker capacity

The payroll-worker capacity contract.

## Throughput

Each replica handles about 300 events a minute; peak traffic needs 5.

## Deadlines

Events must be processed within 10 minutes.
