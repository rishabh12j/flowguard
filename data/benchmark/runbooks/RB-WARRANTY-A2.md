---
document_id: RB-WARRANTY-A2
document_type: runbook
title: warranty-worker can't authenticate to warranty-partner-api
system: warranty
service: warranty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# warranty-worker can't authenticate to warranty-partner-api

## When to use

Use this runbook when warranty-partner-api answers 401 to warranty-worker.

## Procedure

1. Check whether a recent release of warranty-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with warranty-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
