---
document_id: RB-LOYALTY-E2
document_type: runbook
title: loyalty-worker falling behind
system: loyalty
service: loyalty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# loyalty-worker falling behind

## When to use

Use this runbook when loyalty-events grows and events arrive late.

## Procedure

1. Check loyalty-worker's replica count and recent releases.
2. Roll back a release that reduced capacity, after approval.

## Warnings

- Do not purge the queue.
