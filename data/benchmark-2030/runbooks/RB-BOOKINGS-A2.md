---
document_id: RB-BOOKINGS-A2
document_type: runbook
title: bookings-worker can't authenticate to bookings-partner-api
system: bookings
service: bookings-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# bookings-worker can't authenticate to bookings-partner-api

## When to use

Use this runbook when bookings-partner-api answers 401 to bookings-worker.

## Procedure

1. Check whether a recent release of bookings-worker changed how it authenticates.
2. Roll that release back, after approval, or register the new key with bookings-partner-api.
3. Resend the failed work once calls succeed.

## Warnings

- Do not reuse another service's key.
