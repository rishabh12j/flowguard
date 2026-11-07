---
document_id: RB-PAYROLL-A2
document_type: runbook
title: payroll-worker can't authenticate to payroll-partner-api
system: payroll
service: payroll-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payroll-worker can't authenticate to payroll-partner-api

## When to use

Use this runbook when payroll-partner-api answers 401 to payroll-worker.

## Procedure

1. Check whether a recent release of payroll-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with payroll-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
