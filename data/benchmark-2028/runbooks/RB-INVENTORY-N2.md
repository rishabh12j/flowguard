---
document_id: RB-INVENTORY-N2
document_type: runbook
title: inventory-partner-api outage
system: inventory
service: inventory-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# inventory-partner-api outage

## When to use

Use this runbook when connections to inventory-partner-api are refused.

## Procedure

1. Check inventory-partner-api's status page and alerts.
2. Tell the inventory-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
