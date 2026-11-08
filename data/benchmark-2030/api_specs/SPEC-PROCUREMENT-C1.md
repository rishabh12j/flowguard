---
document_id: SPEC-PROCUREMENT-C1
document_type: api_spec
title: procurement-worker settings
system: procurement
service: procurement-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# procurement-worker settings

The procurement-worker settings contract.

## Required

QUEUE_URL is required. Without it, procurement-worker exits at start.

## Optional

BATCH_SIZE defaults to 50.
