---
document_id: SPEC-CLAIMS-C1
document_type: api_spec
title: claims-worker settings
system: claims
service: claims-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# claims-worker settings

The claims-worker settings contract.

## Required

RELAY_HOST is required. Without it, claims-worker exits at start.

## Optional

BATCH_SIZE defaults to 50.
