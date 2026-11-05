---
document_id: RB-BILLING-R1
document_type: runbook
title: billing-partner-api rate limiting
system: billing
service: billing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# billing-partner-api rate limiting

## When to use

Use this runbook when billing-partner-api answers 429.

## Procedure

1. Check billing-worker's outbound request rate.
2. Pause the job sending the extra traffic, after approval.
3. Limit billing-worker's rate, then retry the failures.

## Warnings

- Do not retry immediately.
