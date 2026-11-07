---
document_id: SPEC-ONBOARDING-E2
document_type: api_spec
title: onboarding-worker capacity
system: onboarding
service: onboarding-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# onboarding-worker capacity

The onboarding-worker capacity contract.

## Throughput

Each replica handles about 300 events a minute; peak traffic needs 5.

## Deadlines

Events must be processed within 10 minutes.
