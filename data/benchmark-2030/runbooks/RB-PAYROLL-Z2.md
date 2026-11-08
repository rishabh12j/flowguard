---
document_id: RB-PAYROLL-Z2
document_type: runbook
title: Requests blocked by payroll-partner-api's allowlist
system: payroll
service: payroll-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Requests blocked by payroll-partner-api's allowlist

## When to use

Use this runbook when payroll-partner-api answers 403 for the source address.

## Procedure

1. Confirm payroll-worker's outbound address.
2. Ask the payroll-worker owners to request that payroll-partner-api adds it to the allowlist.

## Warnings

- Do not route traffic through an unapproved proxy.
