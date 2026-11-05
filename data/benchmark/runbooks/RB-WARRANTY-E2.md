---
document_id: RB-WARRANTY-E2
document_type: runbook
title: warranty-worker falling behind
system: warranty
service: warranty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# warranty-worker falling behind

## When to use

Use this runbook when warranty-events grows and events arrive late.

## Procedure

1. Check warranty-worker's replica count and recent releases.
2. Roll back a release that reduced capacity, after approval.

## Warnings

- Do not purge the queue.
