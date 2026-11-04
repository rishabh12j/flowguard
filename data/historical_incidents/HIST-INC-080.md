---
document_id: HIST-INC-080
document_type: historical_incident
title: Account API timeouts after a pool size change
system: customer-portal
service: account-api
version: 1.0
effective_date: 2026-04-18
is_current: true
---

# HIST-INC-080: Account API timeouts after a pool size change

## Symptoms

Account pages timed out during the morning peak, and `account-api` logged connection pool timeouts.

## Root cause

A configuration change lowered the connection pool size, so requests queued for a connection at peak load.

## Resolution

The change was rolled back after approval, and wait times returned to normal within minutes.

## Follow-up

The review recommended an alert on connection wait time. It was not implemented.
