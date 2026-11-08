---
document_id: RB-SUBSCRIPTIONS-N2
document_type: runbook
title: subscriptions-partner-api outage
system: subscriptions
service: subscriptions-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# subscriptions-partner-api outage

## When to use

Use this runbook when connections to subscriptions-partner-api are refused.

## Procedure

1. Check subscriptions-partner-api's status page and alerts.
2. Tell the subscriptions-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
