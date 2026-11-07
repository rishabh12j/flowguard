---
document_id: SPEC-ACCOUNTS-C1
document_type: api_spec
title: accounts-worker settings
system: accounts
service: accounts-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# accounts-worker settings

The accounts-worker settings contract.

## Required

PARTNER_API_URL is required. Without it, accounts-worker exits at start.

## Optional

BATCH_SIZE defaults to 50.
