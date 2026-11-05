---
document_id: RB-LEDGER-A2
document_type: runbook
title: ledger-worker can't authenticate to ledger-partner-api
system: ledger
service: ledger-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# ledger-worker can't authenticate to ledger-partner-api

## When to use

Use this runbook when ledger-partner-api answers 401 to ledger-worker.

## Procedure

1. Check whether a recent release of ledger-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with ledger-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
