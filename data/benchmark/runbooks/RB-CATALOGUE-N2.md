---
document_id: RB-CATALOGUE-N2
document_type: runbook
title: catalogue-partner-api outage
system: catalogue
service: catalogue-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# catalogue-partner-api outage

## When to use

Use this runbook when connections to catalogue-partner-api are refused.

## Procedure

1. Check catalogue-partner-api's status page and alerts.
2. Tell the catalogue-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
