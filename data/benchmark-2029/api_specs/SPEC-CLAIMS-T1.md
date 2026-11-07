---
document_id: SPEC-CLAIMS-T1
document_type: api_spec
title: claims-processor capacity
system: claims
service: claims-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# claims-processor capacity

The claims-processor capacity contract.

## Pool

claims-processor needs about 40 database connections at peak; its pool is sized at 50.

## Timeouts

A request waiting 30 s for a connection fails.
