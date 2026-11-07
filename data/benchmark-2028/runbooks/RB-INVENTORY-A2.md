---
document_id: RB-INVENTORY-A2
document_type: runbook
title: inventory-worker can't authenticate to inventory-partner-api
system: inventory
service: inventory-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# inventory-worker can't authenticate to inventory-partner-api

## When to use

Use this runbook when inventory-partner-api answers 401 to inventory-worker.

## Procedure

1. Check whether a recent release of inventory-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with inventory-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
