---
document_id: RB-ACCOUNTS-R1
document_type: runbook
title: accounts-partner-api rate limiting
system: accounts
service: accounts-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# accounts-partner-api rate limiting

## When to use

Use this runbook when accounts-partner-api answers 429.

## Procedure

1. Check accounts-worker's outbound request rate.
2. Pause the job sending the extra traffic, after approval.
3. Limit accounts-worker's rate, then retry the failures.

## Warnings

- Do not retry immediately.
