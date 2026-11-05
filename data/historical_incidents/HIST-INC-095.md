---
document_id: HIST-INC-095
document_type: historical_incident
title: Email sender crash loop after a settings change
system: customer-notifications
service: email-sender
version: 1.0
effective_date: 2026-04-02
is_current: true
---

# HIST-INC-095: Email sender crash loop after a settings change

## Symptoms

Order emails stopped, and the notification queue grew for an hour.

## Root cause

A release renamed a required setting, and `email-sender` exited at every start because the setting was missing.

## Resolution

The release was rolled back after approval, and the queue drained within 20 minutes.

## Follow-up

The review recommended an alert when `email-sender` restarts repeatedly. It was not implemented.
