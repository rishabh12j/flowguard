---
document_id: SPEC-PRICING-C1
document_type: api_spec
title: pricing-worker settings
system: pricing
service: pricing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# pricing-worker settings

The pricing-worker settings contract.

## Required

RELAY_HOST is required. Without it, pricing-worker exits at start.

## Optional

BATCH_SIZE defaults to 50.
