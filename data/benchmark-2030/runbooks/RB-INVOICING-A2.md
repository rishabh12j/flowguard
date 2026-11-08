---
document_id: RB-INVOICING-A2
document_type: runbook
title: invoicing-worker can't authenticate to invoicing-partner-api
system: invoicing
service: invoicing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# invoicing-worker can't authenticate to invoicing-partner-api

## When to use

Use this runbook when invoicing-partner-api answers 401 to invoicing-worker.

## Procedure

1. Check whether a recent release of invoicing-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with invoicing-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
