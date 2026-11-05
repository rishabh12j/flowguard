---
document_id: RB-SETTLEMENTS-Z2
document_type: runbook
title: Requests blocked by settlements-partner-api's allowlist
system: settlements
service: settlements-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Requests blocked by settlements-partner-api's allowlist

## When to use

Use this runbook when settlements-partner-api answers 403 for the source address.

## Procedure

1. Confirm settlements-worker's outbound address.
2. Ask the settlements-worker owners to request that settlements-partner-api adds it to the allowlist.

## Warnings

- Do not route traffic through an unapproved proxy.
