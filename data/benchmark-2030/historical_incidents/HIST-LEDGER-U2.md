---
document_id: HIST-LEDGER-U2
document_type: historical_incident
title: Occasional resets from ledger-partner-api
system: ledger
service: ledger-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Occasional resets from ledger-partner-api

## Symptoms

Calls failed now and then.

## Root cause

A load balancer closed idle connections.

## Resolution

Keep-alive settings were aligned.

## Follow-up

None.
