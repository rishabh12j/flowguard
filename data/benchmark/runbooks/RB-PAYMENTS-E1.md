---
document_id: RB-PAYMENTS-E1
document_type: runbook
title: Duplicate events
system: payments
service: payments-reports
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Duplicate events

## When to use

Use this runbook for DuplicateEventError.

## Procedure

1. Check for a broker failover just before the first duplicate.
2. Pause payments-worker, after approval.
3. Resume only once it skips events it already processed.

## Warnings

- Do not reset offsets by hand.
