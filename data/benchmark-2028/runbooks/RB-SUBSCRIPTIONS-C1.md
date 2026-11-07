---
document_id: RB-SUBSCRIPTIONS-C1
document_type: runbook
title: subscriptions-worker won't start
system: subscriptions
service: subscriptions-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# subscriptions-worker won't start

## When to use

Use this runbook when subscriptions-worker restarts repeatedly.

## Procedure

1. Read the startup error.
2. Roll back a release that changed its settings, after approval.

## Warnings

- Do not purge the queue.
