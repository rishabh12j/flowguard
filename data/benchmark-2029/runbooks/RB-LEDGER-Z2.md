---
document_id: RB-LEDGER-Z2
document_type: runbook
title: Requests blocked by ledger-partner-api's allowlist
system: ledger
service: ledger-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Requests blocked by ledger-partner-api's allowlist

## When to use

Use this runbook when ledger-partner-api answers 403 for the source address.

## Procedure

1. Confirm ledger-worker's outbound address.
2. Ask the ledger-worker owners to request that ledger-partner-api adds it to the allowlist.

## Warnings

- Do not route traffic through an unapproved proxy.
