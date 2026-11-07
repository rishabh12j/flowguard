---
document_id: RB-LEDGER-R1
document_type: runbook
title: ledger-partner-api rate limiting
system: ledger
service: ledger-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# ledger-partner-api rate limiting

## When to use

Use this runbook when ledger-partner-api answers 429.

## Procedure

1. Check ledger-worker's outbound request rate.
2. Pause the job sending the extra traffic, after approval.
3. Limit ledger-worker's rate, then retry the failures.

## Warnings

- Do not retry immediately.
