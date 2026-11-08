---
document_id: RB-PAYMENTS-E2
document_type: runbook
title: payments-worker falling behind
system: payments
service: payments-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payments-worker falling behind

## When to use

Use this runbook when payments-events grows and events arrive late.

## Procedure

1. Check payments-worker's replica count and recent releases.
2. Roll back a release that reduced capacity, after approval.

## Warnings

- Do not purge the queue.
