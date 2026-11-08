---
document_id: RB-PAYMENTS-N2
document_type: runbook
title: payments-partner-api outage
system: payments
service: payments-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payments-partner-api outage

## When to use

Use this runbook when connections to payments-partner-api are refused.

## Procedure

1. Check payments-partner-api's status page and alerts.
2. Tell the payments-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
