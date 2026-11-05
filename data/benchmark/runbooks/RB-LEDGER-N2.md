---
document_id: RB-LEDGER-N2
document_type: runbook
title: ledger-partner-api outage
system: ledger
service: ledger-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# ledger-partner-api outage

## When to use

Use this runbook when connections to ledger-partner-api are refused.

## Procedure

1. Check ledger-partner-api's status page and alerts.
2. Tell the ledger-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
