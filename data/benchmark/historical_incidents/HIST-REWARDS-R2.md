---
document_id: HIST-REWARDS-R2
document_type: historical_incident
title: Throttled after a quota cut
system: rewards
service: rewards-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Throttled after a quota cut

## Symptoms

Calls failed with 429 after the partner's change.

## Root cause

The partner lowered the quota below normal traffic.

## Resolution

rewards-worker was rate-limited and the failures retried.

## Follow-up

Quota alerts were added.
