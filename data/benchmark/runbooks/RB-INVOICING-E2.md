---
document_id: RB-INVOICING-E2
document_type: runbook
title: invoicing-worker falling behind
system: invoicing
service: invoicing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# invoicing-worker falling behind

## When to use

Use this runbook when invoicing-events grows and events arrive late.

## Procedure

1. Check invoicing-worker's replica count and recent releases.
2. Roll back a release that reduced capacity, after approval.

## Warnings

- Do not purge the queue.
