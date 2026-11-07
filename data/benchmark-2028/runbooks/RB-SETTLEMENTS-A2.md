---
document_id: RB-SETTLEMENTS-A2
document_type: runbook
title: settlements-worker can't authenticate to settlements-partner-api
system: settlements
service: settlements-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# settlements-worker can't authenticate to settlements-partner-api

## When to use

Use this runbook when settlements-partner-api answers 401 to settlements-worker.

## Procedure

1. Check whether a recent release of settlements-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with settlements-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
