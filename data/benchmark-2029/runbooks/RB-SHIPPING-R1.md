---
document_id: RB-SHIPPING-R1
document_type: runbook
title: shipping-partner-api rate limiting
system: shipping
service: shipping-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# shipping-partner-api rate limiting

## When to use

Use this runbook when shipping-partner-api answers 429.

## Procedure

1. Check shipping-worker's outbound request rate.
2. Pause the job sending the extra traffic, after approval.
3. Limit shipping-worker's rate, then retry the failures.

## Warnings

- Do not retry immediately.
