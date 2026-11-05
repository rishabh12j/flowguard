---
document_id: SPEC-CATALOGUE-T1
document_type: api_spec
title: catalogue-processor capacity
system: catalogue
service: catalogue-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# catalogue-processor capacity

The catalogue-processor capacity contract.

## Pool

catalogue-processor needs about 40 database connections at peak; its pool is sized at 50.

## Timeouts

A request waiting 30 s for a connection fails.
