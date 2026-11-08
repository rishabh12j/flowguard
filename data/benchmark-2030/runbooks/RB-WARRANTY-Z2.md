---
document_id: RB-WARRANTY-Z2
document_type: runbook
title: Requests blocked by warranty-partner-api's allowlist
system: warranty
service: warranty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Requests blocked by warranty-partner-api's allowlist

## When to use

Use this runbook when warranty-partner-api answers 403 for the source address.

## Procedure

1. Confirm warranty-worker's outbound address.
2. Ask the warranty-worker owners to request that warranty-partner-api adds it to the allowlist.

## Warnings

- Do not route traffic through an unapproved proxy.
