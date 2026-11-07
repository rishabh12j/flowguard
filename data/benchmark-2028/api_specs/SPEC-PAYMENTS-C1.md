---
document_id: SPEC-PAYMENTS-C1
document_type: api_spec
title: payments-worker settings
system: payments
service: payments-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payments-worker settings

The payments-worker settings contract.

## Required

RELAY_HOST is required. Without it, payments-worker exits at start.

## Optional

BATCH_SIZE defaults to 50.
