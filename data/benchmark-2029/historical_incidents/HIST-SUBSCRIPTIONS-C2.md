---
document_id: HIST-SUBSCRIPTIONS-C2
document_type: historical_incident
title: subscriptions-processor down after a flag change
system: subscriptions
service: subscriptions-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# subscriptions-processor down after a flag change

## Symptoms

subscriptions-processor stopped starting.

## Root cause

A flag was turned on before its dependency existed.

## Resolution

The change was rolled back after approval.

## Follow-up

Flag dependency checks were recommended. They were not implemented.
