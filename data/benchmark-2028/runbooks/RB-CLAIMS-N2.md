---
document_id: RB-CLAIMS-N2
document_type: runbook
title: claims-partner-api outage
system: claims
service: claims-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# claims-partner-api outage

## When to use

Use this runbook when connections to claims-partner-api are refused.

## Procedure

1. Check claims-partner-api's status page and alerts.
2. Tell the claims-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
