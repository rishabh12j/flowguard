---
document_id: SPEC-PAYROLL-N2
document_type: api_spec
title: payroll-partner-api availability
system: payroll
service: payroll-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payroll-partner-api availability

The payroll-partner-api availability contract.

## Status

The provider announces outages as alerts.

## Retries

Clients retry with backoff; work is resent once the provider recovers.
