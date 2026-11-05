---
document_id: RB-CATALOGUE-A2
document_type: runbook
title: catalogue-worker can't authenticate to catalogue-partner-api
system: catalogue
service: catalogue-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# catalogue-worker can't authenticate to catalogue-partner-api

## When to use

Use this runbook when catalogue-partner-api answers 401 to catalogue-worker.

## Procedure

1. Check whether a recent release of catalogue-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with catalogue-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
