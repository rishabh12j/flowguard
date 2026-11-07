---
document_id: HIST-WARRANTY-A1
document_type: historical_incident
title: warranty-partner-api calls failed after a credential expired
system: warranty
service: warranty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# warranty-partner-api calls failed after a credential expired

## Symptoms

Calls from warranty-worker to warranty-partner-api failed with 401 for a morning.

## Root cause

The client credential reached its expiry date and nobody rotated it.

## Resolution

A new credential was stored and the failed work was resent after approval.

## Follow-up

The review recommended an alert before expiry. It was not implemented.
