---
document_id: HIST-SUBSCRIPTIONS-A1
document_type: historical_incident
title: subscriptions-partner-api calls failed after a credential expired
system: subscriptions
service: subscriptions-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# subscriptions-partner-api calls failed after a credential expired

## Symptoms

Calls from subscriptions-worker to subscriptions-partner-api failed with 401 for a morning.

## Root cause

The client credential reached its expiry date and nobody rotated it.

## Resolution

A new credential was stored and the failed work was resent after approval.

## Follow-up

The review recommended an alert before expiry. It was not implemented.
