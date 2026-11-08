---
document_id: SPEC-RETURNS-C1
document_type: api_spec
title: returns-worker settings
system: returns
service: returns-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# returns-worker settings

The returns-worker settings contract.

## Required

RELAY_HOST is required. Without it, returns-worker exits at start.

## Optional

BATCH_SIZE defaults to 50.
