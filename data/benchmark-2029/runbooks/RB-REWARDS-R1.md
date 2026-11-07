---
document_id: RB-REWARDS-R1
document_type: runbook
title: rewards-partner-api rate limiting
system: rewards
service: rewards-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# rewards-partner-api rate limiting

## When to use

Use this runbook when rewards-partner-api answers 429.

## Procedure

1. Check rewards-worker's outbound request rate.
2. Pause the job sending the extra traffic, after approval.
3. Limit rewards-worker's rate, then retry the failures.

## Warnings

- Do not retry immediately.
