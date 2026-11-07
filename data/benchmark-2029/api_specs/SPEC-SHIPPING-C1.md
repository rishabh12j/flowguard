---
document_id: SPEC-SHIPPING-C1
document_type: api_spec
title: shipping-worker settings
system: shipping
service: shipping-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# shipping-worker settings

The shipping-worker settings contract.

## Required

SERVICE_REGION is required. Without it, shipping-worker exits at start.

## Optional

BATCH_SIZE defaults to 50.
