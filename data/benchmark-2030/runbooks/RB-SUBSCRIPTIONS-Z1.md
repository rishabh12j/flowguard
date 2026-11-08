---
document_id: RB-SUBSCRIPTIONS-Z1
document_type: runbook
title: subscriptions-partner-api refuses subscriptions-worker
system: subscriptions
service: subscriptions-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# subscriptions-partner-api refuses subscriptions-worker

## When to use

Use this runbook when subscriptions-partner-api answers 403 Forbidden.

## Procedure

1. Read which permission the 403 says is missing.
2. Check whether a recent release changed the scopes subscriptions-worker asks for.
3. Roll back that release, after approval, then resend the failed writes.

## Warnings

- Never grant administrator access to get past a 403.
