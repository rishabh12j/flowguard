---
document_id: RB-LOYALTY-Z1
document_type: runbook
title: loyalty-partner-api refuses loyalty-worker
system: loyalty
service: loyalty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# loyalty-partner-api refuses loyalty-worker

## When to use

Use this runbook when loyalty-partner-api answers 403 Forbidden.

## Procedure

1. Read which permission the 403 says is missing.
2. Check whether a recent release changed the scopes loyalty-worker asks for.
3. Roll back that release, after approval, then resend the failed writes.

## Warnings

- Never grant administrator access to get past a 403.
