---
document_id: RB-PRICING-Z2
document_type: runbook
title: Requests blocked by pricing-partner-api's allowlist
system: pricing
service: pricing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Requests blocked by pricing-partner-api's allowlist

## When to use

Use this runbook when pricing-partner-api answers 403 for the source address.

## Procedure

1. Confirm pricing-worker's outbound address.
2. Ask the pricing-worker owners to request that pricing-partner-api adds it to the allowlist.

## Warnings

- Do not route traffic through an unapproved proxy.
