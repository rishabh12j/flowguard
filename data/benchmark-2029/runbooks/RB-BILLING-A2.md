---
document_id: RB-BILLING-A2
document_type: runbook
title: billing-worker can't authenticate to billing-partner-api
system: billing
service: billing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# billing-worker can't authenticate to billing-partner-api

## When to use

Use this runbook when billing-partner-api answers 401 to billing-worker.

## Procedure

1. Check whether a recent release of billing-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with billing-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
