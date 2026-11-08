---
document_id: SPEC-SETTLEMENTS-C1
document_type: api_spec
title: settlements-worker settings
system: settlements
service: settlements-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# settlements-worker settings

The settlements-worker settings contract.

## Required

QUEUE_URL is required. Without it, settlements-worker exits at start.

## Optional

BATCH_SIZE defaults to 50.
