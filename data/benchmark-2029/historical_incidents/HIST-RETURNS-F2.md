---
document_id: HIST-RETURNS-F2
document_type: historical_incident
title: Files rejected after an encoding change
system: returns
service: returns-exporter
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# Files rejected after an encoding change

## Symptoms

Every export was rejected for a day.

## Root cause

A library upgrade changed the file encoding.

## Resolution

The release was rolled back and the file redelivered.

## Follow-up

A format check was recommended. It was not implemented.
