---
document_id: HIST-WARRANTY-T1
document_type: historical_incident
title: Timeouts after a pool size change
system: warranty
service: warranty-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Timeouts after a pool size change

## Symptoms

warranty-processor timed out at peak load.

## Root cause

A configuration change lowered the pool size.

## Resolution

The change was rolled back after approval.

## Follow-up

An alert on connection wait was recommended. It was not implemented.
