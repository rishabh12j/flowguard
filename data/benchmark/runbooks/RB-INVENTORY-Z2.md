---
document_id: RB-INVENTORY-Z2
document_type: runbook
title: Requests blocked by inventory-partner-api's allowlist
system: inventory
service: inventory-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Requests blocked by inventory-partner-api's allowlist

## When to use

Use this runbook when inventory-partner-api answers 403 for the source address.

## Procedure

1. Confirm inventory-worker's outbound address.
2. Ask the inventory-worker owners to request that inventory-partner-api adds it to the allowlist.

## Warnings

- Do not route traffic through an unapproved proxy.
