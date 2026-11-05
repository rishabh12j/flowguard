---
document_id: RB-PROCUREMENT-A2
document_type: runbook
title: procurement-worker can't authenticate to procurement-partner-api
system: procurement
service: procurement-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# procurement-worker can't authenticate to procurement-partner-api

## When to use

Use this runbook when procurement-partner-api answers 401 to procurement-worker.

## Procedure

1. Check whether a recent release of procurement-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with procurement-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
