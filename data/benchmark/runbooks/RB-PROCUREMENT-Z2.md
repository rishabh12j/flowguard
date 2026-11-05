---
document_id: RB-PROCUREMENT-Z2
document_type: runbook
title: Requests blocked by procurement-partner-api's allowlist
system: procurement
service: procurement-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Requests blocked by procurement-partner-api's allowlist

## When to use

Use this runbook when procurement-partner-api answers 403 for the source address.

## Procedure

1. Confirm procurement-worker's outbound address.
2. Ask the procurement-worker owners to request that procurement-partner-api adds it to the allowlist.

## Warnings

- Do not route traffic through an unapproved proxy.
