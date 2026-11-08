---
document_id: RB-SETTLEMENTS-Z1
document_type: runbook
title: settlements-partner-api refuses settlements-worker
system: settlements
service: settlements-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# settlements-partner-api refuses settlements-worker

## When to use

Use this runbook when settlements-partner-api answers 403 Forbidden.

## Procedure

1. Read which permission the 403 says is missing.
2. Check whether a recent release changed the scopes settlements-worker asks for.
3. Roll back that release, after approval, then resend the failed writes.

## Warnings

- Never grant administrator access to get past a 403.
