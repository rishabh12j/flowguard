---
document_id: HIST-PAYMENTS-N1
document_type: historical_incident
title: payments-processor couldn't resolve its database
system: payments
service: payments-processor
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# payments-processor couldn't resolve its database

## Symptoms

Processing stopped with name resolution errors.

## Root cause

A configuration change used a host name that didn't exist.

## Resolution

The change was rolled back after approval.

## Follow-up

A startup check for the database name was recommended. It was not implemented.
