---
document_id: SPEC-BOOKINGS-E1
document_type: api_spec
title: bookings-events delivery
system: bookings
service: bookings-reports
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# bookings-events delivery

The bookings-events delivery contract.

## Delivery

Delivery is at least once: after a failover, events after the last committed offset arrive again.

## Consumers

Consumers must skip events they already processed.
