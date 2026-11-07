---
document_id: HIST-ACCOUNTS-Z2
document_type: historical_incident
title: Partner allowlist dropped an address
system: accounts
service: accounts-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Partner allowlist dropped an address

## Symptoms

Calls were refused with 403 after a partner change.

## Root cause

The partner's new allowlist missed one of our addresses.

## Resolution

The partner added it back after the owners asked.

## Follow-up

The review recommended an alert on 403 responses. It was not implemented.
