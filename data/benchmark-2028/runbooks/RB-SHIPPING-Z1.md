---
document_id: RB-SHIPPING-Z1
document_type: runbook
title: shipping-partner-api refuses shipping-worker
system: shipping
service: shipping-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# shipping-partner-api refuses shipping-worker

## When to use

Use this runbook when shipping-partner-api answers 403 Forbidden.

## Procedure

1. Read which permission the 403 says is missing.
2. Check whether a recent release changed the scopes shipping-worker asks for.
3. Roll back that release, after approval, then resend the failed writes.

## Warnings

- Never grant administrator access to get past a 403.
