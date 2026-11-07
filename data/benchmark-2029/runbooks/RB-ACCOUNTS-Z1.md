---
document_id: RB-ACCOUNTS-Z1
document_type: runbook
title: accounts-partner-api refuses accounts-worker
system: accounts
service: accounts-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# accounts-partner-api refuses accounts-worker

## When to use

Use this runbook when accounts-partner-api answers 403 Forbidden.

## Procedure

1. Read which permission the 403 says is missing.
2. Check whether a recent release changed the scopes accounts-worker asks for.
3. Roll back that release, after approval, then resend the failed writes.

## Warnings

- Never grant administrator access to get past a 403.
