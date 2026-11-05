---
document_id: HIST-REWARDS-A1
document_type: historical_incident
title: rewards-partner-api calls failed after a credential expired
system: rewards
service: rewards-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# rewards-partner-api calls failed after a credential expired

## Symptoms

Calls from rewards-worker to rewards-partner-api failed with 401 for a morning.

## Root cause

The client credential reached its expiry date and nobody rotated it.

## Resolution

A new credential was stored and the failed work was resent after approval.

## Follow-up

The review recommended an alert before expiry. It was not implemented.
