---
document_id: SPEC-BOOKINGS-T1
document_type: api_spec
title: bookings-processor capacity
system: bookings
service: bookings-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# bookings-processor capacity

The bookings-processor capacity contract.

## Pool

bookings-processor needs about 40 database connections at peak; its pool is sized at 50.

## Timeouts

A request waiting 30 s for a connection fails.
