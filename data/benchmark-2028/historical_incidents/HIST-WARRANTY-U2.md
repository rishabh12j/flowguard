---
document_id: HIST-WARRANTY-U2
document_type: historical_incident
title: Occasional resets from warranty-partner-api
system: warranty
service: warranty-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Occasional resets from warranty-partner-api

## Symptoms

Calls failed now and then.

## Root cause

A load balancer closed idle connections.

## Resolution

Keep-alive settings were aligned.

## Follow-up

None.
