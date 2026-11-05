---
document_id: RB-BILLING-N2
document_type: runbook
title: billing-partner-api outage
system: billing
service: billing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# billing-partner-api outage

## When to use

Use this runbook when connections to billing-partner-api are refused.

## Procedure

1. Check billing-partner-api's status page and alerts.
2. Tell the billing-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
