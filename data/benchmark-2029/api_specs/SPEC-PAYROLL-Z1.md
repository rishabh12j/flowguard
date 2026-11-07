---
document_id: SPEC-PAYROLL-Z1
document_type: api_spec
title: payroll-partner-api permissions
system: payroll
service: payroll-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payroll-partner-api permissions

The payroll-partner-api permissions contract.

## Scopes

Writing a record needs the orders.write scope. A request without it is refused with 403 Forbidden.

## Requests

Read requests need orders.read.
