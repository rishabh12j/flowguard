---
document_id: SPEC-BILLING-T1
document_type: api_spec
title: billing-processor capacity
system: billing
service: billing-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# billing-processor capacity

The billing-processor capacity contract.

## Pool

billing-processor needs about 40 database connections at peak; its pool is sized at 50.

## Timeouts

A request waiting 30 s for a connection fails.
