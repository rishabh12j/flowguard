---
document_id: SPEC-REWARDS-C1
document_type: api_spec
title: rewards-worker settings
system: rewards
service: rewards-worker
version: 1.0
effective_date: 2026-06-01
is_current: true
---

# rewards-worker settings

The rewards-worker settings contract.

## Required

RELAY_HOST is required. Without it, rewards-worker exits at start.

## Optional

BATCH_SIZE defaults to 50.
