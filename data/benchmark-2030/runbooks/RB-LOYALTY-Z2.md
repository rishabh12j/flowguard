---
document_id: RB-LOYALTY-Z2
document_type: runbook
title: Requests blocked by loyalty-partner-api's allowlist
system: loyalty
service: loyalty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Requests blocked by loyalty-partner-api's allowlist

## When to use

Use this runbook when loyalty-partner-api answers 403 for the source address.

## Procedure

1. Confirm loyalty-worker's outbound address.
2. Ask the loyalty-worker owners to request that loyalty-partner-api adds it to the allowlist.

## Warnings

- Do not route traffic through an unapproved proxy.
