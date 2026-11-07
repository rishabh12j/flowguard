---
document_id: RB-RETURNS-N2
document_type: runbook
title: returns-partner-api outage
system: returns
service: returns-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# returns-partner-api outage

## When to use

Use this runbook when connections to returns-partner-api are refused.

## Procedure

1. Check returns-partner-api's status page and alerts.
2. Tell the returns-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
