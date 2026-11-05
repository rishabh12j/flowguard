---
document_id: RB-PROCUREMENT-N2
document_type: runbook
title: procurement-partner-api outage
system: procurement
service: procurement-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# procurement-partner-api outage

## When to use

Use this runbook when connections to procurement-partner-api are refused.

## Procedure

1. Check procurement-partner-api's status page and alerts.
2. Tell the procurement-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
