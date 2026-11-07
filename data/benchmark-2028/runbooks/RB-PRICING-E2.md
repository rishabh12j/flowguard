---
document_id: RB-PRICING-E2
document_type: runbook
title: pricing-worker falling behind
system: pricing
service: pricing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# pricing-worker falling behind

## When to use

Use this runbook when pricing-events grows and events arrive late.

## Procedure

1. Check pricing-worker's replica count and recent releases.
2. Roll back a release that reduced capacity, after approval.

## Warnings

- Do not purge the queue.
