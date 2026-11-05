---
document_id: SPEC-LOYALTY-C1
document_type: api_spec
title: loyalty-worker settings
system: loyalty
service: loyalty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# loyalty-worker settings

The loyalty-worker settings contract.

## Required

RELAY_HOST is required. Without it, loyalty-worker exits at start.

## Optional

BATCH_SIZE defaults to 50.
