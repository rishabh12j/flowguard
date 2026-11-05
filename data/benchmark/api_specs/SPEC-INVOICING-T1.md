---
document_id: SPEC-INVOICING-T1
document_type: api_spec
title: invoicing-processor capacity
system: invoicing
service: invoicing-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# invoicing-processor capacity

The invoicing-processor capacity contract.

## Pool

invoicing-processor needs about 40 database connections at peak; its pool is sized at 50.

## Timeouts

A request waiting 30 s for a connection fails.
