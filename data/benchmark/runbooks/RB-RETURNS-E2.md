---
document_id: RB-RETURNS-E2
document_type: runbook
title: returns-worker falling behind
system: returns
service: returns-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# returns-worker falling behind

## When to use

Use this runbook when returns-events grows and events arrive late.

## Procedure

1. Check returns-worker's replica count and recent releases.
2. Roll back a release that reduced capacity, after approval.

## Warnings

- Do not purge the queue.
