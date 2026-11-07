---
document_id: SPEC-LOYALTY-T1
document_type: api_spec
title: loyalty-processor capacity
system: loyalty
service: loyalty-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# loyalty-processor capacity

The loyalty-processor capacity contract.

## Pool

loyalty-processor needs about 40 database connections at peak; its pool is sized at 50.

## Timeouts

A request waiting 30 s for a connection fails.
