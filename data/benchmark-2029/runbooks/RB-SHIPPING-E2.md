---
document_id: RB-SHIPPING-E2
document_type: runbook
title: shipping-worker falling behind
system: shipping
service: shipping-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# shipping-worker falling behind

## When to use

Use this runbook when shipping-events grows and events arrive late.

## Procedure

1. Check shipping-worker's replica count and recent releases.
2. Roll back a release that reduced capacity, after approval.

## Warnings

- Do not purge the queue.
