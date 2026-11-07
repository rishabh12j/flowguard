---
document_id: SPEC-SUBSCRIPTIONS-C1
document_type: api_spec
title: subscriptions-worker settings
system: subscriptions
service: subscriptions-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# subscriptions-worker settings

The subscriptions-worker settings contract.

## Required

SERVICE_REGION is required. Without it, subscriptions-worker exits at start.

## Optional

BATCH_SIZE defaults to 50.
