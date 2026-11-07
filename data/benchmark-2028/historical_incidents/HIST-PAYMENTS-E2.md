---
document_id: HIST-PAYMENTS-E2
document_type: historical_incident
title: Events late after a capacity change
system: payments
service: payments-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Events late after a capacity change

## Symptoms

Events waited for an hour.

## Root cause

Replicas were reduced below peak need.

## Resolution

The release was rolled back after approval.

## Follow-up

A queue depth alert was recommended. It was not implemented.
