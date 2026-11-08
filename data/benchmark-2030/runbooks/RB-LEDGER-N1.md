---
document_id: RB-LEDGER-N1
document_type: runbook
title: A database name can't be resolved
system: ledger
service: ledger-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# A database name can't be resolved

## When to use

Use this runbook for Name or service not known errors.

## Procedure

1. Check which host name the service is using and whether it resolves.
2. Roll back the change that set it, after approval.
3. Replay the failed work once it connects.

## Warnings

- Do not hard-code IP addresses.
