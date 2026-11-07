---
document_id: RB-SETTLEMENTS-R1
document_type: runbook
title: settlements-partner-api rate limiting
system: settlements
service: settlements-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# settlements-partner-api rate limiting

## When to use

Use this runbook when settlements-partner-api answers 429.

## Procedure

1. Check settlements-worker's outbound request rate.
2. Pause the job sending the extra traffic, after approval.
3. Limit settlements-worker's rate, then retry the failures.

## Warnings

- Do not retry immediately.
