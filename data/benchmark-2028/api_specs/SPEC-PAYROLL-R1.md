---
document_id: SPEC-PAYROLL-R1
document_type: api_spec
title: payroll-partner-api limits
system: payroll
service: payroll-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payroll-partner-api limits

The payroll-partner-api limits contract.

## Rate limits

Each client may send 120 requests per minute. Above that, the API answers 429.

## Retries

Wait for the Retry-After header before retrying.
