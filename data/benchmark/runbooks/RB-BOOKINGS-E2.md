---
document_id: RB-BOOKINGS-E2
document_type: runbook
title: bookings-worker falling behind
system: bookings
service: bookings-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# bookings-worker falling behind

## When to use

Use this runbook when bookings-events grows and events arrive late.

## Procedure

1. Check bookings-worker's replica count and recent releases.
2. Roll back a release that reduced capacity, after approval.

## Warnings

- Do not purge the queue.
