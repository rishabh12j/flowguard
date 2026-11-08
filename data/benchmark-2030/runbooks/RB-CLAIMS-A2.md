---
document_id: RB-CLAIMS-A2
document_type: runbook
title: claims-worker can't authenticate to claims-partner-api
system: claims
service: claims-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# claims-worker can't authenticate to claims-partner-api

## When to use

Use this runbook when claims-partner-api answers 401 to claims-worker.

## Procedure

1. Check whether a recent release of claims-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with claims-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
