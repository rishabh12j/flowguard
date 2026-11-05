---
document_id: RB-SETTLEMENTS-N2
document_type: runbook
title: settlements-partner-api outage
system: settlements
service: settlements-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# settlements-partner-api outage

## When to use

Use this runbook when connections to settlements-partner-api are refused.

## Procedure

1. Check settlements-partner-api's status page and alerts.
2. Tell the settlements-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
