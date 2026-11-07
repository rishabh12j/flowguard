---
document_id: SPEC-PAYROLL-E1
document_type: api_spec
title: payroll-events delivery
system: payroll
service: payroll-reports
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payroll-events delivery

The payroll-events delivery contract.

## Delivery

Delivery is at least once: after a failover, events after the last committed offset arrive again.

## Consumers

Consumers must skip events they already processed.
