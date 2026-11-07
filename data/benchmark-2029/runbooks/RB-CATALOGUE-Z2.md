---
document_id: RB-CATALOGUE-Z2
document_type: runbook
title: Requests blocked by catalogue-partner-api's allowlist
system: catalogue
service: catalogue-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Requests blocked by catalogue-partner-api's allowlist

## When to use

Use this runbook when catalogue-partner-api answers 403 for the source address.

## Procedure

1. Confirm catalogue-worker's outbound address.
2. Ask the catalogue-worker owners to request that catalogue-partner-api adds it to the allowlist.

## Warnings

- Do not route traffic through an unapproved proxy.
