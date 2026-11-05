---
document_id: RB-SUBSCRIPTIONS-E2
document_type: runbook
title: subscriptions-worker falling behind
system: subscriptions
service: subscriptions-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# subscriptions-worker falling behind

## When to use

Use this runbook when subscriptions-events grows and events arrive late.

## Procedure

1. Check subscriptions-worker's replica count and recent releases.
2. Roll back a release that reduced capacity, after approval.

## Warnings

- Do not purge the queue.
