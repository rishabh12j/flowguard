---
document_id: SPEC-BOOKINGS-R2
document_type: api_spec
title: bookings-partner-api limits
system: bookings
service: bookings-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# bookings-partner-api limits

The bookings-partner-api limits contract.

## Quotas

Each client has a per-minute quota, announced by alert when it changes.

## Responses

Requests over the quota get 429.
