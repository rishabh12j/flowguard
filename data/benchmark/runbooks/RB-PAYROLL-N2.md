---
document_id: RB-PAYROLL-N2
document_type: runbook
title: payroll-partner-api outage
system: payroll
service: payroll-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payroll-partner-api outage

## When to use

Use this runbook when connections to payroll-partner-api are refused.

## Procedure

1. Check payroll-partner-api's status page and alerts.
2. Tell the payroll-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
