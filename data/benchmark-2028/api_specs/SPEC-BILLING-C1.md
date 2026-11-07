---
document_id: SPEC-BILLING-C1
document_type: api_spec
title: billing-worker settings
system: billing
service: billing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# billing-worker settings

The billing-worker settings contract.

## Required

QUEUE_URL is required. Without it, billing-worker exits at start.

## Optional

BATCH_SIZE defaults to 50.
