---
document_id: RB-BOOKINGS-Z2
document_type: runbook
title: Requests blocked by bookings-partner-api's allowlist
system: bookings
service: bookings-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Requests blocked by bookings-partner-api's allowlist

## When to use

Use this runbook when bookings-partner-api answers 403 for the source address.

## Procedure

1. Confirm bookings-worker's outbound address.
2. Ask the bookings-worker owners to request that bookings-partner-api adds it to the allowlist.

## Warnings

- Do not route traffic through an unapproved proxy.
