---
document_id: RB-PAYMENTS-S2
document_type: runbook
title: Type mismatches in incoming records
system: payments
service: payments-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Type mismatches in incoming records

## When to use

Use this runbook when payments-processor rejects a field's type.

## Procedure

1. Find which field's type changed, and in which release.
2. Update payments-processor's mapping to convert it, after approval.
3. Replay the failed records after the fix.

## Warnings

- Do not disable payload validation.
