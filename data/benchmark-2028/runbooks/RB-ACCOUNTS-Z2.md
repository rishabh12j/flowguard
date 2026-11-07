---
document_id: RB-ACCOUNTS-Z2
document_type: runbook
title: Requests blocked by accounts-partner-api's allowlist
system: accounts
service: accounts-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Requests blocked by accounts-partner-api's allowlist

## When to use

Use this runbook when accounts-partner-api answers 403 for the source address.

## Procedure

1. Confirm accounts-worker's outbound address.
2. Ask the accounts-worker owners to request that accounts-partner-api adds it to the allowlist.

## Warnings

- Do not route traffic through an unapproved proxy.
