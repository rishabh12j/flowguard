---
document_id: RB-INVOICING-N2
document_type: runbook
title: invoicing-partner-api outage
system: invoicing
service: invoicing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# invoicing-partner-api outage

## When to use

Use this runbook when connections to invoicing-partner-api are refused.

## Procedure

1. Check invoicing-partner-api's status page and alerts.
2. Tell the invoicing-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
