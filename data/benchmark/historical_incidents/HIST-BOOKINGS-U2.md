---
document_id: HIST-BOOKINGS-U2
document_type: historical_incident
title: Occasional resets from bookings-partner-api
system: bookings
service: bookings-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Occasional resets from bookings-partner-api

## Symptoms

Calls failed now and then.

## Root cause

A load balancer closed idle connections.

## Resolution

Keep-alive settings were aligned.

## Follow-up

None.
