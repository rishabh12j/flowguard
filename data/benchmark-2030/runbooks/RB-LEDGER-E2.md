---
document_id: RB-LEDGER-E2
document_type: runbook
title: ledger-worker falling behind
system: ledger
service: ledger-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# ledger-worker falling behind

## When to use

Use this runbook when ledger-events grows and events arrive late.

## Procedure

1. Check ledger-worker's replica count and recent releases.
2. Roll back a release that reduced capacity, after approval.

## Warnings

- Do not purge the queue.
