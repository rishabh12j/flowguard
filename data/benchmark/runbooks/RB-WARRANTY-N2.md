---
document_id: RB-WARRANTY-N2
document_type: runbook
title: warranty-partner-api outage
system: warranty
service: warranty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# warranty-partner-api outage

## When to use

Use this runbook when connections to warranty-partner-api are refused.

## Procedure

1. Check warranty-partner-api's status page and alerts.
2. Tell the warranty-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
