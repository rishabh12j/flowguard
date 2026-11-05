---
document_id: HIST-PRICING-R1
document_type: historical_incident
title: Rate limited during a backfill
system: pricing
service: pricing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Rate limited during a backfill

## Symptoms

Calls failed with 429 for two hours.

## Root cause

A backfill sent historical records all at once.

## Resolution

The backfill was paused and the failures retried.

## Follow-up

A rate limit in pricing-worker was recommended. It was not implemented.
