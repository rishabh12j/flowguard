---
document_id: HIST-INC-063
document_type: historical_incident
title: Carrier rate limiting during an order migration
system: order-fulfilment
service: order-sync-worker
version: 1.0
effective_date: 2026-06-20
is_current: true
---

# HIST-INC-063: Carrier rate limiting during an order migration

## Symptoms

Shipments failed with `429 Too Many Requests` for two hours, and customers saw delayed labels.

## Root cause

An order migration sent every historical order through `order-sync-worker` at once, far above the carrier's 100 requests per minute.

## Resolution

The migration was paused, and the failed shipments were retried once the rate dropped.

## Follow-up

The review recommended a rate limit in `order-sync-worker` itself. It was not implemented.
