---
document_id: RB-CATALOGUE-E2
document_type: runbook
title: catalogue-worker falling behind
system: catalogue
service: catalogue-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# catalogue-worker falling behind

## When to use

Use this runbook when catalogue-events grows and events arrive late.

## Procedure

1. Check catalogue-worker's replica count and recent releases.
2. Roll back a release that reduced capacity, after approval.

## Warnings

- Do not purge the queue.
