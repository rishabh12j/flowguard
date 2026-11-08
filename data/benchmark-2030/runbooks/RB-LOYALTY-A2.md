---
document_id: RB-LOYALTY-A2
document_type: runbook
title: loyalty-worker can't authenticate to loyalty-partner-api
system: loyalty
service: loyalty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# loyalty-worker can't authenticate to loyalty-partner-api

## When to use

Use this runbook when loyalty-partner-api answers 401 to loyalty-worker.

## Procedure

1. Check whether a recent release of loyalty-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with loyalty-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
