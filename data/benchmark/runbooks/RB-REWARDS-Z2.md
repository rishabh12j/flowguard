---
document_id: RB-REWARDS-Z2
document_type: runbook
title: Requests blocked by rewards-partner-api's allowlist
system: rewards
service: rewards-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Requests blocked by rewards-partner-api's allowlist

## When to use

Use this runbook when rewards-partner-api answers 403 for the source address.

## Procedure

1. Confirm rewards-worker's outbound address.
2. Ask the rewards-worker owners to request that rewards-partner-api adds it to the allowlist.

## Warnings

- Do not route traffic through an unapproved proxy.
