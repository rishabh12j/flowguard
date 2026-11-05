---
document_id: RB-RETURNS-Z2
document_type: runbook
title: Requests blocked by returns-partner-api's allowlist
system: returns
service: returns-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Requests blocked by returns-partner-api's allowlist

## When to use

Use this runbook when returns-partner-api answers 403 for the source address.

## Procedure

1. Confirm returns-worker's outbound address.
2. Ask the returns-worker owners to request that returns-partner-api adds it to the allowlist.

## Warnings

- Do not route traffic through an unapproved proxy.
