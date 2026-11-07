---
document_id: SPEC-INVENTORY-T1
document_type: api_spec
title: inventory-processor capacity
system: inventory
service: inventory-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# inventory-processor capacity

The inventory-processor capacity contract.

## Pool

inventory-processor needs about 40 database connections at peak; its pool is sized at 50.

## Timeouts

A request waiting 30 s for a connection fails.
