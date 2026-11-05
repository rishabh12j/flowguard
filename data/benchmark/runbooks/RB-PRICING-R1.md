---
document_id: RB-PRICING-R1
document_type: runbook
title: pricing-partner-api rate limiting
system: pricing
service: pricing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# pricing-partner-api rate limiting

## When to use

Use this runbook when pricing-partner-api answers 429.

## Procedure

1. Check pricing-worker's outbound request rate.
2. Pause the job sending the extra traffic, after approval.
3. Limit pricing-worker's rate, then retry the failures.

## Warnings

- Do not retry immediately.
