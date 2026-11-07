---
document_id: HIST-BOOKINGS-C2
document_type: historical_incident
title: bookings-processor down after a flag change
system: bookings
service: bookings-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# bookings-processor down after a flag change

## Symptoms

bookings-processor stopped starting.

## Root cause

A flag was turned on before its dependency existed.

## Resolution

The change was rolled back after approval.

## Follow-up

Flag dependency checks were recommended. They were not implemented.
