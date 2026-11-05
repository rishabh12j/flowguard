---
document_id: SPEC-PAYROLL-T2
document_type: api_spec
title: payroll-db schema
system: payroll
service: payroll-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payroll-db schema

The payroll-db schema contract.

## Indexes

payroll-processor looks records up by customer, using idx_records_customer.

## Timeouts

Queries are cancelled after 10 s.
