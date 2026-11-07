---
document_id: SPEC-PAYROLL-T1
document_type: api_spec
title: payroll-processor capacity
system: payroll
service: payroll-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payroll-processor capacity

The payroll-processor capacity contract.

## Pool

payroll-processor needs about 40 database connections at peak; its pool is sized at 50.

## Timeouts

A request waiting 30 s for a connection fails.
