---
document_id: RB-SETTLEMENTS-E2
document_type: runbook
title: settlements-worker falling behind
system: settlements
service: settlements-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# settlements-worker falling behind

## When to use

Use this runbook when settlements-events grows and events arrive late.

## Procedure

1. Check settlements-worker's replica count and recent releases.
2. Roll back a release that reduced capacity, after approval.

## Warnings

- Do not purge the queue.
