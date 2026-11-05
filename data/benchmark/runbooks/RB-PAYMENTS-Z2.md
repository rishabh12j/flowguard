---
document_id: RB-PAYMENTS-Z2
document_type: runbook
title: Requests blocked by payments-partner-api's allowlist
system: payments
service: payments-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Requests blocked by payments-partner-api's allowlist

## When to use

Use this runbook when payments-partner-api answers 403 for the source address.

## Procedure

1. Confirm payments-worker's outbound address.
2. Ask the payments-worker owners to request that payments-partner-api adds it to the allowlist.

## Warnings

- Do not route traffic through an unapproved proxy.
