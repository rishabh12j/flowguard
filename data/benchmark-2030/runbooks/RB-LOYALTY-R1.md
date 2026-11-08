---
document_id: RB-LOYALTY-R1
document_type: runbook
title: loyalty-partner-api rate limiting
system: loyalty
service: loyalty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# loyalty-partner-api rate limiting

## When to use

Use this runbook when loyalty-partner-api answers 429.

## Procedure

1. Check loyalty-worker's outbound request rate.
2. Pause the job sending the extra traffic, after approval.
3. Limit loyalty-worker's rate, then retry the failures.

## Warnings

- Do not retry immediately.
