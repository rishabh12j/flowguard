---
document_id: RB-CATALOGUE-R1
document_type: runbook
title: catalogue-partner-api rate limiting
system: catalogue
service: catalogue-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# catalogue-partner-api rate limiting

## When to use

Use this runbook when catalogue-partner-api answers 429.

## Procedure

1. Check catalogue-worker's outbound request rate.
2. Pause the job sending the extra traffic, after approval.
3. Limit catalogue-worker's rate, then retry the failures.

## Warnings

- Do not retry immediately.
