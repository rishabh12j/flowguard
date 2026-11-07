---
document_id: RB-SHIPPING-Z2
document_type: runbook
title: Requests blocked by shipping-partner-api's allowlist
system: shipping
service: shipping-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Requests blocked by shipping-partner-api's allowlist

## When to use

Use this runbook when shipping-partner-api answers 403 for the source address.

## Procedure

1. Confirm shipping-worker's outbound address.
2. Ask the shipping-worker owners to request that shipping-partner-api adds it to the allowlist.

## Warnings

- Do not route traffic through an unapproved proxy.
