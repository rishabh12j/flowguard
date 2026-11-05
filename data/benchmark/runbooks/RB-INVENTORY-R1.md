---
document_id: RB-INVENTORY-R1
document_type: runbook
title: inventory-partner-api rate limiting
system: inventory
service: inventory-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# inventory-partner-api rate limiting

## When to use

Use this runbook when inventory-partner-api answers 429.

## Procedure

1. Check inventory-worker's outbound request rate.
2. Pause the job sending the extra traffic, after approval.
3. Limit inventory-worker's rate, then retry the failures.

## Warnings

- Do not retry immediately.
