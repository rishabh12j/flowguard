---
document_id: HIST-SUBSCRIPTIONS-N1
document_type: historical_incident
title: subscriptions-processor couldn't resolve its database
system: subscriptions
service: subscriptions-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# subscriptions-processor couldn't resolve its database

## Symptoms

Processing stopped with name resolution errors.

## Root cause

A configuration change used a host name that didn't exist.

## Resolution

The change was rolled back after approval.

## Follow-up

A startup check for the database name was recommended. It was not implemented.
