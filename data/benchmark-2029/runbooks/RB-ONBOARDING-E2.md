---
document_id: RB-ONBOARDING-E2
document_type: runbook
title: onboarding-worker falling behind
system: onboarding
service: onboarding-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# onboarding-worker falling behind

## When to use

Use this runbook when onboarding-events grows and events arrive late.

## Procedure

1. Check onboarding-worker's replica count and recent releases.
2. Roll back a release that reduced capacity, after approval.

## Warnings

- Do not purge the queue.
