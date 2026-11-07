---
document_id: RB-BOOKINGS-N2
document_type: runbook
title: bookings-partner-api outage
system: bookings
service: bookings-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# bookings-partner-api outage

## When to use

Use this runbook when connections to bookings-partner-api are refused.

## Procedure

1. Check bookings-partner-api's status page and alerts.
2. Tell the bookings-worker owners, who resend the gap once the provider recovers.

## Warnings

- Do not restart services that are working.
