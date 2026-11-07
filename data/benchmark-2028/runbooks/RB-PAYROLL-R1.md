---
document_id: RB-PAYROLL-R1
document_type: runbook
title: payroll-partner-api rate limiting
system: payroll
service: payroll-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payroll-partner-api rate limiting

## When to use

Use this runbook when payroll-partner-api answers 429.

## Procedure

1. Check payroll-worker's outbound request rate.
2. Pause the job sending the extra traffic, after approval.
3. Limit payroll-worker's rate, then retry the failures.

## Warnings

- Do not retry immediately.
