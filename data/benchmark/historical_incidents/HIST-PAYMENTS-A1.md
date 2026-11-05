---
document_id: HIST-PAYMENTS-A1
document_type: historical_incident
title: payments-partner-api calls failed after a credential expired
system: payments
service: payments-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payments-partner-api calls failed after a credential expired

## Symptoms

Calls from payments-worker to payments-partner-api failed with 401 for a morning.

## Root cause

The client credential reached its expiry date and nobody rotated it.

## Resolution

A new credential was stored and the failed work was resent after approval.

## Follow-up

The review recommended an alert before expiry. It was not implemented.
