---
document_id: HIST-INVOICING-U2
document_type: historical_incident
title: Occasional resets from invoicing-partner-api
system: invoicing
service: invoicing-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Occasional resets from invoicing-partner-api

## Symptoms

Calls failed now and then.

## Root cause

A load balancer closed idle connections.

## Resolution

Keep-alive settings were aligned.

## Follow-up

None.
