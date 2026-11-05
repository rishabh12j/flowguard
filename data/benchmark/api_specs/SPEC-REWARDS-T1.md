---
document_id: SPEC-REWARDS-T1
document_type: api_spec
title: rewards-processor capacity
system: rewards
service: rewards-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# rewards-processor capacity

The rewards-processor capacity contract.

## Pool

rewards-processor needs about 40 database connections at peak; its pool is sized at 50.

## Timeouts

A request waiting 30 s for a connection fails.
