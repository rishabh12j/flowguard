---
document_id: SPEC-ONBOARDING-T1
document_type: api_spec
title: onboarding-processor capacity
system: onboarding
service: onboarding-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# onboarding-processor capacity

The onboarding-processor capacity contract.

## Pool

onboarding-processor needs about 40 database connections at peak; its pool is sized at 50.

## Timeouts

A request waiting 30 s for a connection fails.
