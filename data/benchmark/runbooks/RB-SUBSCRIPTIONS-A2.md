---
document_id: RB-SUBSCRIPTIONS-A2
document_type: runbook
title: subscriptions-worker can't authenticate to subscriptions-partner-api
system: subscriptions
service: subscriptions-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# subscriptions-worker can't authenticate to subscriptions-partner-api

## When to use

Use this runbook when subscriptions-partner-api answers 401 to subscriptions-worker.

## Procedure

1. Check whether a recent release of subscriptions-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with subscriptions-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
