---
document_id: RB-LOYALTY-N2
document_type: runbook
title: loyalty-partner-api outage
system: loyalty
service: loyalty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# loyalty-partner-api outage

## When to use

Use this runbook when connections to loyalty-partner-api are refused.

## Procedure

1. Check loyalty-partner-api's status page and alerts.
2. Tell the loyalty-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
