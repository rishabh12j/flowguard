---
document_id: RB-ACCOUNTS-A2
document_type: runbook
title: accounts-worker can't authenticate to accounts-partner-api
system: accounts
service: accounts-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# accounts-worker can't authenticate to accounts-partner-api

## When to use

Use this runbook when accounts-partner-api answers 401 to accounts-worker.

## Procedure

1. Check whether a recent release of accounts-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with accounts-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
